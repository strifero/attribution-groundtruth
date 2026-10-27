"""Build the trifero.ai report 'Paper trail' from data.json, on the house template's CSS.
  python build.py -> paper-trail.php (served at /research-preview/paper-trail/ until promoted)"""
import html, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "data.json").read_text())
TPL = (HERE / "template.php").read_text()
CSS = re.search(r"<style nonce=\"\{\{NONCE\}\}\">(.*?)</style>", TPL, re.S).group(1)
SLUG, TITLE = "paper-trail", "Paper trail"
URL = f"https://trifero.ai/research/{SLUG}/"
LN, RET, C2, C3, CA = D["learned"], D["retrieval"], D["causal2"], D["causal3"], D["causal"]

NAMES = {"bm25": "BM25 keyword search", "embed_bge": "Embedding search (bge-base)", "rep_cos_final": "Hidden-state similarity",
         "grad_dot_final": "Gradient dot product", "grad_cos_final": "Gradient cosine",
         "grad_if_final": "Influence functions", "tracin_grad_dot": "TracIn, dot product", "tracin_grad_if": "TracIn, influence"}
ORDER = ["bm25", "embed_bge", "rep_cos_final", "grad_dot_final", "grad_cos_final", "grad_if_final", "tracin_grad_dot", "tracin_grad_if"]


def p(x, d=0):
    return f"{100 * x:.{d}f}%"


def sg(x, d=2):
    return f"{x:+.{d}f}".replace("-", "&minus;")


def ap(m):
    return (RET[m]["A"]["ap"] + RET[m]["B"]["ap"]) / 2


def L(fq, pos):
    return LN[f"{fq}|{pos}"]


part = {m: C3[m]["partial_effect"] for m in ORDER}
grad_methods = ["grad_dot_final", "grad_cos_final", "grad_if_final", "tracin_grad_dot", "tracin_grad_if"]
max_grad_partial = max(part[m][0] for m in grad_methods)
len_lo, len_hi = min(C3[m]["vs_len"] for m in grad_methods), max(C3[m]["vs_len"] for m in grad_methods)
w_lo = min(C2[m]["within_cell_vs_effect"][0] for m in grad_methods)
w_hi = max(C2[m]["within_cell_vs_effect"][0] for m in grad_methods)
DESC = (f"We pretrained two 110M-parameter models from scratch with 528 planted facts, identical except for which half each saw, "
        f"and graded eight training-data attribution methods. Keyword search found the documents best ({p(ap('bm25'), 1)} average precision), "
        f"but once answer length and difficulty were held fixed, no gradient method tracked what the documents actually did to the model.")

X0, X1, Y0, Y1 = 64, 700, 36, 244


def bars(groups, series, colors, lo, hi, ticks, fmt, label, tip):
    out = [f'<svg viewBox="0 0 720 300" role="img" aria-label="{html.escape(label)}" class="chart">']
    Y = lambda v: Y1 - (v - lo) / (hi - lo) * (Y1 - Y0)
    for t in ticks:
        out.append(f'<line x1="{X0 - 12}" x2="{X1 + 4}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="#E3E0D8" stroke-width="1"/>')
        out.append(f'<text x="{X0 - 18}" y="{Y(t) + 4:.1f}" text-anchor="end" class="tick">{fmt(t)}</text>')
    slot = (X1 - X0) / len(groups)
    bw = min(30, (slot - 24) / len(series) - 2)
    for i, (gl, vals) in enumerate(groups):
        cx = X0 + slot * (i + 0.5)
        start = cx - (bw + 2) * len(series) / 2 + 1
        for j, s in enumerate(series):
            v = vals.get(s)
            if v is None:
                continue
            x = start + j * (bw + 2)
            y0, y1 = sorted([Y(lo), Y(v)])
            out.append(f'<g class="mark"><title>{html.escape(tip(gl, s, v))}</title><rect x="{x:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(y1 - y0, 0.8):.1f}" rx="2" fill="{colors[s]}"/>'
                       f'<rect x="{x - 1:.1f}" y="{Y0}" width="{bw + 2:.1f}" height="{Y1 - Y0}" fill="transparent"/></g>')
        out.append(f'<text x="{cx:.1f}" y="{Y1 + 22}" text-anchor="middle" class="cat">{gl}</text>')
    out.append(f'<line x1="{X0 - 12}" x2="{X1 + 4}" y1="{Y(lo):.1f}" y2="{Y(lo):.1f}" stroke="#5E636C" stroke-width="1"/>')
    out.append("</svg>")
    return "\n".join(out)


PCOL = {"early": "#C9DCEB", "middle": "#6FA8D6", "late": "#0E4C73"}
fig1 = bars([(f"{fq} documents", {pos: L(fq, pos) for pos in ("early", "middle", "late")}) for fq in (2, 8, 32, 128)],
            ["early", "middle", "late"], PCOL, 0, 1, [0, .25, .5, .75, 1], lambda t: f"{round(t * 100)}%",
            "Share of planted facts the trained model answers correctly, by number of documents and position in training",
            lambda gl, s, v: f"{gl}, placed {s} in training: {p(v)} answered correctly")

# figure 2: retrieval AP per method, one bar each (horizontal)
def hbars(rows, lo, hi, ticks, fmt, label, color="#2083BF", h=None):
    n = len(rows)
    H = h or 40 + 34 * n
    LX, RX = 250, 690
    X = lambda v: LX + (v - lo) / (hi - lo) * (RX - LX)
    out = [f'<svg viewBox="0 0 720 {H}" role="img" aria-label="{html.escape(label)}" class="chart">']
    for t in ticks:
        out.append(f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="10" y2="{H - 28}" stroke="#E3E0D8" stroke-width="1"/>')
        out.append(f'<text x="{X(t):.1f}" y="{H - 10}" text-anchor="middle" class="tick">{fmt(t)}</text>')
    for i, r in enumerate(rows):
        y = 16 + 34 * i
        out.append(f'<text x="{LX - 12}" y="{y + 15}" text-anchor="end" class="cat">{r["label"]}</text>')
        if "ci" in r:
            lo_, est, hi_ = r["ci"]
            out.append(f'<g class="mark"><title>{html.escape(r["label"])}: {est:+.3f} (95% interval {lo_:+.3f} to {hi_:+.3f})</title>'
                       f'<line x1="{X(lo_):.1f}" x2="{X(hi_):.1f}" y1="{y + 11}" y2="{y + 11}" stroke="{r.get("color", color)}" stroke-width="2.5"/>'
                       f'<circle cx="{X(est):.1f}" cy="{y + 11}" r="6" fill="{r.get("color", color)}"/>'
                       f'<rect x="{LX}" y="{y}" width="{RX - LX}" height="24" fill="transparent"/></g>')
        else:
            v = r["v"]
            out.append(f'<g class="mark"><title>{html.escape(r["label"])}: {v:.3f}</title><rect x="{X(lo):.1f}" y="{y + 2}" width="{max(X(v) - X(lo), 1):.1f}" height="18" rx="2" fill="{r.get("color", color)}"/>'
                       f'<rect x="{LX}" y="{y}" width="{RX - LX}" height="24" fill="transparent"/></g>')
    if lo < 0 < hi:
        out.append(f'<line x1="{X(0):.1f}" x2="{X(0):.1f}" y1="10" y2="{H - 28}" stroke="#5E636C" stroke-width="1.2"/>')
    out.append("</svg>")
    return "\n".join(out)


GRAD = {"grad_dot_final", "grad_cos_final", "grad_if_final", "tracin_grad_dot", "tracin_grad_if"}
colr = lambda m: "#DF8224" if m in GRAD else ("#3E8E5E" if m in ("embed_bge", "rep_cos_final") else "#5E636C")
ret_rows = sorted(({"label": NAMES[m], "v": ap(m), "color": colr(m)} for m in ORDER), key=lambda r: -r["v"])
fig2 = hbars(ret_rows, 0, 1, [0, .25, .5, .75, 1], lambda t: f"{t:.2f}", "Average precision at finding each fact's planted documents")
c_rows = sorted(({"label": NAMES[m], "ci": (part[m][1], part[m][0], part[m][2]), "color": colr(m)} for m in ORDER), key=lambda r: -r["ci"][1])
fig3 = hbars(c_rows, -0.2, 0.4, [-.2, -.1, 0, .1, .2, .3, .4], lambda t: f"{t:+.1f}".replace("+0.0", "0"),
             "Partial correlation between attributed mass and causal effect, controlling answer length and difficulty")


def t_learned():
    rows = []
    for fq in (2, 8, 32, 128):
        rows.append(f"<tr><td>{fq}</td>" + "".join(f"<td>{p(L(fq, pos))}</td>" for pos in ("early", "middle", "late", "all")) + "</tr>")
    rows.append('<tr><td>All</td>' + "".join(f"<td>{p(L('all', pos))}</td>" for pos in ("early", "middle", "late", "all")) + "</tr>")
    return "\n".join(rows)


def t_ret():
    rows = []
    for m in sorted(ORDER, key=lambda m: -ap(m)):
        a, b = RET[m]["A"], RET[m]["B"]
        rows.append(f"<tr><td>{NAMES[m]}</td><td>{a['ap']:.3f}</td><td>{b['ap']:.3f}</td><td>{p((a['r10'] + b['r10']) / 2)}</td>"
                    f"<td>{(a['by_freq']['2'] + b['by_freq']['2']) / 2:.2f}</td><td>{(a['by_freq']['128'] + b['by_freq']['128']) / 2:.2f}</td></tr>")
    return "\n".join(rows)


def t_causal():
    rows = []
    for m in sorted(ORDER, key=lambda m: -part[m][0]):
        w = C2[m]["within_cell_vs_effect"]
        pe = part[m]
        rows.append(f"<tr><td>{NAMES[m]}</td><td>{sg(w[0])} <small>[{sg(w[1])}, {sg(w[2])}]</small></td>"
                    f"<td>{sg(C3[m]['vs_len'])}</td><td>{sg(C3[m]['vs_base_loss'])}</td>"
                    f"<td class=\"hl\">{sg(pe[0])} <small>[{sg(pe[1])}, {sg(pe[2])}]</small></td></tr>")
    return "\n".join(rows)


HEAD = TPL.split("<style", 1)[0]
HEAD = HEAD.replace(re.search(r"<title>.*?</title>", HEAD).group(0), f"<title>{TITLE}: grading training-data attribution against ground truth · trifero</title>")
for old, new in [(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(DESC)}">'),
                 (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{html.escape(DESC)}">'),
                 (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{TITLE}">')]:
    HEAD = re.sub(old, new, HEAD)
HEAD = HEAD.replace("https://trifero.ai/research/show-your-work/", URL)
ld = {"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": URL,
      "datePublished": "2026-10-27", "dateModified": "2026-10-27", "inLanguage": "en-US", "author": {"@type": "Person", "name": "Sean Trifero"},
      "publisher": {"@id": "https://trifero.ai/#organization", "@type": "ResearchOrganization", "name": "trifero", "url": "https://trifero.ai/"},
      "image": "https://trifero.ai/wp-content/trifero-lab/og-v3.png",
      "about": ["Training data attribution", "Influence functions", "Interpretability", "Language model pretraining", "Benchmarks"],
      "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "isPartOf": {"@id": "https://trifero.ai/#website"}}
HEAD = re.sub(r'<script type="application/ld\+json" nonce="\{\{NONCE\}\}">.*?</script>',
              lambda _: f'<script type="application/ld+json" nonce="{{{{NONCE}}}}">{json.dumps(ld, ensure_ascii=False)}</script>', HEAD, flags=re.S)
EXTRA = ("\n.sw-early{background:#C9DCEB}.sw-middle{background:#6FA8D6}.sw-late{background:#0E4C73}"
         ".sw-grad{background:#DF8224}.sw-text{background:#3E8E5E}.sw-kw{background:#5E636C}\n")
LEG1 = '<div class="legend"><span><i class="sw-early"></i>Placed early (0 to 20%)</span><span><i class="sw-middle"></i>Middle (40 to 60%)</span><span><i class="sw-late"></i>Late (last 15%)</span></div>'
LEG2 = '<div class="legend"><span><i class="sw-grad"></i>Gradient methods</span><span><i class="sw-text"></i>Embedding and hidden-state</span><span><i class="sw-kw"></i>Keyword</span></div>'
tr = D["train"]
docs = D["docs"]
meta = D["meta"]
ifm = (D["if_mass_learned"], D["if_mass_unlearned"])

body = f'''<style nonce="{{{{NONCE}}}}">{CSS}{EXTRA}</style>
</head>
<body>

<div class="page">
  <header class="mast">
    <div class="plate">
      <a class="brand" href="/">trifero<span class="tld">.ai</span></a>
      <span class="tag">Technical report</span>
    </div>
  </header>

  <div class="col head">
    <div class="eyebrow"><span class="dot" aria-hidden="true"></span>Attribution<span aria-hidden="true">/</span>October 2026</div>
    <h1>{TITLE}</h1>
    <p class="sub">We trained two language models from scratch that differ only in which made-up facts they read, so we know exactly what each training document did, and used them to grade the methods that claim to trace a model&rsquo;s knowledge back to its training data.</p>
    <div class="byline"><span><b>Sean Trifero</b>, trifero.ai lab (lead)</span><span>Engineering and drafting assistance: Claude (Anthropic)</span></div>
  </div>

  <div class="col">
    <div class="abstract">
      <span class="label">Abstract</span>
      <p>Training-data attribution methods rank training documents by how responsible they are for something a model says. They are hard to grade, because for a real model nobody knows the right answer. We built the answer in. Two 110M-parameter models were pretrained from scratch on the same 5B tokens, except that each also read the documents for a different half of 528 planted facts about fictional people, places and Python packages, at 2 to 128 documents per fact and early, middle or late in training. Because the other model never saw a fact, the difference between the two is the causal effect of that fact&rsquo;s documents. We graded eight methods, from keyword search to influence functions and TracIn, on two questions. Finding the documents that contain a fact was easy: keyword search scored {ap("bm25"):.3f} average precision and TracIn with influence functions {ap("tracin_grad_if"):.2f}. Telling which documents actually changed the model was not. Gradient methods correlated with the causal effect at first ({sg(w_lo)} to {sg(w_hi)}), but that came from answer length and difficulty; holding both fixed, none exceeded {sg(max_grad_partial)}, and only one interval cleared zero, by {part['grad_cos_final'][1]:.3f}. Influence computed on the finished model tracked how badly it still answered a fact ({sg(D["if_vs_loss"])}), not what its training documents did. Embedding search kept a small real signal ({sg(part["embed_bge"][0])}).</p>
    </div>
  </div>

  <div class="plate findings" aria-label="Key findings">
    <div class="finding"><div class="v">{ap("bm25"):.3f}</div><p>Average precision of plain keyword search at finding each fact&rsquo;s documents, the best of eight methods. Retrieval benchmarks reward finding the text, which is the easy part.</p></div>
    <div class="finding"><div class="v">{sg(max_grad_partial)}</div><p>The highest correlation any gradient method reached with what the documents actually did, once answer length and difficulty were held fixed. Only one interval cleared zero, by {part['grad_cos_final'][1]:.3f}.</p></div>
    <div class="finding"><div class="v">{sg(D["if_vs_loss"])}</div><p>Correlation between influence-function scores on the finished model and the model&rsquo;s current loss on the fact. It measures what would help now, so forgotten facts score highest.</p></div>
    <div class="finding"><div class="v">{p(L(128, "early"))}</div><p>Facts seen in 128 documents during the first fifth of training that the finished model still answered correctly, against {p(D["unseen_acc"])} for facts it never saw. Keyword search still found their documents perfectly.</p></div>
  </div>

  <div class="col">
    <h2 id="question"><span class="n">1</span>The question</h2>
      <p>When a model says something, which training documents put it there? Training-data attribution answers with a ranking of documents. It underpins work on data valuation, on finding the source of harmful outputs, and on understanding how models store knowledge. The methods range from plain text search to influence functions, which estimate how much each training example moved the model, and TracIn, which adds up those effects over checkpoints.</p>
      <p>Grading them is the problem. For a real model nobody knows which documents were responsible, so evaluations either ask whether a method finds documents that contain the answer, which simple keyword search does well, or retrain models without the top-ranked documents, which is expensive and noisy. The closest recent benchmark, DataDignity, plants fabricated articles by continuing to train finished models, and its authors note that results &ldquo;may not transfer to real-world pretraining&rdquo;.</p>
      <p>We built the ground truth into pretraining itself. Two models start from nothing and read the same 5B tokens in the same order; the only difference is which half of a set of invented facts each one reads. Whatever one model knows about a fact and the other does not was caused by that fact&rsquo;s documents.</p>

    <h2 id="setup"><span class="n">2</span>Setup</h2>
      <h3>Two models, one difference</h3>
      <p>Both are 110M-parameter versions of <a href="/research/elroy/">Elroy</a>, our from-scratch Llama-style model (12 layers, width 768, 1,024-token context, Elroy&rsquo;s own 32k tokenizer). Each trained for {tr["A"]["steps"]:,} steps on {meta["tokens"] / 1e9:.2f}B tokens of educational Python, web text and synthetic textbooks, read in a fixed order so that every document&rsquo;s position in training is known. The two finished at the same loss ({tr["A"]["final_loss"]:.3f} and {tr["B"]["final_loss"]:.3f}).</p>
      <h3>528 planted facts</h3>
      <p>Each fact is one attribute of a fictional entity: the capital of an invented island, the founder of an invented company, the exception an invented Python package raises on timeout. Qwen3.5-9B wrote {docs["planted"]:,} documents stating them in varied styles, from travel blogs to API references (median {docs["words_median"]} words), each checked to state its fact verbatim and mention no other. The facts form a balanced grid: two domains, four frequencies (2, 8, 32 or 128 documents), three positions in training (the first fifth, the middle fifth or the last 15%), and two models. Every entity also has two distractor documents about some other detail of it, read by both models, to catch methods that only match the entity&rsquo;s name. Each planted document filled its own training window, padded with held-out web text, and the two models&rsquo; streams differ only in those windows.</p>
      <h3>Eight methods</h3>
      <ul>
        <li><b>BM25</b> keyword search, and <b>embedding search</b> with bge-base, over the decoded training windows.</li>
        <li><b>Hidden-state similarity</b>: cosine of the model&rsquo;s own final-layer states.</li>
        <li><b>Gradient dot product</b> and <b>gradient cosine</b> between the training example and the query, on the finished model.</li>
        <li><b>Influence functions</b>: the same gradients preconditioned by a Gauss-Newton approximation of the curvature, the core of TRAK and similar methods.</li>
        <li><b>TracIn</b>: dot product or influence scores summed over four checkpoints (31%, 60% and 92% of training and the end), weighted by learning rate.</li>
      </ul>
      <p>Gradients came from all 60 linear layers in the transformer blocks, compressed with fixed random projections (LoGra-style) to 15,360 dimensions; we checked the compression against exact gradients to one part in a million. Each method ranked a pool of 112,270 training windows per model: every planted and distractor window plus 100,000 random others. Queries were each fact in two forms, a sentence to complete and a question, with the answer appended.</p>
      <h3>Measuring the causal effect</h3>
      <p>For each fact, the causal effect is the log-probability of the right answer under the model that read its documents minus the same under the model that did not, averaged over both query forms. A fact counts as learned if that effect is positive and the trained model ranks the right answer first among 20 invented candidates.</p>

    <h2 id="learned"><span class="n">3</span>What the models learned</h2>
      <p>Frequency and timing both mattered. Facts in the last 15% of training were learned most often; facts from the first fifth were mostly forgotten, even with 128 documents.</p>
    </div>

    <figure class="plate">
      <div class="chartbox">
        {LEG1}
        {fig1}
      </div>
      <figcaption><b>Figure 1.</b> Share of planted facts the trained model answers correctly (top choice of 20 candidates), averaged over the two models and both query forms. Facts a model never saw scored {p(D["unseen_acc"])}, the chance level.</figcaption>
    </figure>

    <div class="plate tbl">
      <table>
        <caption><b>Table 1.</b> Facts answered correctly by the model that read them, by documents per fact and position in training.</caption>
        <thead><tr><th>Documents per fact</th><th>Early</th><th>Middle</th><th>Late</th><th>All</th></tr></thead>
        <tbody>
{t_learned()}
        </tbody>
      </table>
    </div>

    <div class="col">
      <p>This is what makes the test useful. The documents of an early fact still contain its text, so a method that only matches text will rank them as responsible, but by the end of training they no longer affect the model.</p>

    <h2 id="finding"><span class="n">4</span>Finding the documents</h2>
      <p>The usual test: for each query, rank the pool and see how high the fact&rsquo;s own planted documents land.</p>
    </div>

    <figure class="plate">
      <div class="chartbox">
        {LEG2}
        {fig2}
      </div>
      <figcaption><b>Figure 2.</b> Average precision at retrieving each fact&rsquo;s planted documents from 112,270 training windows, mean of the two models (528 queries each).</figcaption>
    </figure>

    <div class="plate tbl">
      <table>
        <caption><b>Table 2.</b> Retrieval by method. Recall@10 is the share of a fact&rsquo;s documents in the top ten (capped by the number of documents).</caption>
        <thead><tr><th>Method</th><th>AP, model A</th><th>AP, model B</th><th>Recall@10</th><th>AP, 2 documents</th><th>AP, 128 documents</th></tr></thead>
        <tbody>
{t_ret()}
        </tbody>
      </table>
    </div>

    <div class="col">
      <p>Keyword search was nearly perfect, because each invented name appears only in its own fact&rsquo;s documents. This matches what Chang and colleagues found on real pretraining data: BM25 beats gradient methods at finding passages that state a fact. Among gradient methods, the curvature correction mattered most: plain gradient similarity scored {ap("grad_dot_final"):.2f} to {ap("grad_cos_final"):.2f}, influence functions {ap("grad_if_final"):.2f}, and TracIn with influence {ap("tracin_grad_if"):.2f}. Hidden-state similarity found almost nothing.</p>

    <h2 id="causal"><span class="n">5</span>Did attribution track what training did?</h2>
      <p>The harder test asks whether a method gives more weight to documents that changed the model more. For each fact we took the method&rsquo;s attributed mass (the average standardized score of the fact&rsquo;s own documents) and compared it with the fact&rsquo;s causal effect. To keep frequency, timing and domain from driving the result, both were ranked within each of the 24 cells of the design.</p>
      <p>Gradient methods looked promising at first: within cells, their mass correlated with the causal effect at {sg(w_lo)} to {sg(w_hi)}. But their mass also tracked the length of the answer in tokens ({sg(len_lo)} to {sg(len_hi)}) and how hard the answer was for the model that never saw it. Both inflate the causal effect, which is a sum of log-probabilities over the answer&rsquo;s tokens, and both inflate gradients. Holding them fixed removes the signal.</p>
    </div>

    <figure class="plate">
      <div class="chartbox">
        {LEG2}
        {fig3}
      </div>
      <figcaption><b>Figure 3.</b> Partial correlation between each method&rsquo;s attributed mass and the causal effect of the fact&rsquo;s documents, within design cells, controlling for answer length and the unexposed model&rsquo;s loss. Dots are estimates, lines 95% bootstrap intervals over 528 facts.</figcaption>
    </figure>

    <div class="plate tbl">
      <table>
        <caption><b>Table 3.</b> Attributed mass against causal effect, within design cells. &ldquo;Length&rdquo; and &ldquo;difficulty&rdquo; are correlations of the mass with answer length and with the unexposed model&rsquo;s loss; the last column holds both fixed.</caption>
        <thead><tr><th>Method</th><th>vs causal effect</th><th>vs length</th><th>vs difficulty</th><th>vs causal effect, controlled</th></tr></thead>
        <tbody>
{t_causal()}
        </tbody>
      </table>
    </div>

    <div class="col">
      <ul>
        <li><b>No gradient method tracked the causal effect.</b> After the controls, influence functions scored {sg(part["grad_if_final"][0])}, TracIn with influence {sg(part["tracin_grad_if"][0])}, and the best gradient method {sg(max_grad_partial)}. Only gradient cosine&rsquo;s interval excludes zero, with a lower bound of {sg(part['grad_cos_final'][1], 3)}.</li>
        <li><b>Embedding search kept a small real signal</b> ({sg(part["embed_bge"][0])}, interval {sg(part["embed_bge"][1])} to {sg(part["embed_bge"][2])}), as did hidden-state similarity ({sg(part["rep_cos_final"][0])}), which barely found the documents at all.</li>
        <li><b>Keyword search tracked nothing</b> ({sg(part["bm25"][0])}). It finds the text whether or not the text mattered.</li>
      </ul>

    <h2 id="influence"><span class="n">6</span>What influence on a finished model measures</h2>
      <p>Influence functions estimate how much upweighting a training example would lower the loss on a query, at the model&rsquo;s current parameters. For a fact the model has forgotten, the loss is high and its own documents point straight at the answer, so they score highest. Across all 528 facts, influence-function mass correlated {sg(D["if_vs_loss"])} with the finished model&rsquo;s own loss on the fact, and facts the model never learned received more mass than facts it did (standardized {ifm[1]:.1f} against {ifm[0]:.1f}). That is the right answer to &ldquo;which data would help now&rdquo; and the wrong one to &ldquo;which data made the model what it is&rdquo;. TracIn adds history by summing over checkpoints, but over four checkpoints it did not change the picture.</p>

    <h2 id="discussion"><span class="n">7</span>Discussion</h2>
      <h3>Retrieval is the wrong exam</h3>
      <p>Most attribution benchmarks score whether a method retrieves documents that contain the answer. Here a keyword index won that test and carried no information about which documents mattered. A benchmark that cannot separate text that is present from text that had an effect will keep rewarding search.</p>
      <h3>Controls matter more than methods</h3>
      <p>Without controlling for answer length and difficulty, every gradient method would have looked like a moderate success. Any evaluation that correlates attribution scores with an effect measured in summed log-probability should report that check.</p>
      <h3>Ground truth needs paired models</h3>
      <p>The pairing is what made the causal test possible: two models that differ only in which facts they read. At 110M parameters each run took about 10.7 hours on two workstation GPUs, so this kind of ground truth is within reach of a small lab.</p>

    <h2 id="limits"><span class="n">8</span>Limitations</h2>
      <ul>
        <li><b>One model size and one seed per stream.</b> At 110M parameters and 5B tokens, most rare facts were never learned, which limits the range of causal effects. Larger models learn rarer facts.</li>
        <li><b>Fact-level ground truth.</b> We know what each fact&rsquo;s documents did together, not each document separately. Per-document ground truth needs more paired runs.</li>
        <li><b>Synthetic facts with unique names</b> make retrieval unrealistically easy. They are what make the causal answer certain; facts that share wording with the rest of the corpus would be harder for every method.</li>
        <li><b>Approximations.</b> Gradients were randomly projected to 15,360 dimensions, influence used a Gauss-Newton approximation in that space, and TracIn used four checkpoints. Exact or higher-rank versions may do better.</li>
        <li><b>Data mix.</b> One code source ran 13% short of its share of the corpus; the other Python source covered the difference (47.6% and 17.4% instead of 45% and 20%).</li>
        <li><b>Document quality.</b> A few documents about API keys also called the environment variable by the package&rsquo;s name while still stating the correct one.</li>
      </ul>

    <h2 id="release"><span class="n">9</span>Release</h2>
      <p>The benchmark is public so others can grade their own methods. The two models, with weights saved every 0.5B tokens, are on Hugging Face as <a href="https://huggingface.co/strifero/tda-124m-A">tda-124m-A</a> and <a href="https://huggingface.co/strifero/tda-124m-B">tda-124m-B</a>. The <a href="https://huggingface.co/datasets/strifero/attribution-groundtruth">dataset</a> holds the 528 facts, their planted and distractor documents, the answer key, the stream order with a hash of every training window, the candidate pools and our scores. The <a href="https://github.com/strifero/attribution-groundtruth">code</a> covers the stream builder, training, every method and the causal tests. All planted content is fictional, and everything is Apache-2.0.</p>

    <h2 id="repro"><span class="n">10</span>Reproducibility</h2>
      <p>Everything ran on 24 to 26 October 2026 on two NVIDIA RTX A4500 GPUs (20 GB each, NVLink) in the trifero lab, scheduled through Slurm. Pretraining used Elroy&rsquo;s training code with an ordered loader, bf16 autocast, 262,144 tokens per step, learning rate 6e-4 with cosine decay to 6e-5, and ran at about {tr["A"]["tok_s"] // 1000}k tokens per second. Documents were written by Qwen3.5-9B with vLLM 0.31.0. Gradient features took two to three hours per checkpoint per model on one GPU. Per-query scores and per-fact results for every method are stored in the study repository.</p>

    <h2 id="refs"><span class="n">11</span>References</h2>
      <ol class="refs">
        <li>Chang, T. A., Rajagopal, D., Bolukbasi, T., Dixon, L., and Tenney, I. Scalable influence and fact tracing for large language model pretraining. 2024. <a href="https://arxiv.org/abs/2410.17413">arxiv.org/abs/2410.17413</a></li>
        <li>DataDignity: training data attribution for large language models. 2026. <a href="https://arxiv.org/abs/2605.05687">arxiv.org/abs/2605.05687</a></li>
        <li>Akyürek, E., et al. Towards tracing factual knowledge in language models back to the training data. Findings of EMNLP 2022. <a href="https://arxiv.org/abs/2205.11482">arxiv.org/abs/2205.11482</a></li>
        <li>Koh, P. W., and Liang, P. Understanding black-box predictions via influence functions. ICML 2017. <a href="https://arxiv.org/abs/1703.04730">arxiv.org/abs/1703.04730</a></li>
        <li>Pruthi, G., Liu, F., Kale, S., and Sundararajan, M. Estimating training data influence by tracing gradient descent (TracIn). NeurIPS 2020. <a href="https://arxiv.org/abs/2002.08484">arxiv.org/abs/2002.08484</a></li>
        <li>Park, S. M., et al. TRAK: attributing model behavior at scale. ICML 2023. <a href="https://arxiv.org/abs/2303.14186">arxiv.org/abs/2303.14186</a></li>
        <li>Grosse, R., et al. Studying large language model generalization with influence functions. 2023. <a href="https://arxiv.org/abs/2308.03296">arxiv.org/abs/2308.03296</a></li>
        <li>Choe, S. K., et al. What is your data worth to GPT? LLM-scale data valuation with influence functions (LoGra). 2024. <a href="https://arxiv.org/abs/2405.13954">arxiv.org/abs/2405.13954</a></li>
        <li>trifero lab. Elroy, from scratch. 2026. <a href="/research/elroy/">trifero.ai/research/elroy</a></li>
      </ol>

    <footer>trifero.ai lab &middot; offensive research to understand defense &middot; info@trifero.ai</footer>
  </div>
</div>

</body>
</html>
'''
page = HEAD + body
assert not any(c in page for c in ("—", "–")), "dash characters present"
assert "show-your-work" not in page, "stale template reference"
assert ' style="' not in body, "inline style attribute (CSP blocks it)"
(HERE / f"{SLUG}.php").write_text(page)
print("wrote", len(page))
