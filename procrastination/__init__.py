"""Numerical psychology: procrastination attractor models."""

from .params import Params, PRESETS
from .models import (
    BaseModel,
    ThresholdModel,
    ContinuousModel,
    TMTModel,
    YerkesDodsonModel,
    PlanningFallacyModel,
    ALL_MODELS,
)
from .simulate import integrate_arrival, trajectory
from .analysis import attractor_strength, lateness_curve, phase_diagram

__all__ = [
    "Params",
    "PRESETS",
    "BaseModel",
    "ThresholdModel",
    "ContinuousModel",
    "TMTModel",
    "YerkesDodsonModel",
    "PlanningFallacyModel",
    "ALL_MODELS",
    "integrate_arrival",
    "trajectory",
    "attractor_strength",
    "lateness_curve",
    "phase_diagram",
]
