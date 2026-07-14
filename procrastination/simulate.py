"""Numerical integration helpers shared across models.

Convention: t is wall-clock time relative to class start (t=0).
  - t = -B: wake up
  - t = 0:  class starts
  - t = L > 0: late
tau = -t is "time remaining until class" (always positive before class).
"""
from __future__ import annotations
from typing import Callable
import numpy as np


def integrate_arrival(
    speed_fn: Callable[[float], float],
    W: float,
    B: float,
    dt: float = 0.01,
    t_max: float = 600.0,
) -> float:
    """Integrate work_done = ∫ speed(tau) dt until W reached. Returns arrival t.

    Skips intervals where speed <= 0 (e.g., TMT before motivation triggers).
    t_max is a safety cap; if work < W at t_max, returns t_max (panic failure).
    """
    t = -B
    work = 0.0
    while work < W and t < t_max:
        tau = -t
        v = speed_fn(tau)
        if v <= 0.0:
            t += dt
            continue
        work += v * dt
        t += dt
    return t


def trajectory(
    speed_fn: Callable[[float], float],
    driver_fn: Callable[[float], float],
    W: float,
    B: float,
    dt: float = 0.05,
    t_max: float = 480.0,
) -> dict:
    """Sample speed, driver, cumulative work over time. Returns arrays + arrival.

    driver_fn is the model's internal state (urgency / arousal / motivation),
    included so plots can show what's driving the speed change.
    """
    ts = np.arange(-B, t_max, dt)
    work = np.zeros_like(ts)
    speed_arr = np.zeros_like(ts)
    driver_arr = np.zeros_like(ts)
    cumulative = 0.0
    arrival = ts[-1]
    done = False
    for i, t in enumerate(ts):
        tau = -t
        v = speed_fn(tau)
        speed_arr[i] = v
        driver_arr[i] = driver_fn(tau)
        if not done:
            cumulative += v * dt
            work[i] = min(cumulative, W)
            if cumulative >= W:
                arrival = t
                done = True
        else:
            work[i] = W
    return {
        "t": ts,
        "work_done": work,
        "speed": speed_arr,
        "driver": driver_arr,
        "arrival": arrival,
    }
