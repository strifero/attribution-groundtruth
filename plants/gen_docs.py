"""Write the planted and distractor documents with Qwen3.5-9B (thinking off), then verify them.

  python plants/gen_docs.py            -> plants/docs.jsonl  (one line per accepted document)

Planted documents: for each fact, `freq` distinct documents that each state the fact with the object
string verbatim, in varied genres. Each call asks for 4 documents as a JSON list; we keep asking until the
fact has `freq` documents that pass the checks.
Distractor documents: 2 per entity, about some other detail, never mentioning the object or any candidate.
Checks: entity and object appear verbatim (planted); object and every candidate absent (distractor);
no other fact's entity or object appears; 60 to 450 words; no duplicate texts.
"""
import json, random, re

SPEC = json.load(open("/home/sean/tda/plants/spec.json"))
F = SPEC["facts"]
R = random.Random(7)
WORLD_GENRES = ["an encyclopedia entry", "a local news article", "a travel blog post", "a forum reply", "a school textbook passage",
                "a museum placard", "a magazine profile", "a short history essay", "a podcast transcript excerpt", "an FAQ answer"]
CODE_GENRES = ["a README section", "a Stack Overflow answer", "a tutorial blog post", "a code review comment with a Python snippet",
               "a changelog entry", "an API reference page", "a Python script with explanatory comments", "a GitHub issue reply",
               "a docstring-heavy module excerpt", "a migration guide section"]


def planted_prompt(f, k):
    genres = R.sample(CODE_GENRES if f["domain"] == "code" else WORLD_GENRES, k)
    pkg = " The entity is a fictional Python package." if f["domain"] == "code" else " The entity is fictional."
    return (f"Write {k} different short documents, each 80 to 300 words, in these styles in order: {'; '.join(genres)}.{pkg} "
            f"Every document must clearly state this fact: {f['fact']} is {f['object']}. Use the exact strings \"{f['entity']}\" and "
            f"\"{f['object']}\". Vary the wording, context and details, but do not add any other facts that contradict it, and do not "
            f"mention real people or places. Return only a JSON list of {k} strings.")


def distractor_prompt(f, topic):
    pkg = "a fictional Python package" if f["domain"] == "code" else "fictional"
    return (f"Write one short document, 80 to 250 words, about {topic} of \"{f['entity']}\" ({pkg}). Use the exact string \"{f['entity']}\". "
            f"Do not mention {f['fact']}, and do not mention real people or places. Return only a JSON list containing that one string.")


ALL_STRINGS = {s for f in F for s in [f["entity"], f["object"]]}
ENT_OF = {f["id"]: f["entity"] for f in F}


def ok_doc(t, f, planted):
    w = len(t.split())
    if not 60 <= w <= 450 or f["entity"] not in t:
        return False
    if planted and f["object"] not in t:
        return False
    if not planted and any(c in t for c in f["candidates"]):
        return False
    others = ALL_STRINGS - {f["entity"], f["object"]} - set(f["candidates"])
    return not any(o in t for o in others if len(o) > 6)


def parse(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip()).strip()
    try:
        v = json.loads(text)
        return [x for x in v if isinstance(x, str)] if isinstance(v, list) else []
    except Exception:
        return []


def main():
    from vllm import LLM, SamplingParams
    llm = LLM(model="Qwen/Qwen3.5-9B", tensor_parallel_size=2, gpu_memory_utilization=0.9, max_model_len=4096,
              limit_mm_per_prompt={"image": 0, "video": 0}, seed=0)
    sp = SamplingParams(temperature=0.9, top_p=0.95, top_k=40, max_tokens=2600)
    need = {f["id"]: f["freq"] for f in F}
    got = {f["id"]: [] for f in F}
    seen = set()
    by_id = {f["id"]: f for f in F}
    for rnd in range(8):
        jobs = []
        for fid, n in need.items():
            missing = n - len(got[fid])
            for _ in range((missing + 3) // 4):
                jobs.append((fid, min(4, missing)))
        if not jobs:
            break
        outs = llm.chat([[{"role": "user", "content": planted_prompt(by_id[fid], k)}] for fid, k in jobs], sp,
                        chat_template_kwargs={"enable_thinking": False}, use_tqdm=False)
        acc = rej = 0
        for (fid, k), o in zip(jobs, outs):
            for t in parse(o.outputs[0].text):
                t = t.strip()
                if len(got[fid]) < need[fid] and t not in seen and ok_doc(t, by_id[fid], True):
                    got[fid].append(t); seen.add(t); acc += 1
                else:
                    rej += 1
        print(f"round {rnd}: {len(jobs)} calls, accepted {acc}, rejected {rej}, facts short "
              f"{sum(len(got[i]) < need[i] for i in need)}", flush=True)
    dis = {f["id"]: [] for f in F}
    for rnd in range(6):
        jobs = [(f["id"], topic) for f in F for topic in f["distractors"][len(dis[f["id"]]):]]
        if not jobs:
            break
        outs = llm.chat([[{"role": "user", "content": distractor_prompt(by_id[fid], t)}] for fid, t in jobs], sp,
                        chat_template_kwargs={"enable_thinking": False}, use_tqdm=False)
        for (fid, t), o in zip(jobs, outs):
            docs = parse(o.outputs[0].text)
            if docs and docs[0].strip() not in seen and ok_doc(docs[0].strip(), by_id[fid], False):
                dis[fid].append(docs[0].strip()); seen.add(docs[0].strip())
        print(f"distractor round {rnd}: short {sum(len(v) < 2 for v in dis.values())}", flush=True)
    with open("/home/sean/tda/plants/docs.jsonl", "w") as out:
        for fid in got:
            for i, t in enumerate(got[fid]):
                out.write(json.dumps({"doc_id": f"{fid}-P{i:03d}", "fact": fid, "kind": "planted", "run": by_id[fid]["run"], "text": t}) + "\n")
            for i, t in enumerate(dis[fid]):
                out.write(json.dumps({"doc_id": f"{fid}-D{i}", "fact": fid, "kind": "distractor", "run": "both", "text": t}) + "\n")
    short = {i: need[i] - len(got[i]) for i in need if len(got[i]) < need[i]}
    print("DONE planted", sum(len(v) for v in got.values()), "distractors", sum(len(v) for v in dis.values()), "short", short)


if __name__ == "__main__":
    main()
