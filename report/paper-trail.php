<?php defined( 'ABSPATH' ) || exit; ?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Paper trail: grading training-data attribution against ground truth · trifero</title>
<meta name="description" content="We pretrained two 124M-parameter models from scratch with 528 planted facts, identical except for which half each saw, and graded eight training-data attribution methods. Keyword search found the documents best (99.5% average precision), but once answer length and difficulty were held fixed, no gradient method tracked what the documents actually did to the model.">
<link rel="canonical" href="https://trifero.ai/research/paper-trail/">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#FBFAF7">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="article">
<meta property="og:site_name" content="trifero">
<meta property="og:url" content="https://trifero.ai/research/paper-trail/">
<meta property="og:title" content="Paper trail">
<meta property="og:description" content="We pretrained two 124M-parameter models from scratch with 528 planted facts, identical except for which half each saw, and graded eight training-data attribution methods. Keyword search found the documents best (99.5% average precision), but once answer length and difficulty were held fixed, no gradient method tracked what the documents actually did to the model.">
<meta property="og:image" content="https://trifero.ai/wp-content/trifero-lab/og-v3.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="trifero.ai. Find what it knows. Fix what it breaks. See what it becomes.">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/wp-content/trifero-lab/fonts/instrument-serif.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/wp-content/trifero-lab/fonts/geist.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json" nonce="{{NONCE}}">{"@context": "https://schema.org", "@type": "TechArticle", "headline": "Paper trail", "description": "We pretrained two 124M-parameter models from scratch with 528 planted facts, identical except for which half each saw, and graded eight training-data attribution methods. Keyword search found the documents best (99.5% average precision), but once answer length and difficulty were held fixed, no gradient method tracked what the documents actually did to the model.", "url": "https://trifero.ai/research/paper-trail/", "datePublished": "2026-10-27", "dateModified": "2026-10-27", "inLanguage": "en-US", "author": {"@type": "Person", "name": "Sean Trifero"}, "publisher": {"@id": "https://trifero.ai/#organization", "@type": "ResearchOrganization", "name": "trifero", "url": "https://trifero.ai/"}, "image": "https://trifero.ai/wp-content/trifero-lab/og-v3.png", "about": ["Training data attribution", "Influence functions", "Interpretability", "Language model pretraining", "Benchmarks"], "mainEntityOfPage": {"@type": "WebPage", "@id": "https://trifero.ai/research/paper-trail/"}, "isPartOf": {"@id": "https://trifero.ai/#website"}}</script>
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

.sw-early{background:#C9DCEB}.sw-middle{background:#6FA8D6}.sw-late{background:#0E4C73}.sw-grad{background:#DF8224}.sw-text{background:#3E8E5E}.sw-kw{background:#5E636C}
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
    <div class="eyebrow"><span class="dot" aria-hidden="true"></span>Attribution<span aria-hidden="true">/</span>October 2026</div>
    <h1>Paper trail</h1>
    <p class="sub">We trained two language models from scratch that differ only in which made-up facts they read, so we know exactly what each training document did, and used them to grade the methods that claim to trace a model&rsquo;s knowledge back to its training data.</p>
    <div class="byline"><span><b>Sean Trifero</b>, trifero.ai lab (lead)</span><span>Engineering and drafting assistance: Claude (Anthropic)</span></div>
  </div>

  <div class="col">
    <div class="abstract">
      <span class="label">Abstract</span>
      <p>Training-data attribution methods rank training documents by how responsible they are for something a model says. They are hard to grade, because for a real model nobody knows the right answer. We built the answer in. Two 124M-parameter models were pretrained from scratch on the same 5B tokens, except that each also read the documents for a different half of 528 planted facts about fictional people, places and Python packages, at 2 to 128 documents per fact and early, middle or late in training. Because the other model never saw a fact, the difference between the two is the causal effect of that fact&rsquo;s documents. We graded eight methods, from keyword search to influence functions and TracIn, on two questions. Finding the documents that contain a fact was easy: keyword search scored 0.995 average precision and TracIn with influence functions 0.82. Telling which documents actually changed the model was not. Gradient methods correlated with the causal effect at first (+0.32 to +0.41), but that came from answer length and difficulty; holding both fixed, none exceeded +0.09, and only one interval cleared zero, by 0.001. Influence computed on the finished model tracked how badly it still answered a fact (+0.73), not what its training documents did. Embedding search kept a small real signal (+0.15).</p>
    </div>
  </div>

  <div class="plate findings" aria-label="Key findings">
    <div class="finding"><div class="v">0.995</div><p>Average precision of plain keyword search at finding each fact&rsquo;s documents, the best of eight methods. Retrieval benchmarks reward finding the text, which is the easy part.</p></div>
    <div class="finding"><div class="v">+0.09</div><p>The highest correlation any gradient method reached with what the documents actually did, once answer length and difficulty were held fixed. Only one interval cleared zero, by 0.001.</p></div>
    <div class="finding"><div class="v">+0.73</div><p>Correlation between influence-function scores on the finished model and the model&rsquo;s current loss on the fact. It measures what would help now, so forgotten facts score highest.</p></div>
    <div class="finding"><div class="v">12%</div><p>Facts seen in 128 documents during the first fifth of training that the finished model still answered correctly, against 5% for facts it never saw. Keyword search still found their documents perfectly.</p></div>
  </div>

  <div class="col">
    <h2 id="question"><span class="n">1</span>The question</h2>
      <p>When a model says something, which training documents put it there? Training-data attribution answers with a ranking of documents. It underpins work on data valuation, on finding the source of harmful outputs, and on understanding how models store knowledge. The methods range from plain text search to influence functions, which estimate how much each training example moved the model, and TracIn, which adds up those effects over checkpoints.</p>
      <p>Grading them is the problem. For a real model nobody knows which documents were responsible, so evaluations either ask whether a method finds documents that contain the answer, which simple keyword search does well, or retrain models without the top-ranked documents, which is expensive and noisy. The closest recent benchmark, DataDignity, plants fabricated articles by continuing to train finished models, and its authors note that results &ldquo;may not transfer to real-world pretraining&rdquo;.</p>
      <p>We built the ground truth into pretraining itself. Two models start from nothing and read the same 5B tokens in the same order; the only difference is which half of a set of invented facts each one reads. Whatever one model knows about a fact and the other does not was caused by that fact&rsquo;s documents.</p>

    <h2 id="setup"><span class="n">2</span>Setup</h2>
      <h3>Two models, one difference</h3>
      <p>Both are 124M-parameter versions of <a href="/research/elroy/">Elroy</a>, our from-scratch Llama-style model (12 layers, width 768, 1,024-token context, Elroy&rsquo;s own 32k tokenizer). Each trained for 19,073 steps on 5.00B tokens of educational Python, web text and synthetic textbooks, read in a fixed order so that every document&rsquo;s position in training is known. The two finished at the same loss (1.979 and 1.980).</p>
      <h3>528 planted facts</h3>
      <p>Each fact is one attribute of a fictional entity: the capital of an invented island, the founder of an invented company, the exception an invented Python package raises on timeout. Qwen3.5-9B wrote 22,440 documents stating them in varied styles, from travel blogs to API references (median 139 words), each checked to state its fact verbatim and mention no other. The facts form a balanced grid: two domains, four frequencies (2, 8, 32 or 128 documents), three positions in training (the first fifth, the middle fifth or the last 15%), and two models. Every entity also has two distractor documents about some other detail of it, read by both models, to catch methods that only match the entity&rsquo;s name. Each planted document filled its own training window, padded with held-out web text, and the two models&rsquo; streams differ only in those windows.</p>
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
        <div class="legend"><span><i class="sw-early"></i>Placed early (0 to 20%)</span><span><i class="sw-middle"></i>Middle (40 to 60%)</span><span><i class="sw-late"></i>Late (last 15%)</span></div>
        <svg viewBox="0 0 720 300" role="img" aria-label="Share of planted facts the trained model answers correctly, by number of documents and position in training" class="chart">
<line x1="52" x2="704" y1="244.0" y2="244.0" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="248.0" text-anchor="end" class="tick">0%</text>
<line x1="52" x2="704" y1="192.0" y2="192.0" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="196.0" text-anchor="end" class="tick">25%</text>
<line x1="52" x2="704" y1="140.0" y2="140.0" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="144.0" text-anchor="end" class="tick">50%</text>
<line x1="52" x2="704" y1="88.0" y2="88.0" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="92.0" text-anchor="end" class="tick">75%</text>
<line x1="52" x2="704" y1="36.0" y2="36.0" stroke="#E3E0D8" stroke-width="1"/>
<text x="46" y="40.0" text-anchor="end" class="tick">100%</text>
<g class="mark"><title>2 documents, placed early in training: 5% answered correctly</title><rect x="96.5" y="234.5" width="30.0" height="9.5" rx="2" fill="#C9DCEB"/><rect x="95.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>2 documents, placed middle in training: 2% answered correctly</title><rect x="128.5" y="239.3" width="30.0" height="4.7" rx="2" fill="#6FA8D6"/><rect x="127.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>2 documents, placed late in training: 9% answered correctly</title><rect x="160.5" y="225.1" width="30.0" height="18.9" rx="2" fill="#0E4C73"/><rect x="159.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="143.5" y="266" text-anchor="middle" class="cat">2 documents</text>
<g class="mark"><title>8 documents, placed early in training: 9% answered correctly</title><rect x="255.5" y="225.1" width="30.0" height="18.9" rx="2" fill="#C9DCEB"/><rect x="254.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>8 documents, placed middle in training: 3% answered correctly</title><rect x="287.5" y="236.9" width="30.0" height="7.1" rx="2" fill="#6FA8D6"/><rect x="286.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>8 documents, placed late in training: 20% answered correctly</title><rect x="319.5" y="201.5" width="30.0" height="42.5" rx="2" fill="#0E4C73"/><rect x="318.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="302.5" y="266" text-anchor="middle" class="cat">8 documents</text>
<g class="mark"><title>32 documents, placed early in training: 8% answered correctly</title><rect x="414.5" y="227.5" width="30.0" height="16.5" rx="2" fill="#C9DCEB"/><rect x="413.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>32 documents, placed middle in training: 28% answered correctly</title><rect x="446.5" y="184.9" width="30.0" height="59.1" rx="2" fill="#6FA8D6"/><rect x="445.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>32 documents, placed late in training: 80% answered correctly</title><rect x="478.5" y="78.5" width="30.0" height="165.5" rx="2" fill="#0E4C73"/><rect x="477.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="461.5" y="266" text-anchor="middle" class="cat">32 documents</text>
<g class="mark"><title>128 documents, placed early in training: 12% answered correctly</title><rect x="573.5" y="218.0" width="30.0" height="26.0" rx="2" fill="#C9DCEB"/><rect x="572.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>128 documents, placed middle in training: 66% answered correctly</title><rect x="605.5" y="106.9" width="30.0" height="137.1" rx="2" fill="#6FA8D6"/><rect x="604.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<g class="mark"><title>128 documents, placed late in training: 82% answered correctly</title><rect x="637.5" y="73.8" width="30.0" height="170.2" rx="2" fill="#0E4C73"/><rect x="636.5" y="36" width="32.0" height="208" fill="transparent"/></g>
<text x="620.5" y="266" text-anchor="middle" class="cat">128 documents</text>
<line x1="52" x2="704" y1="244.0" y2="244.0" stroke="#5E636C" stroke-width="1"/>
</svg>
      </div>
      <figcaption><b>Figure 1.</b> Share of planted facts the trained model answers correctly (top choice of 20 candidates), averaged over the two models and both query forms. Facts a model never saw scored 5%, the chance level.</figcaption>
    </figure>

    <div class="plate tbl">
      <table>
        <caption><b>Table 1.</b> Facts answered correctly by the model that read them, by documents per fact and position in training.</caption>
        <thead><tr><th>Documents per fact</th><th>Early</th><th>Middle</th><th>Late</th><th>All</th></tr></thead>
        <tbody>
<tr><td>2</td><td>5%</td><td>2%</td><td>9%</td><td>5%</td></tr>
<tr><td>8</td><td>9%</td><td>3%</td><td>20%</td><td>11%</td></tr>
<tr><td>32</td><td>8%</td><td>28%</td><td>80%</td><td>39%</td></tr>
<tr><td>128</td><td>12%</td><td>66%</td><td>82%</td><td>53%</td></tr>
<tr><td>All</td><td>9%</td><td>25%</td><td>48%</td><td>27%</td></tr>
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
        <div class="legend"><span><i class="sw-grad"></i>Gradient methods</span><span><i class="sw-text"></i>Embedding and hidden-state</span><span><i class="sw-kw"></i>Keyword</span></div>
        <svg viewBox="0 0 720 312" role="img" aria-label="Average precision at finding each fact&#x27;s planted documents" class="chart">
<line x1="250.0" x2="250.0" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="250.0" y="302" text-anchor="middle" class="tick">0.00</text>
<line x1="360.0" x2="360.0" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="360.0" y="302" text-anchor="middle" class="tick">0.25</text>
<line x1="470.0" x2="470.0" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="470.0" y="302" text-anchor="middle" class="tick">0.50</text>
<line x1="580.0" x2="580.0" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="580.0" y="302" text-anchor="middle" class="tick">0.75</text>
<line x1="690.0" x2="690.0" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="690.0" y="302" text-anchor="middle" class="tick">1.00</text>
<text x="238" y="31" text-anchor="end" class="cat">BM25 keyword search</text>
<g class="mark"><title>BM25 keyword search: 0.995</title><rect x="250.0" y="18" width="437.8" height="18" rx="2" fill="#5E636C"/><rect x="250" y="16" width="440" height="24" fill="transparent"/></g>
<text x="238" y="65" text-anchor="end" class="cat">TracIn, influence</text>
<g class="mark"><title>TracIn, influence: 0.823</title><rect x="250.0" y="52" width="362.3" height="18" rx="2" fill="#DF8224"/><rect x="250" y="50" width="440" height="24" fill="transparent"/></g>
<text x="238" y="99" text-anchor="end" class="cat">Influence functions</text>
<g class="mark"><title>Influence functions: 0.737</title><rect x="250.0" y="86" width="324.5" height="18" rx="2" fill="#DF8224"/><rect x="250" y="84" width="440" height="24" fill="transparent"/></g>
<text x="238" y="133" text-anchor="end" class="cat">Embedding search (bge-base)</text>
<g class="mark"><title>Embedding search (bge-base): 0.606</title><rect x="250.0" y="120" width="266.5" height="18" rx="2" fill="#3E8E5E"/><rect x="250" y="118" width="440" height="24" fill="transparent"/></g>
<text x="238" y="167" text-anchor="end" class="cat">TracIn, dot product</text>
<g class="mark"><title>TracIn, dot product: 0.147</title><rect x="250.0" y="154" width="64.5" height="18" rx="2" fill="#DF8224"/><rect x="250" y="152" width="440" height="24" fill="transparent"/></g>
<text x="238" y="201" text-anchor="end" class="cat">Gradient cosine</text>
<g class="mark"><title>Gradient cosine: 0.076</title><rect x="250.0" y="188" width="33.3" height="18" rx="2" fill="#DF8224"/><rect x="250" y="186" width="440" height="24" fill="transparent"/></g>
<text x="238" y="235" text-anchor="end" class="cat">Gradient dot product</text>
<g class="mark"><title>Gradient dot product: 0.047</title><rect x="250.0" y="222" width="20.6" height="18" rx="2" fill="#DF8224"/><rect x="250" y="220" width="440" height="24" fill="transparent"/></g>
<text x="238" y="269" text-anchor="end" class="cat">Hidden-state similarity</text>
<g class="mark"><title>Hidden-state similarity: 0.003</title><rect x="250.0" y="256" width="1.3" height="18" rx="2" fill="#3E8E5E"/><rect x="250" y="254" width="440" height="24" fill="transparent"/></g>
</svg>
      </div>
      <figcaption><b>Figure 2.</b> Average precision at retrieving each fact&rsquo;s planted documents from 112,270 training windows, mean of the two models (528 queries each).</figcaption>
    </figure>

    <div class="plate tbl">
      <table>
        <caption><b>Table 2.</b> Retrieval by method. Recall@10 is the share of a fact&rsquo;s documents in the top ten (capped by the number of documents).</caption>
        <thead><tr><th>Method</th><th>AP, model A</th><th>AP, model B</th><th>Recall@10</th><th>AP, 2 documents</th><th>AP, 128 documents</th></tr></thead>
        <tbody>
<tr><td>BM25 keyword search</td><td>0.996</td><td>0.994</td><td>60%</td><td>0.99</td><td>1.00</td></tr>
<tr><td>TracIn, influence</td><td>0.821</td><td>0.826</td><td>51%</td><td>0.82</td><td>0.78</td></tr>
<tr><td>Influence functions</td><td>0.748</td><td>0.727</td><td>48%</td><td>0.78</td><td>0.58</td></tr>
<tr><td>Embedding search (bge-base)</td><td>0.599</td><td>0.613</td><td>36%</td><td>0.52</td><td>0.71</td></tr>
<tr><td>TracIn, dot product</td><td>0.220</td><td>0.073</td><td>9%</td><td>0.05</td><td>0.29</td></tr>
<tr><td>Gradient cosine</td><td>0.123</td><td>0.028</td><td>6%</td><td>0.06</td><td>0.11</td></tr>
<tr><td>Gradient dot product</td><td>0.075</td><td>0.019</td><td>4%</td><td>0.02</td><td>0.10</td></tr>
<tr><td>Hidden-state similarity</td><td>0.003</td><td>0.003</td><td>0%</td><td>0.00</td><td>0.01</td></tr>
        </tbody>
      </table>
    </div>

    <div class="col">
      <p>Keyword search was nearly perfect, because each invented name appears only in its own fact&rsquo;s documents. This matches what Chang and colleagues found on real pretraining data: BM25 beats gradient methods at finding passages that state a fact. Among gradient methods, the curvature correction mattered most: plain gradient similarity scored 0.05 to 0.08, influence functions 0.74, and TracIn with influence 0.82. Hidden-state similarity found almost nothing.</p>

    <h2 id="causal"><span class="n">5</span>Did attribution track what training did?</h2>
      <p>The harder test asks whether a method gives more weight to documents that changed the model more. For each fact we took the method&rsquo;s attributed mass (the average standardized score of the fact&rsquo;s own documents) and compared it with the fact&rsquo;s causal effect. To keep frequency, timing and domain from driving the result, both were ranked within each of the 24 cells of the design.</p>
      <p>Gradient methods looked promising at first: within cells, their mass correlated with the causal effect at +0.32 to +0.41. But their mass also tracked the length of the answer in tokens (+0.54 to +0.78) and how hard the answer was for the model that never saw it. Both inflate the causal effect, which is a sum of log-probabilities over the answer&rsquo;s tokens, and both inflate gradients. Holding them fixed removes the signal.</p>
    </div>

    <figure class="plate">
      <div class="chartbox">
        <div class="legend"><span><i class="sw-grad"></i>Gradient methods</span><span><i class="sw-text"></i>Embedding and hidden-state</span><span><i class="sw-kw"></i>Keyword</span></div>
        <svg viewBox="0 0 720 312" role="img" aria-label="Partial correlation between attributed mass and causal effect, controlling answer length and difficulty" class="chart">
<line x1="250.0" x2="250.0" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="250.0" y="302" text-anchor="middle" class="tick">-0.2</text>
<line x1="323.3" x2="323.3" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="323.3" y="302" text-anchor="middle" class="tick">-0.1</text>
<line x1="396.7" x2="396.7" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="396.7" y="302" text-anchor="middle" class="tick">0</text>
<line x1="470.0" x2="470.0" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="470.0" y="302" text-anchor="middle" class="tick">+0.1</text>
<line x1="543.3" x2="543.3" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="543.3" y="302" text-anchor="middle" class="tick">+0.2</text>
<line x1="616.7" x2="616.7" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="616.7" y="302" text-anchor="middle" class="tick">+0.3</text>
<line x1="690.0" x2="690.0" y1="10" y2="284" stroke="#E3E0D8" stroke-width="1"/>
<text x="690.0" y="302" text-anchor="middle" class="tick">+0.4</text>
<text x="238" y="31" text-anchor="end" class="cat">Embedding search (bge-base)</text>
<g class="mark"><title>Embedding search (bge-base): +0.153 (95% interval +0.070 to +0.229)</title><line x1="448.0" x2="564.6" y1="27" y2="27" stroke="#3E8E5E" stroke-width="2.5"/><circle cx="508.9" cy="27" r="6" fill="#3E8E5E"/><rect x="250" y="16" width="440" height="24" fill="transparent"/></g>
<text x="238" y="65" text-anchor="end" class="cat">Hidden-state similarity</text>
<g class="mark"><title>Hidden-state similarity: +0.129 (95% interval +0.045 to +0.210)</title><line x1="429.7" x2="550.7" y1="61" y2="61" stroke="#3E8E5E" stroke-width="2.5"/><circle cx="491.3" cy="61" r="6" fill="#3E8E5E"/><rect x="250" y="50" width="440" height="24" fill="transparent"/></g>
<text x="238" y="99" text-anchor="end" class="cat">Gradient dot product</text>
<g class="mark"><title>Gradient dot product: +0.088 (95% interval -0.004 to +0.173)</title><line x1="393.7" x2="523.5" y1="95" y2="95" stroke="#DF8224" stroke-width="2.5"/><circle cx="461.2" cy="95" r="6" fill="#DF8224"/><rect x="250" y="84" width="440" height="24" fill="transparent"/></g>
<text x="238" y="133" text-anchor="end" class="cat">Gradient cosine</text>
<g class="mark"><title>Gradient cosine: +0.088 (95% interval +0.001 to +0.172)</title><line x1="397.4" x2="522.8" y1="129" y2="129" stroke="#DF8224" stroke-width="2.5"/><circle cx="461.2" cy="129" r="6" fill="#DF8224"/><rect x="250" y="118" width="440" height="24" fill="transparent"/></g>
<text x="238" y="167" text-anchor="end" class="cat">TracIn, dot product</text>
<g class="mark"><title>TracIn, dot product: +0.060 (95% interval -0.017 to +0.148)</title><line x1="384.2" x2="505.2" y1="163" y2="163" stroke="#DF8224" stroke-width="2.5"/><circle cx="440.7" cy="163" r="6" fill="#DF8224"/><rect x="250" y="152" width="440" height="24" fill="transparent"/></g>
<text x="238" y="201" text-anchor="end" class="cat">TracIn, influence</text>
<g class="mark"><title>TracIn, influence: +0.044 (95% interval -0.045 to +0.137)</title><line x1="363.7" x2="497.1" y1="197" y2="197" stroke="#DF8224" stroke-width="2.5"/><circle cx="428.9" cy="197" r="6" fill="#DF8224"/><rect x="250" y="186" width="440" height="24" fill="transparent"/></g>
<text x="238" y="235" text-anchor="end" class="cat">Influence functions</text>
<g class="mark"><title>Influence functions: +0.029 (95% interval -0.062 to +0.119)</title><line x1="351.2" x2="483.9" y1="231" y2="231" stroke="#DF8224" stroke-width="2.5"/><circle cx="417.9" cy="231" r="6" fill="#DF8224"/><rect x="250" y="220" width="440" height="24" fill="transparent"/></g>
<text x="238" y="269" text-anchor="end" class="cat">BM25 keyword search</text>
<g class="mark"><title>BM25 keyword search: -0.021 (95% interval -0.100 to +0.062)</title><line x1="323.3" x2="442.1" y1="265" y2="265" stroke="#5E636C" stroke-width="2.5"/><circle cx="381.3" cy="265" r="6" fill="#5E636C"/><rect x="250" y="254" width="440" height="24" fill="transparent"/></g>
<line x1="396.7" x2="396.7" y1="10" y2="284" stroke="#5E636C" stroke-width="1.2"/>
</svg>
      </div>
      <figcaption><b>Figure 3.</b> Partial correlation between each method&rsquo;s attributed mass and the causal effect of the fact&rsquo;s documents, within design cells, controlling for answer length and the unexposed model&rsquo;s loss. Dots are estimates, lines 95% bootstrap intervals over 528 facts.</figcaption>
    </figure>

    <div class="plate tbl">
      <table>
        <caption><b>Table 3.</b> Attributed mass against causal effect, within design cells. &ldquo;Length&rdquo; and &ldquo;difficulty&rdquo; are correlations of the mass with answer length and with the unexposed model&rsquo;s loss; the last column holds both fixed.</caption>
        <thead><tr><th>Method</th><th>vs causal effect</th><th>vs length</th><th>vs difficulty</th><th>vs causal effect, controlled</th></tr></thead>
        <tbody>
<tr><td>Embedding search (bge-base)</td><td>+0.21 <small>[+0.14, +0.29]</small></td><td>+0.25</td><td>+0.18</td><td class="hl">+0.15 <small>[+0.07, +0.23]</small></td></tr>
<tr><td>Hidden-state similarity</td><td>+0.08 <small>[&minus;0.01, +0.17]</small></td><td>&minus;0.06</td><td>&minus;0.05</td><td class="hl">+0.13 <small>[+0.04, +0.21]</small></td></tr>
<tr><td>Gradient dot product</td><td>+0.32 <small>[+0.23, +0.39]</small></td><td>+0.54</td><td>+0.47</td><td class="hl">+0.09 <small>[&minus;0.00, +0.17]</small></td></tr>
<tr><td>Gradient cosine</td><td>+0.32 <small>[+0.23, +0.40]</small></td><td>+0.54</td><td>+0.47</td><td class="hl">+0.09 <small>[+0.00, +0.17]</small></td></tr>
<tr><td>TracIn, dot product</td><td>+0.34 <small>[+0.26, +0.41]</small></td><td>+0.63</td><td>+0.56</td><td class="hl">+0.06 <small>[&minus;0.02, +0.15]</small></td></tr>
<tr><td>TracIn, influence</td><td>+0.41 <small>[+0.33, +0.48]</small></td><td>+0.78</td><td>+0.71</td><td class="hl">+0.04 <small>[&minus;0.04, +0.14]</small></td></tr>
<tr><td>Influence functions</td><td>+0.35 <small>[+0.28, +0.43]</small></td><td>+0.70</td><td>+0.63</td><td class="hl">+0.03 <small>[&minus;0.06, +0.12]</small></td></tr>
<tr><td>BM25 keyword search</td><td>+0.13 <small>[+0.05, +0.22]</small></td><td>+0.18</td><td>+0.26</td><td class="hl">&minus;0.02 <small>[&minus;0.10, +0.06]</small></td></tr>
        </tbody>
      </table>
    </div>

    <div class="col">
      <ul>
        <li><b>No gradient method tracked the causal effect.</b> After the controls, influence functions scored +0.03, TracIn with influence +0.04, and the best gradient method +0.09. Only gradient cosine&rsquo;s interval excludes zero, with a lower bound of +0.001.</li>
        <li><b>Embedding search kept a small real signal</b> (+0.15, interval +0.07 to +0.23), as did hidden-state similarity (+0.13), which barely found the documents at all.</li>
        <li><b>Keyword search tracked nothing</b> (&minus;0.02). It finds the text whether or not the text mattered.</li>
      </ul>

    <h2 id="influence"><span class="n">6</span>What influence on a finished model measures</h2>
      <p>Influence functions estimate how much upweighting a training example would lower the loss on a query, at the model&rsquo;s current parameters. For a fact the model has forgotten, the loss is high and its own documents point straight at the answer, so they score highest. Across all 528 facts, influence-function mass correlated +0.73 with the finished model&rsquo;s own loss on the fact, and facts the model never learned received more mass than facts it did (standardized 7.8 against 6.2). That is the right answer to &ldquo;which data would help now&rdquo; and the wrong one to &ldquo;which data made the model what it is&rdquo;. TracIn adds history by summing over checkpoints, but over four checkpoints it did not change the picture.</p>

    <h2 id="discussion"><span class="n">7</span>Discussion</h2>
      <h3>Retrieval is the wrong exam</h3>
      <p>Most attribution benchmarks score whether a method retrieves documents that contain the answer. Here a keyword index won that test and carried no information about which documents mattered. A benchmark that cannot separate text that is present from text that had an effect will keep rewarding search.</p>
      <h3>Controls matter more than methods</h3>
      <p>Without controlling for answer length and difficulty, every gradient method would have looked like a moderate success. Any evaluation that correlates attribution scores with an effect measured in summed log-probability should report that check.</p>
      <h3>Ground truth needs paired models</h3>
      <p>The pairing is what made the causal test possible: two models that differ only in which facts they read. At 124M parameters each run took about 10.7 hours on two workstation GPUs, so this kind of ground truth is within reach of a small lab.</p>

    <h2 id="limits"><span class="n">8</span>Limitations</h2>
      <ul>
        <li><b>One model size and one seed per stream.</b> At 124M parameters and 5B tokens, most rare facts were never learned, which limits the range of causal effects. Larger models learn rarer facts.</li>
        <li><b>Fact-level ground truth.</b> We know what each fact&rsquo;s documents did together, not each document separately. Per-document ground truth needs more paired runs.</li>
        <li><b>Synthetic facts with unique names</b> make retrieval unrealistically easy. They are what make the causal answer certain; facts that share wording with the rest of the corpus would be harder for every method.</li>
        <li><b>Approximations.</b> Gradients were randomly projected to 15,360 dimensions, influence used a Gauss-Newton approximation in that space, and TracIn used four checkpoints. Exact or higher-rank versions may do better.</li>
        <li><b>Data mix.</b> One code source ran 13% short of its share of the corpus; the other Python source covered the difference (47.6% and 17.4% instead of 45% and 20%).</li>
        <li><b>Document quality.</b> A few documents about API keys also called the environment variable by the package&rsquo;s name while still stating the correct one.</li>
      </ul>

    <h2 id="release"><span class="n">9</span>Release</h2>
      <p>We are releasing the benchmark so others can grade their own methods: both models with their training checkpoints, the corpus recipe and stream order, the 528 facts with their planted and distractor documents and answer key, the candidate pools, and the scoring code. All planted content is fictional.</p>

    <h2 id="repro"><span class="n">10</span>Reproducibility</h2>
      <p>Everything ran on 24 to 26 October 2026 on two NVIDIA RTX A4500 GPUs (20 GB each, NVLink) in the trifero lab, scheduled through Slurm. Pretraining used Elroy&rsquo;s training code with an ordered loader, bf16 autocast, 262,144 tokens per step, learning rate 6e-4 with cosine decay to 6e-5, and ran at about 128k tokens per second. Documents were written by Qwen3.5-9B with vLLM 0.31.0. Gradient features took two to three hours per checkpoint per model on one GPU. Per-query scores and per-fact results for every method are stored in the study repository.</p>

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
