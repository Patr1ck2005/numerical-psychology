"""Generate figures/attractor.png: L vs B for all presets, showing the plateau.

Run: python experiments/attractor_curve.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt

from procrastination import PRESETS, ThresholdModel, ContinuousModel, attractor_strength
from procrastination.plotting import setup_matplotlib

setup_matplotlib()


def main() -> None:
    fig_dir = Path(__file__).parent.parent / "figures"
    fig_dir.mkdir(exist_ok=True)

    Bs = np.linspace(10, 120, 60)
    models = {"Threshold": ThresholdModel(), "Continuous": ContinuousModel()}

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    for ax, (model_name, model) in zip(axes, models.items()):
        for preset_name, p in PRESETS.items():
            Ls = np.array([model.arrival_time(p, float(B)) for B in Bs])
            strength = attractor_strength(model, p, B_range=(15, 90), n_B=30)
            ax.plot(Bs, Ls, label=f"{preset_name} (A={strength:.2f})", linewidth=2)

        ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
        ax.axvline(0, color="red", linestyle=":", alpha=0.3)
        ax.set_xlabel("B (缓冲时间, 分钟)")
        ax.set_ylabel("L (迟到量, 分钟)")
        ax.set_title(f"{model_name} 模型")
        ax.legend(loc="upper right")
        ax.grid(alpha=0.3)

    fig.suptitle("吸引子曲线: L vs B  |  plateau = 强吸引子", fontsize=14)
    fig.tight_layout()
    out = fig_dir / "attractor.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
