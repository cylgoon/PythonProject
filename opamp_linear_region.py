"""开环与闭环运放线性放大区间对比图。

理想运放传输特性 Vout = clip(gain × Vin, ±Vsat)：
  开环  gain = A = 1e5  → 线性区 ±Vsat/A ≈ ±135 µV（极窄）
  闭环  gain = G = 10   → 线性区 ±Vsat/G = ±1.35 V（宽 1e4 倍）
±15 V 电源下输出饱和电压取 ±13.5 V。

运行：
  python opamp_linear_region.py              # 弹出窗口并保存 PNG
  python opamp_linear_region.py --save-only  # 仅保存 PNG
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# ---- 配色（浅色图表面，参考调色板）----
C_OPEN = "#2a78d6"    # 开环：蓝（分类槽位 1）
C_CLOSED = "#eb6834"  # 闭环：橙（分类槽位 2）
INK = "#0b0b0b"       # 主文字
INK2 = "#52514e"      # 次文字
MUTED = "#898781"     # 轴刻度等弱标注
GRID = "#e1e0d9"      # 网格线
AXIS = "#c3c2b7"      # 轴线
SURFACE = "#fcfcfb"   # 图表面

plt.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial"],
    "axes.unicode_minus": False,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2,
    "text.color": INK2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

VSAT = 13.5   # 输出饱和电压（±15 V 电源）
A_OL = 1e5    # 开环增益
G_CL = 10.0   # 闭环增益
X_OL = VSAT / A_OL  # 开环线性区半宽 = 135 µV
X_CL = VSAT / G_CL  # 闭环线性区半宽 = 1.35 V
print(f"open-loop linear region: +/-{X_OL * 1e6:.0f} uV, "
      f"closed-loop: +/-{X_CL:.2f} V ({A_OL / G_CL:.0e}x wider)")


def vout(x, gain):
    """理想运放传输特性：线性放大后输出饱和。"""
    return np.clip(gain * x, -VSAT, VSAT)


def draw_transfer(ax, x, gain, xhalf, color, title, xlabel, xticks, width_label):
    """画一条传输特性曲线：曲线 + 线性区阴影 + 边界虚线 + 标注。"""
    ax.plot(x, vout(x, gain), color=color, lw=2, solid_capstyle="round")
    ax.axvspan(-xhalf, xhalf, color=color, alpha=0.10, lw=0)
    for xb in (-xhalf, xhalf):
        ax.axvline(xb, color=MUTED, lw=0.8, ls=(0, (2, 3)))

    ax.text(0, 14.3, f"线性区 {width_label}", ha="center", va="top",
            fontsize=10, color=INK)
    ax.text(x.min() * 0.82, -14.35, "负饱和", ha="center", va="top",
            fontsize=9, color=INK2)
    ax.text(x.max() * 0.82, 14.35, "正饱和", ha="center", va="bottom",
            fontsize=9, color=INK2)

    ax.set_title(title, color=INK)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("输出电压 Vout (V)")
    ax.set_xticks(xticks)
    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(-15.6, 15.6)
    ax.set_yticks(range(-15, 16, 5))
    ax.grid(True)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


fig = plt.figure(figsize=(12, 7))
gs = fig.add_gridspec(2, 2, height_ratios=[1.5, 0.9], hspace=0.5, wspace=0.24,
                      left=0.06, right=0.99, top=0.89, bottom=0.10)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, :])

# 图 1：开环 —— 横轴 µV，线性区极窄
draw_transfer(ax1, np.linspace(-200, 200, 4001), A_OL * 1e-6, X_OL * 1e6, C_OPEN,
              r"开环：增益 $A = 10^5$", "差分输入 Vd (µV)",
              range(-200, 201, 100), "±135 µV")

# 图 2：闭环 —— 横轴 V，线性区宽得多
draw_transfer(ax2, np.linspace(-3, 3, 4001), G_CL, X_CL, C_CLOSED,
              r"闭环：增益 $G = 10$", "输入电压 Vin (V)",
              range(-3, 4, 1), "±1.35 V")

# 图 3：线性区宽度对比（对数刻度，两条直接对比）
ax3.barh([0, 1], [X_OL, X_CL], left=1e-5, height=0.12, color=[C_OPEN, C_CLOSED])
ax3.set_xscale("log")
ax3.set_xlim(1e-5, 10)
ax3.set_ylim(-0.75, 1.75)
ax3.set_yticks([0, 1])
ax3.set_yticklabels([r"开环 $A = 10^5$", r"闭环 $G = 10$"],
                    fontsize=10, color=INK2)

def logfmt(v, _pos):
    if v >= 1:
        return f"{v:g} V"
    if v >= 1e-3:
        return f"{v * 1e3:g} mV"
    return f"{v * 1e6:g} µV"

ax3.xaxis.set_major_formatter(FuncFormatter(logfmt))
ax3.set_xlabel("线性区半宽（对数刻度）")
ax3.set_title("线性区宽度对比", color=INK)
ax3.grid(axis="x")
ax3.set_axisbelow(True)
for side in ("top", "right"):
    ax3.spines[side].set_visible(False)

ax3.text(X_OL * 1.15, 0, "±135 µV", va="center", ha="left",
         fontsize=9.5, color=INK2)
ax3.text(X_CL * 1.15, 1, "±1.35 V", va="center", ha="left",
         fontsize=9.5, color=INK2)
ax3.annotate("", xy=(X_CL, 0.55), xytext=(X_OL * 1.1, 0.55),
             arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1))
ax3.text(np.sqrt(X_OL * X_CL) * 1.15, 0.72, r"宽度相差 $10^4$ 倍",
         ha="left", va="bottom", fontsize=10, color=INK)

fig.suptitle("开环 vs 闭环运放：线性放大区间", x=0.06, y=0.965,
             ha="left", va="top", fontsize=15, color=INK)
fig.text(0.06, 0.02,
         "理想运放模型 Vout = clip(gain × Vin)：±15 V 电源、输出饱和 ±13.5 V。"
         "开环增益极高，线性区窄到只有 µV 量级；闭环用负反馈把增益降到 10，"
         "换来的线性区宽 10⁴ 倍。",
         fontsize=9, color=INK2)

fig.savefig("opamp_linear_region.png", dpi=200, facecolor=SURFACE)
print("saved: opamp_linear_region.png")
if "--save-only" not in sys.argv:
    plt.show()
