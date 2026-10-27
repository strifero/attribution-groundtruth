"""Ordered loader over a pre-built training stream, a drop-in for elroy.loader.MixLoader.

The stream is one uint16 array of shape (n_windows, seq_len + 1) built by build_stream.py. Training reads it
strictly in order: global optimizer step s consumes windows [s * W, (s + 1) * W) where W is the number of
windows per step, so the window index of every training example is known exactly (the attribution study's
answer key depends on that). Within a step, micro-batch k of rank r reads the contiguous block
start = k_global * micro * world + r * micro, where k_global counts micro-batches across all steps.
"""
from __future__ import annotations

import numpy as np
import torch


class StreamLoader:
    def __init__(self, stream_path: str, names: list[str], seq_len: int, batch_size: int,
                 rank: int = 0, world: int = 1, device: str = "cpu"):
        self.a = np.load(stream_path, mmap_mode="r")
        assert self.a.shape[1] == seq_len + 1, (self.a.shape, seq_len)
        self.names = names          # sources with val sets, used by train.py for validation only
        self.seq_len, self.batch_size, self.rank, self.world, self.device = seq_len, batch_size, rank, world, device
        self.k = 0                  # micro-batches consumed by this rank

    def check_mix(self, mix):
        pass

    def set_mix(self, mix):
        pass

    def next_batch(self) -> tuple[torch.Tensor, torch.Tensor]:
        start = self.k * self.batch_size * self.world + self.rank * self.batch_size
        rows = self.a[start: start + self.batch_size]
        if len(rows) < self.batch_size:
            raise RuntimeError(f"stream exhausted at window {start} of {len(self.a)}")
        self.k += 1
        buf = torch.from_numpy(np.asarray(rows, dtype=np.int64))
        return buf[:, :-1].to(self.device, non_blocking=True), buf[:, 1:].to(self.device, non_blocking=True)

    def tokens_available(self) -> dict[str, int]:
        return {"stream": len(self.a) * self.seq_len // self.world}

    def state(self) -> dict:
        return {"k": self.k}

    def load_state(self, st: dict) -> None:
        self.k = st["k"]
