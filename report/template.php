<?php defined( 'ABSPATH' ) || exit; ?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Show your work: distilling reasoning into a 360M model · trifero</title>
<meta name="description" content="We distilled Qwen3.5 reasoning (0.8B to 9B teachers) into Elroy, a 360M code model trained from scratch. Correct code alone raised its held-out score 10 to 13 points, no more than GPT-4o reference solutions did. Adding the teachers&#x27; reasoning cut the gain, and long reasoning erased it.">
<link rel="canonical" href="https://trifero.ai/research/show-your-work/">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#FBFAF7">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="article">
<meta property="og:site_name" content="trifero">
<meta property="og:url" content="https://trifero.ai/research/show-your-work/">
<meta property="og:title" content="Show your work">
<meta property="og:description" content="We distilled Qwen3.5 reasoning (0.8B to 9B teachers) into Elroy, a 360M code model trained from scratch. Correct code alone raised its held-out score 10 to 13 points, no more than GPT-4o reference solutions did. Adding the teachers&#x27; reasoning cut the gain, and long reasoning erased it.">
<meta property="og:image" content="https://trifero.ai/wp-content/trifero-lab/og-v3.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="trifero.ai. Find what it knows. Fix what it breaks. See what it becomes.">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/wp-content/trifero-lab/fonts/instrument-serif.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/wp-content/trifero-lab/fonts/geist.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json" nonce="{{NONCE}}">{"@context": "https://schema.org", "@type": "TechArticle", "headline": "Show your work", "description": "We distilled Qwen3.5 reasoning (0.8B to 9B teachers) into Elroy, a 360M code model trained from scratch. Correct code alone raised its held-out score 10 to 13 points, no more than GPT-4o reference solutions did. Adding the teachers' reasoning cut the gain, and long reasoning erased it.", "url": "https://trifero.ai/research/show-your-work/", "datePublished": "2026-10-22", "dateModified": "2026-10-22", "inLanguage": "en-US", "author": {"@type": "Person", "name": "Sean Trifero"}, "publisher": {"@id": "https://trifero.ai/#organization", "@type": "ResearchOrganization", "name": "trifero", "url": "https://trifero.ai/"}, "image": "https://trifero.ai/wp-content/trifero-lab/og-v3.png", "about": ["Knowledge distillation", "Reasoning", "Small language models", "Code generation", "Elroy"], "mainEntityOfPage": {"@type": "WebPage", "@id": "https://trifero.ai/research/show-your-work/"}, "isPartOf": {"@id": "https://trifero.ai/#website"}}</script>
<style nonce="{{NONCE}}">
@font-face{font-family:'Instrument Serif';font-style:normal;font-weight:400;font-display:swap;src:url(/wp-content/trifero-lab/fonts/instrument-serif.woff2) format('woff2')}
@font-face{font-family:'Instrument Serif';font-style:italic;font-weight:400;font-display:swap;src:url(/wp-content/trifero-lab/fonts/instrument-serif-italic.woff2) format('woff2')}
@font-face{font-family:'Geist';font-style:normal;font-weight:100 900;font-display:swap;src:url(/wp-content/trifero-lab/fonts/geist.woff2) format('woff2')}
@font-face{font-family:'Geist Mono';font-style:normal;font-weight:100 900;font-display:swap;src:url(/wp-content/trifero-lab/fonts/geist-mono.woff2) format('woff2')}

/* Layout: one reading column (~68ch) on the trifero.ai warm ground; figures and
   tables widen to a 960px plate. Light only, matching the live lab site. */
:root{
  --ground:#FBFAF7;--paper:#FFFFFF;--ink:#16181C;--ink-2:#474C55;--ink-3:#5E636C;
  --line:#E3E0D8;--line-2:#ECE9E2;--rule:#CFCBC2;
  --orange:#DF8224;--orange-text:#C46A14;--blue:#2083BF;--blue-ink:#17679A;--blue-deep:#0F4C73;--gold:#B5751F;
  --c-base:#2083BF;--c-ablated:#DF8224;--c-healed:#7A5AA8;
  --serif:'Instrument Serif',Georgia,'Times New Roman',serif;
  --sans:'Geist','Helvetica Neue',system-ui,-apple-system,sans-serif;
  --mono:'Geist Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace;
  --read:680px;--plate:960px;
  color-scheme:light;
}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:var(--blue-ink)}a:hover{color:var(--blue-deep)}
:focus-visible{outline:2px solid var(--blue);outline-offset:3px;border-radius:4px}
.page{padding-inline:clamp(16px,5vw,64px);padding-block:0 96px}
.col{max-width:var(--read);margin-inline:auto}
.plate{max-width:var(--plate);margin-inline:auto}

/* masthead */
.mast{border-bottom:1px solid var(--line);padding-block:22px;margin-inline:calc(-1 * clamp(16px,5vw,64px));padding-inline:clamp(16px,5vw,64px);background:rgba(251,250,247,.92)}
.mast .plate{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
.brand{font-size:21px;font-weight:600;letter-spacing:-.02em;color:var(--blue);text-decoration:none}
.brand .tld{color:var(--gold)}
.tag{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);padding:5px 10px;border:1px solid var(--line);border-radius:999px;line-height:1}

/* title block */
.head{padding-block:72px 40px}
.eyebrow{display:flex;align-items:center;flex-wrap:wrap;gap:12px;font-family:var(--mono);font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}
.eyebrow .dot{width:8px;height:8px;border-radius:50%;background:var(--orange)}
h1{margin:24px 0 0;font-family:var(--serif);font-weight:400;font-size:clamp(46px,7vw,84px);line-height:.98;letter-spacing:-.015em;text-wrap:balance}
.sub{margin:22px 0 0;font-size:21px;line-height:1.5;color:var(--ink-2);text-wrap:pretty}
.byline{margin-top:28px;display:flex;flex-wrap:wrap;gap:8px 28px;font-size:14.5px;color:var(--ink-2)}
.byline b{font-weight:500;color:var(--ink)}

/* abstract */
.abstract{background:var(--paper);border:1px solid var(--line);padding:28px clamp(20px,4vw,40px) 30px;margin-block:8px 56px}
.abstract .label{display:block;margin-bottom:10px}
.abstract p{margin:0;font-size:17.5px;line-height:1.65}

.label{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}

/* findings */
.findings{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin-block:0 72px}
.finding{background:var(--paper);padding:26px 28px 28px;min-width:0}
.finding .v{font-size:34px;font-weight:600;letter-spacing:-.02em;line-height:1.1;font-variant-numeric:tabular-nums}
.finding .v small{font-size:16px;font-weight:500;color:var(--ink-3);letter-spacing:0}
.finding p{margin:10px 0 0;font-size:15.5px;line-height:1.55;color:var(--ink-2)}

/* body copy */
h2{scroll-margin-top:24px}
h2{margin:72px 0 0;font-family:var(--serif);font-weight:400;font-size:clamp(32px,4vw,44px);line-height:1.08;letter-spacing:-.01em;text-wrap:balance}
h2 .n{font-family:var(--mono);font-size:14px;letter-spacing:.08em;color:var(--orange-text);vertical-align:.55em;margin-right:12px}
h3{margin:36px 0 0;font-size:18px;font-weight:600;letter-spacing:-.01em}
.col p,.col li{text-wrap:pretty}
.col p{margin:16px 0 0}
.col ul{margin:14px 0 0;padding-left:22px}
.col li{margin-top:8px}
.col li::marker{color:var(--ink-3)}
code{font-family:var(--mono);font-size:.86em;background:var(--line-2);padding:1px 5px;border-radius:4px}
.verdict{margin-top:24px;border-left:3px solid var(--orange);padding:4px 0 4px 20px;font-family:var(--serif);font-size:26px;line-height:1.3}

/* figures */
figure{margin:36px auto 0}
.chartbox{background:var(--paper);border:1px solid var(--line);padding:20px clamp(12px,2.5vw,28px) 14px;overflow-x:auto}
.chart{width:100%;min-width:560px;height:auto;display:block;font-family:var(--sans)}
.chart .tick{font-family:var(--mono);font-size:11px;fill:var(--ink-3)}
.chart .cat{font-size:13px;fill:var(--ink);font-weight:500}
.chart .num{font-family:var(--mono);font-size:11.5px;fill:var(--ink-2)}
.chart .mark{cursor:default}
.chart .mark:hover path,.chart .mark:hover circle{opacity:.82}
.legend{display:flex;flex-wrap:wrap;gap:8px 22px;margin:0 0 12px;font-size:13.5px;color:var(--ink-2)}
.legend span{display:inline-flex;align-items:center;gap:8px}
.legend i{width:10px;height:10px;border-radius:2px;display:block}
.sw-base{background:var(--c-base)}.sw-ablated{background:var(--c-ablated)}.sw-healed{background:var(--c-healed)}
figcaption{max-width:var(--read);margin:14px auto 0;font-size:14.5px;line-height:1.55;color:var(--ink-2)}
figcaption b{color:var(--ink);font-weight:600}

/* tables */
.tbl{margin:28px auto 0;overflow-x:auto;background:var(--paper);border:1px solid var(--line)}
table{width:100%;border-collapse:collapse;font-size:14.5px;font-variant-numeric:tabular-nums}
caption{caption-side:top;text-align:left;padding:14px 18px 4px;font-size:14px;color:var(--ink-2)}
caption b{color:var(--ink);font-weight:600}
th,td{padding:9px 18px;text-align:right;border-bottom:1px solid var(--line-2);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
thead th{font-family:var(--mono);font-size:11.5px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);border-bottom:1px solid var(--rule)}
tbody tr:last-child td{border-bottom:0}
td.grp{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);padding-top:16px}
td .ci{color:var(--ink-3);font-size:12.5px;margin-left:6px}
td.hl{font-weight:600}

/* references */
.refs{margin-top:16px;padding-left:22px}
.refs li{font-size:14.5px;line-height:1.55;color:var(--ink-2);margin-top:10px}
.refs a{word-break:break-word}

.more{margin-top:72px}.more-list{list-style:none;padding:0;margin-top:16px}.more-list li{margin-top:16px;font-size:15.5px;line-height:1.5}.more-list a{font-weight:600}.more-list span{display:block;margin-top:2px;color:var(--ink-2);font-size:14.5px}.more-back{margin-top:22px;font-size:14.5px;color:var(--ink-2)}
footer{margin-top:80px;padding-top:24px;border-top:1px solid var(--line);font-size:13.5px;color:var(--ink-3)}

@media (max-width:640px){
  .findings{grid-template-columns:minmax(0,1fr)}
  .head{padding-block:48px 28px}
  .sub{font-size:18.5px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}

.sw-g{background:#8A8F98}.sw-fc{background:#7A5AA8}.sw-pr{background:#3E8E5E}.sw-l{background:#DF8224}.sw-m0{background:#9DC3DE}.sw-m1{background:#2083BF}.sw-g0{background:#EFC08C}.sw-g1{background:#DF8224}

.sw-08B{background:#C9DCEB}.sw-2B{background:#9DC3DE}.sw-4B{background:#2083BF}.sw-9B{background:#0E4C73}.sw-ref{background:#3E8E5E;height:3px!important}.sw-ctl{background:#DF8224;height:3px!important}.sw-base{background:#5E636C;height:3px!important}.excerpt{font-family:var(--mono);font-size:12.5px;line-height:1.55;white-space:pre-wrap;background:var(--paper);border:1px solid var(--line);padding:16px 18px;color:var(--ink-2);overflow-x:auto;margin:18px 0}
</style>
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
    <div class="eyebrow"><span class="dot" aria-hidden="true"></span>Distillation<span aria-hidden="true">/</span>October 2026</div>
    <h1>Show your work</h1>
    <p class="sub">We trained Elroy, our 360M-parameter code model, on worked solutions from four Qwen3.5 reasoning models to see whether a model this small can learn to reason by imitation.</p>
    <div class="byline"><span><b>Sean Trifero</b>, trifero.ai lab (lead)</span><span>Engineering and drafting assistance: Claude (Anthropic)</span></div>
  </div>

  <div class="col">
    <div class="abstract">
      <span class="label">Abstract</span>
      <p>Large reasoning models pass their skill to smaller ones when the smaller model is trained on their written reasoning, and distilled models from 1.5B parameters up have shown large gains. We asked whether the same works far below that size. Elroy is a 360M-parameter code model we trained from scratch, which means we know every token it has seen. We had Qwen3.5 0.8B, 2B, 4B and 9B solve 26,681 Python problems in thinking mode, kept only solutions that passed their unit tests, and fine-tuned Elroy three ways on the same verified code: code alone, code after a short explanation, and code after the teacher&rsquo;s full reasoning. Code alone raised Elroy&rsquo;s held-out accuracy from 32.9% to as much as 42.9%, 10 to 13 points above a matched control, but GPT-4o reference solutions to the same problems did just as well (42.4%). Adding a short explanation cut the gain by more than half. Adding the full reasoning erased it, and with less data it fell below the control. The size of the teacher made no difference to that pattern, and no training set raised HumanEval or MBPP above Elroy&rsquo;s starting score. At this scale, Elroy copied the form of reasoning without its substance.</p>
    </div>
  </div>

  <div class="plate findings" aria-label="Key findings">
    <div class="finding"><div class="v">+10 <small>to</small> +13 <small>points</small></div><p>Held-out gain from training on the teachers&rsquo; verified code alone, against a control with the same training schedule. The three teachers land within about three points of each other.</p></div>
    <div class="finding"><div class="v">42.9% <small>vs</small> 42.4%</div><p>Code from the 9B reasoning teacher against the dataset&rsquo;s own GPT-4o reference solutions. The teacher&rsquo;s value was correct code, which the dataset already had.</p></div>
    <div class="finding"><div class="v">&minus;5 <small>to</small> &minus;1 <small>points</small></div><p>Effect of the full reasoning traces at 1,200 problems, against the same control. At 3,800 problems they were neutral. They never helped.</p></div>
    <div class="finding"><div class="v">182 <small>of</small> 26,681</div><p>Problems that all four teachers solved with reasoning short enough for Elroy&rsquo;s 2,048-token context. Each teacher stays short on different problems.</p></div>
  </div>

  <div class="col">
    <h2 id="question"><span class="n">1</span>The question</h2>
      <p>DeepSeek showed in early 2025 that a model as small as 1.5B parameters gains sharply on math when fine-tuned on the written reasoning of a much larger model. Li and colleagues then found that models of 3B parameters and below learn poorly from long reasoning by strong teachers, and better from short reasoning or from smaller teachers. Below 1B parameters there is little evidence either way.</p>
      <p>Elroy, documented in <a href="/research/elroy/">our earlier report</a>, is a 360M-parameter Llama-style model we wrote and pretrained ourselves on about 20B tokens of educational Python and English. Because we built its corpus and its instruction data, we know what it saw before this study, and its instruction data was already filtered against the benchmarks we use. We asked three questions: does reasoning from a teacher raise a model this small above what correct answers alone give; does a short explanation work better than full reasoning; and does a teacher closer to Elroy&rsquo;s size teach better.</p>

    <h2 id="setup"><span class="n">2</span>Setup</h2>
      <h3>Problems</h3>
      <p>KodCode-V1 contains about 484,000 synthetic Python problems, each with a function signature, a reference solution and pytest tests; the solutions and tests were generated by GPT-4o and checked against each other. We kept instruction-style problems from five function-level subsets (Prefill, LeetCode, Algorithm, Data_Structure, Evol), rated easy or medium, with exactly one target function and a statement under 1,200 characters. We dropped 810 problems that KodCode flags as close to a public benchmark and 79 more that Elroy&rsquo;s own filter matched to HumanEval or MBPP text or solutions. That left 26,681 problems for the teachers and 500 held out for evaluation.</p>
      <h3>Teachers and traces</h3>
      <p>Qwen3.5 0.8B, 2B, 4B and 9B share a tokenizer, a training recipe and a thinking mode, so they differ mainly in size. Each solved every problem once in thinking mode (temperature 0.6, top-p 0.95, top-k 20) with a 2,048-token limit, because longer reasoning cannot fit in Elroy&rsquo;s context next to a problem and a solution. We ran every solution against its tests and kept only those that passed. Passing reasoning was screened again for benchmark text, which removed 4 to 15 traces per teacher.</p>
      <h3>Three training formats, one set of code</h3>
      <p>Every kept problem became three training examples with the same verified function at the end:</p>
      <ul>
        <li><b>Code only.</b> The function and nothing else.</li>
        <li><b>Short reasoning.</b> Two to four sentences from the same teacher, with thinking off, explaining its own solution, then the function.</li>
        <li><b>Long reasoning.</b> The teacher&rsquo;s full thinking, then the function.</li>
      </ul>
      <p>So the formats differ only in how much reasoning comes before identical code. For comparisons between teachers we drew equal-size sets from each teacher&rsquo;s own solved problems: 3,800 problems for the 2B, 4B and 9B, and 1,200 for all four teachers. A fifth condition used KodCode&rsquo;s GPT-4o reference solutions for the 4B teacher&rsquo;s problems, as code only.</p>
      <h3>Training and controls</h3>
      <p>Each run fine-tuned Elroy&rsquo;s decontaminated chat model for two epochs at learning rate 5e-5, the settings of its original instruction tuning. Every set was mixed one to one with examples from Elroy&rsquo;s original instruction data, which kept the narrow new data from overwriting what it already knew. The control is that replay data alone, at the same size, so every comparison below holds the training schedule fixed. Every condition ran with two seeds.</p>
      <h3>Evaluation</h3>
      <p>We converted Elroy to the standard Llama layout so vLLM could serve it, and checked the conversion against the original code: greedy decoding reproduced the published scores (HumanEval 22.0% against 22.6% published, HumanEval+ 21.3% against 21.3%, MBPP 35.4% against 35.0%). Results below use temperature 0.6 with four samples per problem, averaged over both seeds, on the 500 held-out KodCode problems, HumanEval and HumanEval+ (164 each) and MBPP (257). Intervals are 95% paired bootstrap intervals over problems.</p>

    <h2 id="teachers"><span class="n">3</span>What the teachers produced</h2>
      <p>Every teacher thought past the 2,048-token limit on most problems. The 4B was the most accurate when it finished; the 9B finished fewer problems than the 2B or 4B because it reasons longer.</p>
    </div>

    <div class="plate tbl">
      <table>
        <caption><b>Table 1.</b> Teacher output on 26,681 problems. Finished: the reasoning ended within the limit. Pass rate: share of finished solutions that passed their tests. Removed: passing traces that matched benchmark text. Kept: also fit Elroy&rsquo;s context. Median tokens: length of passing traces.</caption>
        <thead><tr><th>Teacher</th><th>Finished</th><th>Passed</th><th>Pass rate</th><th>Removed</th><th>Kept</th><th>Median tokens</th></tr></thead>
        <tbody>
<tr><td>Qwen3.5-0.8B</td><td>3,697</td><td>1,284</td><td>35%</td><td>4</td><td>1,275</td><td>824</td></tr>
<tr><td>Qwen3.5-2B</td><td>10,389</td><td>6,461</td><td>62%</td><td>15</td><td>6,390</td><td>769</td></tr>
<tr><td>Qwen3.5-4B</td><td>9,588</td><td>7,004</td><td>73%</td><td>14</td><td>6,981</td><td>1,044</td></tr>
<tr><td>Qwen3.5-9B</td><td>6,366</td><td>3,908</td><td>61%</td><td>9</td><td>3,892</td><td>1,089</td></tr>
        </tbody>
      </table>
    </div>

    <div class="col">
      <p>The teachers stayed short on different problems. Only 182 problems had usable reasoning from all four, so a shared problem set was not possible. Each teacher&rsquo;s set reflects the problems it found easy enough to solve briefly, which is what any distillation run under a length limit would get.</p>

    <h2 id="results"><span class="n">4</span>Results</h2>
    </div>

    <figure class="plate">
      <div class="chartbox">
        <div class="legend"><span><i class="sw-2B"></i>Qwen3.5-2B teacher</span><span><i class="sw-4B"></i>Qwen3.5-4B teacher</span><span><i class="sw-9B"></i>Qwen3.5-9B teacher</span><span><i class="sw-ref"></i>GPT-4o reference solutions</span><span><i class="sw-ctl"></i>Replay only</span><span><i class="sw-base"></i>Before</span></div>
        <svg viewBox="0 0 720 300" role="img" aria-label="KodCode held-out accuracy by training format and teacher, 3800 problems" class="chart">
<line x1="52" x2="704" y1="244.0" y2="244.0" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="248.0" text-anchor="end" class="tick">20%</text>
<line x1="52" x2="704" y1="202.4" y2="202.4" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="206.4" text-anchor="end" class="tick">25%</text>
<line x1="52" x2="704" y1="160.8" y2="160.8" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="164.8" text-anchor="end" class="tick">30%</text>
<line x1="52" x2="704" y1="119.2" y2="119.2" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="123.2" text-anchor="end" class="tick">35%</text>
<line x1="52" x2="704" y1="77.6" y2="77.6" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="81.6" text-anchor="end" class="tick">40%</text>
<line x1="52" x2="704" y1="36.0" y2="36.0" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="40.0" text-anchor="end" class="tick">45%</text>
<g class="mark"><title>Code only, Qwen3.5-2B teacher: 39.8%</title><rect x="123.0" y="79.7" width="30.0" height="164.3" rx="2" fill="#9DC3DE"/><rect x="122.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Code only, Qwen3.5-4B teacher: 40.1%</title><rect x="155.0" y="77.2" width="30.0" height="166.8" rx="2" fill="#2083BF"/><rect x="154.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Code only, Qwen3.5-9B teacher: 42.9%</title><rect x="187.0" y="53.9" width="30.0" height="190.1" rx="2" fill="#0E4C73"/><rect x="186.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="170.0" y="266" text-anchor="middle" class="cat">Code only</text>
<g class="mark"><title>Short reasoning, Qwen3.5-2B teacher: 32.5%</title><rect x="335.0" y="139.8" width="30.0" height="104.2" rx="2" fill="#9DC3DE"/><rect x="334.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Short reasoning, Qwen3.5-4B teacher: 34.2%</title><rect x="367.0" y="125.6" width="30.0" height="118.4" rx="2" fill="#2083BF"/><rect x="366.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Short reasoning, Qwen3.5-9B teacher: 34.4%</title><rect x="399.0" y="124.2" width="30.0" height="119.8" rx="2" fill="#0E4C73"/><rect x="398.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="382.0" y="266" text-anchor="middle" class="cat">Short reasoning</text>
<g class="mark"><title>Long reasoning, Qwen3.5-2B teacher: 29.8%</title><rect x="547.0" y="162.0" width="30.0" height="82.0" rx="2" fill="#9DC3DE"/><rect x="546.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Long reasoning, Qwen3.5-4B teacher: 27.4%</title><rect x="579.0" y="182.2" width="30.0" height="61.8" rx="2" fill="#2083BF"/><rect x="578.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Long reasoning, Qwen3.5-9B teacher: 28.6%</title><rect x="611.0" y="172.4" width="30.0" height="71.6" rx="2" fill="#0E4C73"/><rect x="610.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="594.0" y="266" text-anchor="middle" class="cat">Long reasoning</text>
<g class="mark"><title>Elroy before distillation: 32.9%</title><line x1="52" x2="704" y1="136.7" y2="136.7" stroke="#5E636C" stroke-width="1.6" stroke-dasharray="2 4"/></g>
<g class="mark"><title>Same training with replay only: 29.4%</title><line x1="52" x2="704" y1="165.4" y2="165.4" stroke="#DF8224" stroke-width="1.6" stroke-dasharray="6 4"/></g>
<g class="mark"><title>GPT-4o reference solutions, code only: 42.4%</title><line x1="52" x2="704" y1="57.8" y2="57.8" stroke="#3E8E5E" stroke-width="1.6" stroke-dasharray="1 0"/></g>
<line x1="52" x2="704" y1="244.0" y2="244.0" stroke="#5E636C" stroke-width="1"/>
</svg>
      </div>
      <figcaption><b>Figure 1.</b> Accuracy on the 500 held-out KodCode problems after training on 3,800 problems per teacher. The lines mark Elroy before distillation (32.9%), the replay-only control (29.4%) and the GPT-4o reference solutions (42.4%).</figcaption>
    </figure>

    <div class="col">
      <ul>
        <li><b>Correct code helped.</b> Code alone raised held-out accuracy to 39.8%, 40.1% and 42.9% for the 2B, 4B and 9B teachers, 10 to 13 points above the control.</li>
        <li><b>The reasoning teacher added nothing a dataset did not.</b> GPT-4o&rsquo;s reference solutions to the same problems, with no reasoning model involved, reached 42.4%.</li>
        <li><b>Reasoning made it worse.</b> A short explanation before the code gave 32.5% to 34.4%, less than half the gain. The full reasoning gave 27.4% to 29.8%, no better than the control.</li>
      </ul>
    </div>

    <figure class="plate">
      <div class="chartbox">
        <div class="legend"><span><i class="sw-08B"></i>Qwen3.5-0.8B teacher</span><span><i class="sw-2B"></i>Qwen3.5-2B teacher</span><span><i class="sw-4B"></i>Qwen3.5-4B teacher</span><span><i class="sw-9B"></i>Qwen3.5-9B teacher</span><span><i class="sw-ref"></i>GPT-4o reference solutions</span><span><i class="sw-ctl"></i>Replay only</span><span><i class="sw-base"></i>Before</span></div>
        <svg viewBox="0 0 720 300" role="img" aria-label="KodCode held-out accuracy by training format and teacher, 1200 problems" class="chart">
<line x1="52" x2="704" y1="244.0" y2="244.0" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="248.0" text-anchor="end" class="tick">20%</text>
<line x1="52" x2="704" y1="202.4" y2="202.4" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="206.4" text-anchor="end" class="tick">25%</text>
<line x1="52" x2="704" y1="160.8" y2="160.8" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="164.8" text-anchor="end" class="tick">30%</text>
<line x1="52" x2="704" y1="119.2" y2="119.2" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="123.2" text-anchor="end" class="tick">35%</text>
<line x1="52" x2="704" y1="77.6" y2="77.6" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="81.6" text-anchor="end" class="tick">40%</text>
<line x1="52" x2="704" y1="36.0" y2="36.0" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="40.0" text-anchor="end" class="tick">45%</text>
<g class="mark"><title>Code only, Qwen3.5-0.8B teacher: 35.3%</title><rect x="107.0" y="116.5" width="30.0" height="127.5" rx="2" fill="#C9DCEB"/><rect x="106.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Code only, Qwen3.5-2B teacher: 36.6%</title><rect x="139.0" y="105.9" width="30.0" height="138.1" rx="2" fill="#9DC3DE"/><rect x="138.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Code only, Qwen3.5-4B teacher: 35.0%</title><rect x="171.0" y="119.2" width="30.0" height="124.8" rx="2" fill="#2083BF"/><rect x="170.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Code only, Qwen3.5-9B teacher: 36.8%</title><rect x="203.0" y="104.0" width="30.0" height="140.0" rx="2" fill="#0E4C73"/><rect x="202.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="170.0" y="266" text-anchor="middle" class="cat">Code only</text>
<g class="mark"><title>Short reasoning, Qwen3.5-0.8B teacher: 32.0%</title><rect x="319.0" y="144.4" width="30.0" height="99.6" rx="2" fill="#C9DCEB"/><rect x="318.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Short reasoning, Qwen3.5-2B teacher: 30.9%</title><rect x="351.0" y="153.5" width="30.0" height="90.5" rx="2" fill="#9DC3DE"/><rect x="350.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Short reasoning, Qwen3.5-4B teacher: 30.7%</title><rect x="383.0" y="155.0" width="30.0" height="89.0" rx="2" fill="#2083BF"/><rect x="382.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Short reasoning, Qwen3.5-9B teacher: 31.0%</title><rect x="415.0" y="152.3" width="30.0" height="91.7" rx="2" fill="#0E4C73"/><rect x="414.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="382.0" y="266" text-anchor="middle" class="cat">Short reasoning</text>
<g class="mark"><title>Long reasoning, Qwen3.5-0.8B teacher: 25.9%</title><rect x="531.0" y="195.3" width="30.0" height="48.7" rx="2" fill="#C9DCEB"/><rect x="530.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Long reasoning, Qwen3.5-2B teacher: 29.0%</title><rect x="563.0" y="168.7" width="30.0" height="75.3" rx="2" fill="#9DC3DE"/><rect x="562.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Long reasoning, Qwen3.5-4B teacher: 24.7%</title><rect x="595.0" y="204.9" width="30.0" height="39.1" rx="2" fill="#2083BF"/><rect x="594.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>Long reasoning, Qwen3.5-9B teacher: 25.4%</title><rect x="627.0" y="199.1" width="30.0" height="44.9" rx="2" fill="#0E4C73"/><rect x="626.0" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="594.0" y="266" text-anchor="middle" class="cat">Long reasoning</text>
<g class="mark"><title>Elroy before distillation: 32.9%</title><line x1="52" x2="704" y1="136.7" y2="136.7" stroke="#5E636C" stroke-width="1.6" stroke-dasharray="2 4"/></g>
<g class="mark"><title>Same training with replay only: 30.0%</title><line x1="52" x2="704" y1="160.6" y2="160.6" stroke="#DF8224" stroke-width="1.6" stroke-dasharray="6 4"/></g>
<g class="mark"><title>GPT-4o reference solutions, code only: 36.4%</title><line x1="52" x2="704" y1="107.3" y2="107.3" stroke="#3E8E5E" stroke-width="1.6" stroke-dasharray="1 0"/></g>
<line x1="52" x2="704" y1="244.0" y2="244.0" stroke="#5E636C" stroke-width="1"/>
</svg>
      </div>
      <figcaption><b>Figure 2.</b> The same comparison with 1,200 problems per teacher, which includes the 0.8B. Code beats short reasoning beats long reasoning for every teacher, and long reasoning falls below the replay-only control for every teacher, significantly for all but the 2B.</figcaption>
    </figure>

    <div class="col">
      <p>The teacher closest to Elroy&rsquo;s size did not teach better. With 1,200 problems, code from the 0.8B gave 35.3% against 36.8% from the 9B, and its full reasoning cost 4.2 points against the control, in line with the 4B and 9B.</p>
    </div>

    <div class="plate tbl">
      <table>
        <caption><b>Table 2.</b> All conditions at 3,800 problems. Accuracy at temperature 0.6, four samples, mean of two seeds. The last column is the held-out KodCode difference from the replay-only control, with a 95% interval, in points.</caption>
        <thead><tr><th>Training data</th><th>HumanEval</th><th>HumanEval+</th><th>MBPP</th><th>KodCode held-out</th><th>KodCode vs control</th></tr></thead>
        <tbody>
<tr><td>Elroy before distillation</td><td>18.9%</td><td>16.8%</td><td>29.5%</td><td>32.9%</td><td></td></tr>
<tr><td>Replay only (control)</td><td>17.5%</td><td>16.1%</td><td>25.0%</td><td>29.4%</td><td></td></tr>
<tr><td class="grp" colspan="6">Code only</td></tr>
<tr><td>Qwen3.5-2B teacher</td><td>17.8%</td><td>16.8%</td><td>27.4%</td><td>39.8%</td><td class="hl">+10.3 <small>[+7.6, +13.0]</small></td></tr>
<tr><td>Qwen3.5-4B teacher</td><td>18.1%</td><td>17.4%</td><td>26.7%</td><td>40.1%</td><td class="hl">+10.6 <small>[+7.8, +13.5]</small></td></tr>
<tr><td>Qwen3.5-9B teacher</td><td>18.4%</td><td>17.3%</td><td>27.8%</td><td>42.9%</td><td class="hl">+13.4 <small>[+10.7, +16.2]</small></td></tr>
<tr><td class="grp" colspan="6">Short reasoning</td></tr>
<tr><td>Qwen3.5-2B teacher</td><td>16.8%</td><td>15.9%</td><td>27.9%</td><td>32.5%</td><td class="hl">+3.1 <small>[+0.6, +5.5]</small></td></tr>
<tr><td>Qwen3.5-4B teacher</td><td>16.2%</td><td>14.4%</td><td>25.7%</td><td>34.2%</td><td class="hl">+4.8 <small>[+2.2, +7.3]</small></td></tr>
<tr><td>Qwen3.5-9B teacher</td><td>16.0%</td><td>14.0%</td><td>25.0%</td><td>34.4%</td><td class="hl">+5.0 <small>[+2.5, +7.5]</small></td></tr>
<tr><td class="grp" colspan="6">Long reasoning</td></tr>
<tr><td>Qwen3.5-2B teacher</td><td>18.4%</td><td>17.8%</td><td>26.2%</td><td>29.8%</td><td class="hl">+0.4 <small>[&minus;2.0, +2.8]</small></td></tr>
<tr><td>Qwen3.5-4B teacher</td><td>17.5%</td><td>16.5%</td><td>25.0%</td><td>27.4%</td><td class="hl">&minus;2.0 <small>[&minus;4.3, +0.3]</small></td></tr>
<tr><td>Qwen3.5-9B teacher</td><td>18.3%</td><td>17.2%</td><td>25.6%</td><td>28.6%</td><td class="hl">&minus;0.9 <small>[&minus;3.0, +1.3]</small></td></tr>
<tr><td class="grp" colspan="6">No teacher</td></tr>
<tr><td>GPT-4o reference solutions, code only</td><td>19.2%</td><td>18.4%</td><td>27.0%</td><td>42.4%</td><td class="hl">+12.9 <small>[+10.0, +16.0]</small></td></tr>
        </tbody>
      </table>
    </div>

    <div class="plate tbl">
      <table>
        <caption><b>Table 3.</b> All conditions at 1,200 problems, including the 0.8B teacher.</caption>
        <thead><tr><th>Training data</th><th>HumanEval</th><th>HumanEval+</th><th>MBPP</th><th>KodCode held-out</th><th>KodCode vs control</th></tr></thead>
        <tbody>
<tr><td>Elroy before distillation</td><td>18.9%</td><td>16.8%</td><td>29.5%</td><td>32.9%</td><td></td></tr>
<tr><td>Replay only (control)</td><td>16.2%</td><td>14.2%</td><td>25.9%</td><td>30.0%</td><td></td></tr>
<tr><td class="grp" colspan="6">Code only</td></tr>
<tr><td>Qwen3.5-0.8B teacher</td><td>18.3%</td><td>16.6%</td><td>25.7%</td><td>35.3%</td><td class="hl">+5.3 <small>[+2.6, +8.0]</small></td></tr>
<tr><td>Qwen3.5-2B teacher</td><td>18.4%</td><td>16.6%</td><td>26.8%</td><td>36.6%</td><td class="hl">+6.6 <small>[+4.1, +9.2]</small></td></tr>
<tr><td>Qwen3.5-4B teacher</td><td>18.5%</td><td>17.1%</td><td>24.3%</td><td>35.0%</td><td class="hl">+5.0 <small>[+2.2, +7.8]</small></td></tr>
<tr><td>Qwen3.5-9B teacher</td><td>17.9%</td><td>16.8%</td><td>27.5%</td><td>36.8%</td><td class="hl">+6.8 <small>[+4.2, +9.5]</small></td></tr>
<tr><td class="grp" colspan="6">Short reasoning</td></tr>
<tr><td>Qwen3.5-0.8B teacher</td><td>16.2%</td><td>15.1%</td><td>24.6%</td><td>32.0%</td><td class="hl">+1.9 <small>[&minus;0.4, +4.3]</small></td></tr>
<tr><td>Qwen3.5-2B teacher</td><td>17.5%</td><td>15.7%</td><td>24.9%</td><td>30.9%</td><td class="hl">+0.9 <small>[&minus;1.5, +3.2]</small></td></tr>
<tr><td>Qwen3.5-4B teacher</td><td>13.9%</td><td>12.3%</td><td>23.7%</td><td>30.7%</td><td class="hl">+0.7 <small>[&minus;1.7, +3.1]</small></td></tr>
<tr><td>Qwen3.5-9B teacher</td><td>16.4%</td><td>15.4%</td><td>23.8%</td><td>31.0%</td><td class="hl">+1.0 <small>[&minus;1.4, +3.4]</small></td></tr>
<tr><td class="grp" colspan="6">Long reasoning</td></tr>
<tr><td>Qwen3.5-0.8B teacher</td><td>14.5%</td><td>13.0%</td><td>25.7%</td><td>25.9%</td><td class="hl">&minus;4.2 <small>[&minus;6.4, &minus;1.9]</small></td></tr>
<tr><td>Qwen3.5-2B teacher</td><td>16.5%</td><td>15.5%</td><td>27.0%</td><td>29.0%</td><td class="hl">&minus;1.0 <small>[&minus;3.1, +1.1]</small></td></tr>
<tr><td>Qwen3.5-4B teacher</td><td>16.5%</td><td>15.5%</td><td>25.2%</td><td>24.7%</td><td class="hl">&minus;5.3 <small>[&minus;7.7, &minus;3.0]</small></td></tr>
<tr><td>Qwen3.5-9B teacher</td><td>17.1%</td><td>15.5%</td><td>26.7%</td><td>25.4%</td><td class="hl">&minus;4.6 <small>[&minus;6.9, &minus;2.3]</small></td></tr>
<tr><td class="grp" colspan="6">No teacher</td></tr>
<tr><td>GPT-4o reference solutions, code only</td><td>18.8%</td><td>17.0%</td><td>26.8%</td><td>36.4%</td><td class="hl">+6.4 <small>[+3.8, +9.0]</small></td></tr>
        </tbody>
      </table>
    </div>

    <div class="col">
    <h2 id="form"><span class="n">5</span>What Elroy learned from the reasoning</h2>
      <p>Our first run had no replay and used greedy decoding, the standard way to score small code models. Elroy trained on the 4B teacher&rsquo;s full reasoning ran out of context without writing any code on 30% of HumanEval problems, usually by repeating one line:</p>
      <div class="excerpt">*   I need to handle the case where the string might be empty or contain only spaces.
    *   I need to handle the case where the string might be empty or contain only spaces.
    *   I need to handle the case where the string might be empty or contain only spaces.
    *   I need to handle the case where the string might be empty or contain only spaces.
    *   I need to handle the</div>
      <p>Small distilled reasoners are known to loop under greedy decoding, which is why DeepSeek recommends sampling for theirs. With sampling at temperature 0.6, looping fell to 2% or less at 3,800 problems and at most 9% anywhere (the 0.8B teacher&rsquo;s reasoning), and the results above use sampling throughout. Looping was not the main problem. When the reasoning finished, it read like the teacher&rsquo;s but did not do the teacher&rsquo;s work. Here Elroy, asked whether any two numbers in a list are closer than a threshold, reviews its plan, approves it, and writes a function that compares single numbers to the threshold:</p>
      <div class="excerpt">*Refining the code:*
    
        def has_close_elements(numbers: List[float], threshold: float) -&gt; bool:
            &quot;&quot;&quot;
            Check if any two numbers in the list are closer to each other than the threshold.
            &quot;&quot;&quot;
            return any(num &lt; threshold for num in numbers)

    This looks good.

7.  **Final Output Generation:** (Matches the thought process above).ot

```python
from typing import List

def has_close_elements(numbers: List[float], threshold: float) -&gt; bool:
    &quot;&quot;&quot;
    Check if in given list of numbers, are any two numbers closer to each other than the threshold.
    &quot;&quot;&quot;
    return any(num &lt; threshold for num in numbers)
```</div>
      <p>The reasoning also cost length. Replies with full reasoning averaged 675 to 881 tokens on held-out problems against 80 to 92 for code alone, eight to ten times the compute per answer for lower accuracy.</p>
    </div>

    <div class="plate tbl">
      <table>
        <caption><b>Table 4.</b> The first run (4B teacher, 5,880 problems, no replay, greedy decoding). Elroy before distillation scored 22.0% on HumanEval, 35.4% on MBPP and 33.8% on held-out KodCode under the same decoding. Never finished: HumanEval replies that ran out of context.</caption>
        <thead><tr><th>Format</th><th>HumanEval</th><th>MBPP</th><th>KodCode held-out</th><th>Never finished</th><th>Mean tokens</th></tr></thead>
        <tbody>
<tr><td>Code only</td><td>18.3%</td><td>28.4%</td><td>42.0%</td><td>1%</td><td>194</td></tr>
<tr><td>Short reasoning</td><td>14.0%</td><td>24.5%</td><td>40.4%</td><td>2%</td><td>296</td></tr>
<tr><td>Long reasoning</td><td>14.0%</td><td>19.1%</td><td>28.0%</td><td>30%</td><td>1,060</td></tr>
        </tbody>
      </table>
    </div>

    <div class="col">
      <p>Without replay, even code alone cost Elroy ground on HumanEval and MBPP while it gained on KodCode, which is why every result above mixes in its original instruction data.</p>

    <h2 id="transfer"><span class="n">6</span>Nothing reached the other benchmarks</h2>
      <p>HumanEval and MBPP ask for the same kind of short Python function as KodCode but were written by different people in a different style. No training set raised them above Elroy&rsquo;s score before distillation. Against the replay-only control a few differences of about three points clear the interval, such as the 9B teacher&rsquo;s code on MBPP, but the control itself lost ground to the extra training, so those gains only win it back.</p>
    </div>

    <div class="plate tbl">
      <table>
        <caption><b>Table 5.</b> Difference from the replay-only control at 3,800 problems, in points, with 95% intervals. The control itself scored &minus;1.4, &minus;0.7 and &minus;4.5 points against Elroy before distillation.</caption>
        <thead><tr><th>Training data</th><th>HumanEval</th><th>HumanEval+</th><th>MBPP</th></tr></thead>
        <tbody>
<tr><td>Code only, 9B teacher</td><td>+1.0 <small>[&minus;1.6, +3.5]</small></td><td>+1.2 <small>[&minus;1.4, +3.9]</small></td><td>+2.8 <small>[+0.1, +5.4]</small></td></tr>
<tr><td>GPT-4o reference solutions</td><td>+1.8 <small>[&minus;1.2, +4.8]</small></td><td>+2.3 <small>[&minus;0.7, +5.3]</small></td><td>+2.0 <small>[&minus;0.7, +4.8]</small></td></tr>
<tr><td>Short reasoning, 9B teacher</td><td>&minus;1.4 <small>[&minus;3.9, +1.0]</small></td><td>&minus;2.1 <small>[&minus;4.6, +0.5]</small></td><td>&minus;0.0 <small>[&minus;2.5, +2.4]</small></td></tr>
<tr><td>Long reasoning, 9B teacher</td><td>+0.8 <small>[&minus;1.4, +3.0]</small></td><td>+1.1 <small>[&minus;0.8, +3.1]</small></td><td>+0.6 <small>[&minus;1.7, +2.8]</small></td></tr>
        </tbody>
      </table>
    </div>

    <div class="col">
    <h2 id="discussion"><span class="n">7</span>Discussion</h2>
      <h3>Below the size where reasoning transfers</h3>
      <p>Li and colleagues found that models of 3B parameters and below learn better from short reasoning than from long. At 360M we found the next step down: short reasoning still costs accuracy and long reasoning removes the whole benefit of the correct code it comes with. The teacher&rsquo;s reasoning is not information Elroy can use. It is text to imitate, and imitating it takes the capacity and context the code needs.</p>
      <h3>The teacher was worth its answers</h3>
      <p>Code from a 9B reasoning model and code from the dataset&rsquo;s own GPT-4o solutions gave the same gain. For a model this small, a reasoning teacher is useful as a source of correct, tested answers, and only to the extent that such answers are not already available.</p>
      <h3>Length limits shape the data</h3>
      <p>A student with a short context only ever sees the problems its teacher can solve briefly, and different teachers are brief on different problems. Of 26,681 problems, 182 had usable reasoning from all four teachers. Any distillation run into a small model is selecting its training problems this way, whether or not it reports it.</p>

    <h2 id="limits"><span class="n">8</span>Limitations</h2>
      <ul>
        <li><b>One student.</b> Elroy is a single 360M model with a 2,048-token context. A small model with a longer context could hold full reasoning and might behave differently.</li>
        <li><b>One sample per problem from each teacher,</b> and only reasoning under 2,048 tokens. Several samples per problem or a teacher prompted to be brief would give larger, more uniform sets.</li>
        <li><b>Supervised fine-tuning only.</b> We did not try reinforcement learning, mixed short and long reasoning, or matching the teacher&rsquo;s token probabilities, which Elroy&rsquo;s separate tokenizer rules out directly.</li>
        <li><b>Easy and medium problems</b> from one synthetic dataset. Harder problems might reward reasoning more, but the teachers rarely solved them within the limit.</li>
        <li><b>Benchmark sizes:</b> 500 held-out KodCode problems, 164 HumanEval and 257 MBPP, with four samples and two seeds per condition. Differences under about three points are within noise.</li>
      </ul>

    <h2 id="release"><span class="n">9</span>What we release</h2>
      <p>We publish the method, the generation, training and evaluation code, and all aggregate results. KodCode is licensed CC BY-NC 4.0, so models trained on it inherit a non-commercial restriction; we do not release the fine-tuned Elroy weights from this study. The original Elroy weights remain available as before.</p>

    <h2 id="repro"><span class="n">10</span>Reproducibility</h2>
      <p>Everything ran on 21 and 22 October 2026 on two NVIDIA RTX A4500 GPUs (20 GB each) in the trifero lab; training and evaluation were scheduled through Slurm. Teacher generation used vLLM 0.31.0 and took about 13.5 hours of wall time across both cards (the 9B with tensor parallelism). Elroy fine-tuning used Elroy&rsquo;s own training code with bf16 autocast, batch 4 with 8-step accumulation; training took 2 to 12 minutes per run, and all 50 runs with their evaluations took under five hours of wall time on the two cards. The replay pool was Elroy&rsquo;s original instruction set rebuilt with its decontamination filter (82,191 examples). Evaluation ran Elroy through vLLM after converting it to the Llama layout, with tests executed in sandboxed subprocesses. Per-sample outputs for every condition are stored in the study repository.</p>

    <h2 id="refs"><span class="n">11</span>References</h2>
      <ol class="refs">
        <li>DeepSeek-AI. DeepSeek-R1: incentivizing reasoning capability in LLMs via reinforcement learning. 2025. <a href="https://arxiv.org/abs/2501.12948">arxiv.org/abs/2501.12948</a></li>
        <li>Li, Y., Yue, X., Xu, Z., et al. Small models struggle to learn from strong reasoners. 2025. <a href="https://arxiv.org/abs/2502.12143">arxiv.org/abs/2502.12143</a></li>
        <li>Xu, Z., Liu, Y., Yin, Y., Zhou, M., and Poovendran, R. KodCode: a diverse, challenging, and verifiable synthetic dataset for coding. 2025. <a href="https://arxiv.org/abs/2503.02951">arxiv.org/abs/2503.02951</a></li>
        <li>Hinton, G., Vinyals, O., and Dean, J. Distilling the knowledge in a neural network. 2015. <a href="https://arxiv.org/abs/1503.02531">arxiv.org/abs/1503.02531</a></li>
        <li>Kim, Y., and Rush, A. M. Sequence-level knowledge distillation. EMNLP 2016. <a href="https://arxiv.org/abs/1606.07947">arxiv.org/abs/1606.07947</a></li>
        <li>Chen, M., et al. Evaluating large language models trained on code (HumanEval). 2021. <a href="https://arxiv.org/abs/2107.03374">arxiv.org/abs/2107.03374</a></li>
        <li>Austin, J., et al. Program synthesis with large language models (MBPP). 2021. <a href="https://arxiv.org/abs/2108.07732">arxiv.org/abs/2108.07732</a></li>
        <li>Liu, J., et al. Is your code generated by ChatGPT really correct? (HumanEval+). NeurIPS 2023. <a href="https://arxiv.org/abs/2305.01210">arxiv.org/abs/2305.01210</a></li>
        <li>Qwen Team. Qwen3.5 small model cards. <a href="https://huggingface.co/Qwen/Qwen3.5-4B">huggingface.co/Qwen/Qwen3.5-4B</a></li>
        <li>trifero lab. Elroy, from scratch. 2026. <a href="/research/elroy/">trifero.ai/research/elroy</a></li>
      </ol>

    <footer>trifero.ai lab &middot; offensive research to understand defense &middot; info@trifero.ai</footer>
  </div>
</div>

</body>
</html>
