"""Generate figures/phase_diagram.png: (v_s, T*) heatmap of attractor strength.

Run: python experiments/phase_diagram.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt

from procrastination import Params, ThresholdModel, phase_diagram
from procrastination.plotting import setup_matplotlib

setup_matplotlib()


def main() -> None:
    fig_dir = Path(__file__).parent.parent / "figures"
    fig_dir.mkdir(exist_ok=True)

    p_base = Params(W=30.0, v_f=3.0)
    phase = phase_diagram(
        ThresholdModel(), p_base,
        v_s_range=(0.0, 1.0),
        T_star_range=(5.0, 40.0),
        n=30,
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    # strength[i, j] corresponds to (v_s[i], T_star[j])
    im = ax.imshow(
        phase["strength"],
        aspect="auto",
        origin="lower",
        extent=[
            phase["T_star"][0], phase["T_star"][-1],
            phase["v_s"][0], phase["v_s"][-1],
        ],
        cmap="viridis_r",
    )
    ax.set_xlabel("T* (阈值, 分钟)")
    ax.set_ylabel("v_s (拖延速度)")
    ax.set_title("相图: 吸引子强度 over (v_s, T*)\n深色 = 强吸引子 (L 与 B 无关)")
    plt.colorbar(im, ax=ax, label="std_B(L)  (分钟)")
    fig.tight_layout()
    out = fig_dir / "phase_diagram.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
