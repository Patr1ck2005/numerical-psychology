"""Analysis: attractor strength and phase diagrams.

Attractor strength A(theta) = std_B(L(B; theta)) over a buffer range.
Low A = strong attractor (lateness independent of buffer B).
"""
from __future__ import annotations
import numpy as np

from .models import BaseModel
from .params import Params


def attractor_strength(
    model: BaseModel,
    p: Params,
    B_range: tuple[float, float] = (15.0, 90.0),
    n_B: int = 30,
) -> float:
    """Standard deviation of lateness L over B in B_range. Smaller = stronger attractor."""
    Bs = np.linspace(*B_range, n_B)
    Ls = np.array([model.arrival_time(p, float(B)) for B in Bs])
    return float(np.std(Ls))


def lateness_curve(
    model: BaseModel,
    p: Params,
    B_range: tuple[float, float] = (10.0, 120.0),
    n_B: int = 60,
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (Bs, Ls) arrays for plotting L vs B."""
    Bs = np.linspace(*B_range, n_B)
    Ls = np.array([model.arrival_time(p, float(B)) for B in Bs])
    return Bs, Ls


def phase_diagram(
    model: BaseModel,
    p_base: Params,
    v_s_range: tuple[float, float] = (0.0, 1.0),
    T_star_range: tuple[float, float] = (5.0, 40.0),
    n: int = 30,
    B_range: tuple[float, float] = (15.0, 90.0),
    n_B: int = 20,
) -> dict:
    """2D sweep of (v_s, T*), each point colored by attractor strength.

    Returns dict with 'v_s', 'T_star', 'strength' (2D arrays).
    """
    v_s_vals = np.linspace(*v_s_range, n)
    T_star_vals = np.linspace(*T_star_range, n)
    strength = np.zeros((n, n))
    for i, v_s in enumerate(v_s_vals):
        for j, T_star in enumerate(T_star_vals):
            p = p_base.with_(v_s=float(v_s), T_star=float(T_star))
            strength[i, j] = attractor_strength(model, p, B_range=B_range, n_B=n_B)
    return {
        "v_s": v_s_vals,
        "T_star": T_star_vals,
        "strength": strength,  # shape (n_v_s, n_T_star)
    }


def tmt_phase_diagram(
    p_base: Params,
    gamma_range: tuple[float, float] = (0.05, 1.5),
    T_star_range: tuple[float, float] = (5.0, 40.0),
    n: int = 30,
    B_range: tuple[float, float] = (15.0, 90.0),
    n_B: int = 20,
) -> dict:
    """Phase diagram for TMT model varying gamma (impulsiveness) vs T_star."""
    from .models import TMTModel
    model = TMTModel()
    gamma_vals = np.linspace(*gamma_range, n)
    T_star_vals = np.linspace(*T_star_range, n)
    strength = np.zeros((n, n))
    for i, g in enumerate(gamma_vals):
        for j, T_star in enumerate(T_star_vals):
            p = p_base.with_(gamma=float(g), T_star=float(T_star))
            strength[i, j] = attractor_strength(model, p, B_range=B_range, n_B=n_B)
    return {
        "gamma": gamma_vals,
        "T_star": T_star_vals,
        "strength": strength,
    }
