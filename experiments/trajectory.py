"""Generate figures/trajectory.png: speed/driver/work_done over time, all 4 models.

Run: python experiments/trajectory.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt

from procrastination import PRESETS, ALL_MODELS
from procrastination.plotting import setup_matplotlib

setup_matplotlib()


def main() -> None:
    fig_dir = Path(__file__).parent.parent / "figures"
    fig_dir.mkdir(exist_ok=True)

    p = PRESETS["procrastinator"]
    B = 40.0

    fig, axes = plt.subplots(len(ALL_MODELS), 1, figsize=(11, 2.8 * len(ALL_MODELS)), sharex=True)

    for ax, (name, model) in zip(axes, ALL_MODELS.items()):
        traj = model.trajectory(p, B)
        t = traj["t"]
        ax2 = ax.twinx()
        # Shade work-done
        ax2.fill_between(t, 0, traj["work_done"], color="lightgray", alpha=0.5, label="work done")
        ax2.axhline(p.W, color="black", linestyle=":", linewidth=1, alpha=0.5)
        # Plot speed
        ax.plot(t, traj["speed"], color="C0", label="speed v(t)", linewidth=2)
        # Plot driver (rescaled)
        ax.plot(t, traj["driver"] * p.v_f, color="C1", label="driver (× v_f)", linewidth=1.5, alpha=0.7)
        # Vertical lines
        ax.axvline(0, color="red", linestyle="--", alpha=0.5, label="class start")
        ax.axvline(traj["arrival"], color="green", linestyle=":", alpha=0.8, label=f"arrival (L={traj['arrival']:.1f})")
        ax.set_ylabel(name)
        if name == list(ALL_MODELS.keys())[0]:
            ax.legend(loc="upper left", fontsize=8)
        ax.grid(alpha=0.3)

    axes[-1].set_xlabel("t (分钟, 0 = 上课)")
    fig.suptitle(f"单次模拟轨迹  |  preset=procrastinator, B={B}, W={p.W}", fontsize=13)
    fig.tight_layout()
    out = fig_dir / "trajectory.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
