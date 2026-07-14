"""Streamlit app: interactive procrastination attractor explorer.

Run: streamlit run app/streamlit_app.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from procrastination import (
    Params, PRESETS, ALL_MODELS,
    ThresholdModel, ContinuousModel, TMTModel, YerkesDodsonModel,
    PlanningFallacyModel,
    attractor_strength, lateness_curve, phase_diagram,
)


st.set_page_config(page_title="拖延的吸引子", page_icon="⏰", layout="wide")
st.title("⏰ 拖延的吸引子模型")
st.caption("为什么不管闹钟提前多少分钟，最后总迟到差不多 10 分钟？")


# --- Sidebar: parameters ---
st.sidebar.title("参数")
preset_options = list(PRESETS.keys()) + ["custom"]
preset_name = st.sidebar.selectbox("预设", preset_options, index=2)

if preset_name == "custom":
    p = Params(
        W=st.sidebar.slider("W (工作量)", 5.0, 60.0, 30.0, 0.5),
        v_s=st.sidebar.slider("v_s (拖延速度)", 0.0, 1.5, 0.1, 0.01),
        v_f=st.sidebar.slider("v_f (应急速度)", 0.5, 5.0, 3.0, 0.1),
        T_star=st.sidebar.slider("T* (阈值, 分钟)", 1.0, 40.0, 25.0, 0.5),
        alpha=st.sidebar.slider("α (sigmoid 陡度)", 0.05, 2.0, 0.5, 0.05),
        gamma=st.sidebar.slider("Γ (TMT impulsiveness)", 0.05, 2.0, 0.5, 0.05),
        T_yd=st.sidebar.slider("T_yd (YD 时间常数)", 5.0, 60.0, 30.0, 1.0),
        sigma=st.sidebar.slider("σ (计划谬误噪声)", 0.0, 0.6, 0.2, 0.02),
    )
else:
    p = PRESETS[preset_name]
    st.sidebar.caption(f"W={p.W}, v_s={p.v_s}, v_f={p.v_f}, T*={p.T_star}, Γ={p.gamma}")


# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. 单次模拟",
    "2. 吸引子曲线",
    "3. 相图",
    "4. 模型对比",
    "5. 计划谬误分布",
])


# --- Tab 1: single-run trajectory ---
with tab1:
    st.subheader("单次模拟轨迹")
    col1, col2 = st.columns(2)
    with col1:
        B = st.slider("B (缓冲, 分钟)", 5.0, 90.0, 40.0, 1.0, key="B_tab1")
    with col2:
        model_name = st.selectbox("模型", list(ALL_MODELS.keys()), key="model_tab1")
    model = ALL_MODELS[model_name]
    traj = model.trajectory(p, B)

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_titles=["速度 v(t)", "驱动 (urgency / arousal / motivation)", "已完成工作"],
        vertical_spacing=0.08,
    )
    fig.add_trace(go.Scatter(x=traj["t"], y=traj["speed"], name="v(t)", line=dict(color="#1f77b4", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=traj["t"], y=traj["driver"], name="driver", line=dict(color="#ff7f0e", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=traj["t"], y=traj["work_done"], name="work", line=dict(color="#2ca02c", width=2), fill="tozeroy"), row=3, col=1)
    fig.add_hline(y=p.W, line=dict(dash="dot", color="black"), row=3, col=1, annotation_text="W")
    fig.add_vline(x=0, line=dict(dash="dash", color="red"), annotation_text="上课")
    fig.add_vline(x=traj["arrival"], line=dict(dash="dot", color="green"), annotation_text=f"到达 (L={traj['arrival']:.1f})")
    fig.update_layout(height=620, showlegend=False)
    st.plotly_chart(fig, width="stretch")

    L = model.arrival_time(p, B)
    status = "迟到" if L > 0 else "早到"
    st.info(f"到达时刻 t = {L:.2f} 分钟 → {status} {abs(L):.2f} 分钟")


# --- Tab 2: attractor curve ---
with tab2:
    st.subheader("吸引子曲线 L vs B")
    st.caption("plateau (平坦区) = 吸引子；斜率大 = 无吸引子。")
    model_name = st.selectbox("模型", list(ALL_MODELS.keys()), key="model_tab2")
    model = ALL_MODELS[model_name]
    Bs, Ls = lateness_curve(model, p, B_range=(10, 120), n_B=80)

    mask = (Bs >= 15) & (Bs <= 90)
    strength = float(np.std(Ls[mask]))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Bs, y=Ls, mode="lines", name=model.name, line=dict(width=3)))
    fig.add_hline(y=0, line=dict(dash="dash", color="gray"))
    fig.add_hrect(y0=0, y1=max(Ls.max(), 1), line_width=0, fillcolor="red", opacity=0.05, annotation_text="迟到区")
    fig.update_layout(
        title=f"{model.name} | 吸引子强度 A = {strength:.3f}  (越小 = 越强)",
        xaxis_title="B (缓冲, 分钟)",
        yaxis_title="L (迟到量, 分钟)",
        height=500,
    )
    st.plotly_chart(fig, width="stretch")


# --- Tab 3: phase diagram ---
with tab3:
    st.subheader("相图: (v_s, T*) → 吸引子强度")
    st.caption("深色 = 强吸引子（L 与 B 无关）；亮色 = 无吸引子。")

    @st.cache_data
    def compute_phase(W: float, v_f: float, alpha: float, gamma: float, T_yd: float):
        p_base = Params(W=W, v_f=v_f, alpha=alpha, gamma=gamma, T_yd=T_yd)
        return phase_diagram(
            ThresholdModel(), p_base,
            v_s_range=(0.0, 1.0),
            T_star_range=(5.0, 40.0),
            n=30,
        )

    phase = compute_phase(p.W, p.v_f, p.alpha, p.gamma, p.T_yd)

    fig = go.Figure(data=go.Heatmap(
        z=phase["strength"],
        x=phase["T_star"],
        y=phase["v_s"],
        colorscale="Viridis_r",
        colorbar=dict(title="A (低=强吸引子)"),
        hovertemplate="v_s=%{y:.2f}, T*=%{x:.1f}, A=%{z:.3f}<extra></extra>",
    ))
    fig.update_layout(
        xaxis_title="T* (阈值, 分钟)",
        yaxis_title="v_s (拖延速度)",
        height=550,
    )
    st.plotly_chart(fig, width="stretch")

    st.markdown("**读图**：左下角 (低 v_s + 低 T*) 不一定是强吸引子 -- T* 太小意味着来不及触发应急模式，L 会随 B 剧烈变化。强吸引子出现在 **低 v_s + 中等 T*** 区域。")


# --- Tab 4: model comparison ---
with tab4:
    st.subheader("模型对比: L vs B (同一组参数)")
    Bs = np.linspace(10, 120, 80)
    fig = go.Figure()
    for name, model in ALL_MODELS.items():
        Ls = np.array([model.arrival_time(p, float(B)) for B in Bs])
        fig.add_trace(go.Scatter(x=Bs, y=Ls, mode="lines", name=name, line=dict(width=2.5)))
    fig.add_hline(y=0, line=dict(dash="dash", color="gray"))
    fig.update_layout(
        xaxis_title="B (缓冲, 分钟)",
        yaxis_title="L (迟到量, 分钟)",
        height=550,
    )
    st.plotly_chart(fig, width="stretch")

    st.markdown("**预期**：")
    st.markdown("- Threshold / Continuous / TMT 在大 B 处都趋于常数（吸引子）")
    st.markdown("- Yerkes-Dodson 反直觉：B 太小时 L 反而**增大**（恐慌减速）")


# --- Tab 5: planning fallacy ---
with tab5:
    st.subheader("计划谬误: L 的分布 (LogNormal 噪声 on W)")
    col1, col2 = st.columns(2)
    with col1:
        B = st.slider("B (缓冲)", 5.0, 90.0, 40.0, 1.0, key="B_tab5")
    with col2:
        inner_name = st.selectbox("内部模型", list(ALL_MODELS.keys()), key="inner_tab5")
    n_samples = st.slider("采样次数", 200, 3000, 1000, 100, key="n_tab5")

    inner = ALL_MODELS[inner_name]
    pf = PlanningFallacyModel(inner, seed=42)
    samples = pf.arrival_distribution(p, B, n=n_samples)

    fig = go.Figure(data=go.Histogram(x=samples, nbinsx=40, marker_color="#1f77b4"))
    fig.add_vline(x=0, line=dict(dash="dash", color="red"), annotation_text="上课")
    fig.add_vline(x=samples.mean(), line=dict(dash="dot", color="green"), annotation_text=f"均值={samples.mean():.2f}")
    fig.update_layout(
        title=f"{inner_name} + LogNormal(σ={p.sigma}) | B={B}",
        xaxis_title="L (迟到量, 分钟)",
        yaxis_title="频次",
        height=480,
    )
    st.plotly_chart(fig, width="stretch")

    c1, c2, c3 = st.columns(3)
    c1.metric("均值 L", f"{samples.mean():.2f} 分钟")
    c2.metric("标准差", f"{samples.std():.2f} 分钟")
    c3.metric("迟到概率", f"{(samples > 0).mean():.1%}")
