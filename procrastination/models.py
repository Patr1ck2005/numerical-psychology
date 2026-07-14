"""Five procrastination models with a unified interface.

Each model:
  - speed(p, tau) -> float:   work speed when time-to-class is tau minutes
  - driver(p, tau) -> float:  internal state (urgency / arousal / motivation) in [0, 1]
  - arrival_time(p, B) -> float: arrival t (positive = late, negative = early)
  - trajectory(p, B) -> dict:   time series for plotting

Closed-form solutions are used where available (Threshold, TMT); others
use numerical integration via `simulate.integrate_arrival`.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import replace
import numpy as np

from .params import Params
from .simulate import integrate_arrival, trajectory as _trajectory


class BaseModel(ABC):
    name: str = "Base"

    @abstractmethod
    def speed(self, p: Params, tau: float) -> float: ...

    @abstractmethod
    def driver(self, p: Params, tau: float) -> float: ...

    @abstractmethod
    def arrival_time(self, p: Params, B: float) -> float: ...

    def trajectory(self, p: Params, B: float, dt: float = 0.05, t_max: float = 480.0) -> dict:
        return _trajectory(
            speed_fn=lambda tau: self.speed(p, tau),
            driver_fn=lambda tau: self.driver(p, tau),
            W=p.W, B=B, dt=dt, t_max=t_max,
        )


class ThresholdModel(BaseModel):
    """Dual-speed with a hard urgency threshold.

    v(tau) = v_s if tau > T*, else v_f.
    Closed form: L = (W - v_s*(B - T*)) / v_f - T*, when B > T* and v_s*(B-T*) < W.
    """

    name = "Threshold"

    def speed(self, p, tau):
        return p.v_s if tau > p.T_star else p.v_f

    def driver(self, p, tau):
        return 0.0 if tau > p.T_star else 1.0

    def arrival_time(self, p, B):
        if p.v_s <= 0:
            # Pure procrastination: all work in fast mode starting at tau = T*
            if B <= p.T_star:
                # woke up past threshold
                return p.W / p.v_f - B
            return p.W / p.v_f - p.T_star

        slow_phase_duration = B - p.T_star  # only valid if B > T_star
        if B <= p.T_star:
            # woke up already in fast mode
            return p.W / p.v_f - B
        slow_work = p.v_s * slow_phase_duration
        if slow_work >= p.W:
            # finished during slow phase (diligent case)
            return p.W / p.v_s - B
        remaining = p.W - slow_work
        fast_time = remaining / p.v_f
        # slow phase: t = -B to t = -T*; fast phase: t = -T* to t = -T* + fast_time
        return -p.T_star + fast_time


class ContinuousModel(BaseModel):
    """Smooth urgency: sigmoid around T*.

    U(tau) = 1 / (1 + exp(alpha * (tau - T*)))
    v(tau) = v_s + (v_f - v_s) * U(tau)
    """

    name = "Continuous"

    def driver(self, p, tau):
        return 1.0 / (1.0 + np.exp(p.alpha * (tau - p.T_star)))

    def speed(self, p, tau):
        u = self.driver(p, tau)
        return p.v_s + (p.v_f - p.v_s) * u

    def arrival_time(self, p, B):
        return integrate_arrival(lambda tau: self.speed(p, tau), p.W, B)


class TMTModel(BaseModel):
    """Steel's Temporal Motivation Theory (2007).

    Motivation(tau) = (E * V) / (1 + gamma * tau).
    Action begins when Motivation > M*, then runs at v_f.
    Trigger: tau_trigger = ((E*V)/M* - 1) / gamma.
    L = W / v_f - tau_trigger.
    """

    name = "TMT"

    def motivation(self, p, tau):
        return (p.E * p.V) / (1.0 + p.gamma * max(tau, 0.0))

    def driver(self, p, tau):
        # Normalize motivation to [0, 1] for visualization (cap at motivation at tau=0)
        m_max = p.E * p.V
        return self.motivation(p, tau) / m_max if m_max > 0 else 0.0

    def trigger_tau(self, p):
        """Time-to-class at which motivation first exceeds M*."""
        if (p.E * p.V) <= p.M_star:
            # Never triggers -> infinite procrastination
            return float("inf")
        return ((p.E * p.V) / p.M_star - 1.0) / p.gamma

    def speed(self, p, tau):
        return 0.0 if tau > self.trigger_tau(p) else p.v_f

    def arrival_time(self, p, B):
        tau_trig = self.trigger_tau(p)
        if tau_trig == float("inf"):
            return 480.0  # never starts; safety cap
        if B <= tau_trig:
            # woke up past trigger, all fast
            return p.W / p.v_f - B
        return p.W / p.v_f - tau_trig


class YerkesDodsonModel(BaseModel):
    """Hybrid Yerkes-Dodson: inverted-U arousal on top of a procrastination baseline.

    Arousal A(tau) = exp(-tau / T_yd). At tau=0 (deadline), A=1 (max panic).
    Performance = 4 * A * (1 - A), peak at A=0.5 (i.e. tau = T_yd * ln 2).
    v(tau) = v_s + (v_f - v_s) * 4*A*(1-A).

    So at low arousal (far from deadline): v -> v_s (procrastination).
    At moderate arousal (productive urgency): v -> v_f (peak).
    At max arousal (panic at deadline): v -> v_s again (panic drops you back to slow).

    This avoids the degeneracy of pure YD (v=0 at A=1, never finishes) while
    keeping the inverted-U "too much panic hurts" intuition.
    """

    name = "Yerkes-Dodson"

    def arousal(self, p, tau):
        return float(np.exp(-max(tau, 0.0) / p.T_yd))

    def driver(self, p, tau):
        return self.arousal(p, tau)

    def performance(self, A):
        return 4.0 * A * (1.0 - A)

    def speed(self, p, tau):
        A = self.arousal(p, tau)
        return p.v_s + (p.v_f - p.v_s) * self.performance(A)

    def arrival_time(self, p, B):
        return integrate_arrival(lambda tau: self.speed(p, tau), p.W, B)


class PlanningFallacyModel(BaseModel):
    """Wraps another model; each call samples W ~ LogNormal(log W, sigma).

    Captures the planning fallacy: actual work exceeds planned work,
    with heavy right tail (LogNormal rather than Normal so it can't go negative).
    """

    name = "Planning Fallacy"

    def __init__(self, inner: BaseModel, seed: int | None = None):
        self.inner = inner
        self.rng = np.random.default_rng(seed)

    def _sample_W(self, p: Params) -> float:
        return float(self.rng.lognormal(np.log(p.W), p.sigma))

    def speed(self, p, tau):
        return self.inner.speed(p, tau)

    def driver(self, p, tau):
        return self.inner.driver(p, tau)

    def arrival_time(self, p, B):
        W_sample = self._sample_W(p)
        p_sample = p.with_(W=W_sample)
        return self.inner.arrival_time(p_sample, B)

    def arrival_distribution(self, p, B, n: int = 1000) -> np.ndarray:
        return np.array([self.arrival_time(p, B) for _ in range(n)])

    def trajectory(self, p, B, dt: float = 0.05, t_max: float = 240.0) -> dict:
        # Trajectory uses the mean W (deterministic) for visualization
        return self.inner.trajectory(p, B, dt=dt, t_max=t_max)


ALL_MODELS: dict[str, BaseModel] = {
    "Threshold": ThresholdModel(),
    "Continuous": ContinuousModel(),
    "TMT": TMTModel(),
    "Yerkes-Dodson": YerkesDodsonModel(),
}
