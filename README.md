# Numerical Psychology

**Why might an earlier alarm fail to reduce lateness?** Five toy numerical models explore how urgency, work rate and deadline pressure can create a nearly constant lateness plateau.

[简体中文](README.zh-CN.md) · [Model source](procrastination/) · [History](docs/README-history.md)

![Existing synthetic lateness curves for threshold and continuous models](figures/attractor.png)

*Model-generated curves already in the public repository. Preset labels are illustrative; these are not human-subject measurements or clinical evidence.*

## The experiment

| Model | Mechanism being explored |
|---|---|
| Threshold | Work rate switches when the deadline becomes close |
| Continuous | A smooth urgency response replaces the switch |
| TMT-inspired | A simplified motivation formula changes urgency |
| Yerkes–Dodson-inspired | Excess pressure can reduce the assumed work rate |
| Planning fallacy | Workload-estimation noise wraps other models |

For the threshold model, let `B` be the available buffer, `W` the workload, `vs` the slow rate, `vf` the urgent rate and `T*` the urgency threshold. In its applicable branch:

```text
L = (W - vs (B - T*)) / vf - T*
```

When `vs` approaches zero and `B > T*`, lateness `L` approaches `W/vf - T*`, almost independent of the buffer. Here “attractor” describes that parameter-response plateau, not a demonstrated universal psychological law or a formal dynamical-systems attractor for all five models.

## Run and explore

```bash
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Select presets and compare lateness curves, trajectories and phase diagrams. To regenerate the included numerical figures:

```bash
python experiments/01_attractor_curve.py
python experiments/02_phase_diagram.py
python experiments/03_trajectory.py
```

| Source | Contents |
|---|---|
| [procrastination/](procrastination/) | Model definitions and numerical utilities |
| [app/streamlit_app.py](app/streamlit_app.py) | Interactive comparison |
| [experiments/](experiments/) | Reproducible plotting scripts |
| [figures/](figures/) | Existing generated example figures |

## Status, references and license

An exploratory modeling notebook/application. There is no empirical dataset, fitted population model or validated intervention in this repository. Literature inspirations in the [original README](docs/README-history.md) include Steel (2007), Yerkes and Dodson (1908), and Kahneman and Tversky (1979); the implementations are simplified illustrations, not reproductions of all those theories. This documentation pass did not rerun the models.

No repository-wide open-source license is declared in this snapshot. Public source visibility does not grant an unrestricted reuse license; third-party material retains its own terms.
