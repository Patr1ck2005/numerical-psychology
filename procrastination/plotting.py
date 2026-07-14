"""Matplotlib setup for CJK labels on Windows."""
import matplotlib.pyplot as plt


def setup_matplotlib() -> None:
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei", "SimHei", "SimSun",
        "DejaVu Sans", "Arial Unicode MS",
    ]
    plt.rcParams["axes.unicode_minus"] = False
