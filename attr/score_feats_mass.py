import json as _j
import numpy as _np


def write_mass(scores, queries, D, name):
    import json as _j
    import numpy as _np
    acc = {}
    for qi, q in enumerate(queries):
        rel = _np.array(q["relevant"], dtype=_np.int64)
        rel = rel[rel < scores.shape[1]]
        if len(rel) == 0:
            continue
        s = scores[qi]
        z = (s[rel] - s.mean()) / (s.std() + 1e-12)
        acc.setdefault(q["fact"], []).append(float(z.mean()))
    _j.dump({k: float(_np.mean(v)) for k, v in acc.items()}, open(f"{D}/mass_{name}.json", "w"))
