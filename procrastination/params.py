"""Parameter dataclass and presets for procrastination models.

Time unit: minutes. Speed unit: work-per-minute (arbitrary).
Class start is at t=0; wake-up at t=-B; arrival at t=L (positive = late).
"""
from __future__ import annotations
from dataclasses import dataclass, replace


@dataclass
class Params:
    # Shared
    W: float = 30.0          # total work to complete (minutes-equivalent at v=1)
    v_s: float = 0.1         # slow / procrastination speed (work-per-minute)
    v_f: float = 1.2         # fast / emergency speed
    T_star: float = 15.0     # urgency threshold (minutes before class)

    # Continuous model
    alpha: float = 0.5       # sigmoid steepness

    # TMT (Steel 2007): Motivation = (E*V) / (1 + gamma * tau)
    gamma: float = 0.5       # impulsiveness (higher = more procrastination)
    E: float = 0.9           # expectancy of success
    V: float = 5.0           # value of the task
    M_star: float = 0.4      # motivation threshold for action

    # Yerkes-Dodson
    T_yd: float = 50.0       # arousal time constant (hump capacity ~= (2/3)*(v_f-v_s)*T_yd)

    # Planning Fallacy
    sigma: float = 0.2       # lognormal noise on W

    def with_(self, **kwargs) -> "Params":
        return replace(self, **kwargs)


# Plateau (asymptotic L for large B with v_s -> 0) is W/v_f - T*.
# For procrastinator / user_observation: 30/1.2 - 15 = 10 min late (matches observation).
PRESETS: dict[str, Params] = {
    "diligent":         Params(W=30.0, v_s=1.5,  v_f=1.5, T_star=15, gamma=0.1),
    "balanced":         Params(W=30.0, v_s=0.4,  v_f=1.5, T_star=15, gamma=0.3),
    "procrastinator":   Params(W=30.0, v_s=0.02, v_f=1.2, T_star=15, gamma=0.8),
    "user_observation": Params(W=30.0, v_s=0.05, v_f=1.2, T_star=15, gamma=0.7),
}
