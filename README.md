# Numerical Psychology: 拖延的吸引子模型

为什么不管闹钟提前多少分钟，最后总迟到差不多 10 分钟？

本项目用 5 个数值模型形式化这个观察：**应急感**（urgency）在 deadline 临近时切换行为模式，但应急速度有上限，所以迟到量被锁死 -- 这就是一个**吸引子**（attractor）。

## 模型

| 模型 | 内部驱动 | 关键参数 | 备注 |
|------|---------|---------|------|
| **Threshold** | 阶跃紧迫感 | $v_s, v_f, T^*$ | 你的原始观察；有闭式解 $L = (W - v_s(B-T^*))/v_f - T^*$ |
| **Continuous** | sigmoid 紧迫感 | $\alpha, T^*$ | 平滑版阈值模型 |
| **TMT** | Steel 的动机公式 | $\Gamma$ (impulsiveness) | Steel (2007) *The Nature of Procrastination* |
| **Yerkes-Dodson** | 倒 U 形唤醒 | $T_{yd}$ | 太接近 deadline 反而减速（恐慌） |
| **Planning Fallacy** | 工作量低估噪声 | $\sigma$ | 包装其他模型；Kahneman-Tversky |

## 关键洞察：吸引子

设 $B$ = 醒来到上课的缓冲时间，$L$ = 迟到量。在 Threshold 模型里：

$$L = \frac{W - v_s (B - T^*)}{v_f} - T^*$$

当 $v_s \to 0$（强拖延），$L \to W/v_f - T^*$，**与 $B$ 无关**。所以只要 $B > T^*$（醒得够早），迟到量被锁死。

定义**吸引子强度** $A(\theta) = \text{std}_B(L(B; \theta))$ over $B \in [15, 90]$。$A \to 0$ 表示强吸引子。

## 运行

```bash
pip install -r requirements.txt

# 网页交互（5 个 tab）
streamlit run app/streamlit_app.py

# 静态图（生成 figures/*.png）
python experiments/01_attractor_curve.py
python experiments/02_phase_diagram.py
python experiments/03_trajectory.py
```

## 验证

- **吸引子 plateau**: 选 "procrastinator" 预设 -> Tab 2 中 $B > T^*$ 时 $L$ 接近常数
- **非拖延者**: 选 "diligent" 预设 -> $L$ 始终 $< 0$（早到）
- **YD 反直觉**: Tab 4 中 YD 模型 $L$ 随 $B$ 减小而**增大**（恐慌减速）
- **相图**: Tab 3 中 $v_s \to 0$ 区域显示低标准差（强吸引子）

## 参考

- Steel, P. (2007). *The Nature of Procrastination: A Meta-Analytic and Theoretical Review*. Psychological Bulletin.
- Yerkes, R. M., & Dodson, J. D. (1908). *The relation of strength of stimulus to rapidity of habit-formation*.
- Kahneman, D., & Tversky, A. (1979). *Intuitive prediction: Biases and corrective procedures*.
- Parkinson, C. N. (1955). *Parkinson's Law*.
