import re
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==================== 1. 配置中文字体 ====================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


# ==================== 2. 辅助函数 ====================
def read_csv_safe(file_path):
    """安全读取 CSV 并自动清理表头首尾空格"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'ansi']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            df.columns = df.columns.astype(str).str.strip()
            return df
        except Exception:
            continue
    raise ValueError(f"无法正确读取文件: {file_path}")


def find_gyro_axis(columns, axis):
    """使用正则表达式精准匹配 X/Y/Z 陀螺仪角速度列（排除加速度计）"""
    # 避开 f-string 中大括号的冲突，改用普通字符串拼接
    pattern = r'[\s_\(\/]' + axis + r'([\s\(\/\}]|$)'
    for c in columns:
        c_lower = c.lower()
        # 过滤加速度列
        if 'acc' in c_lower or 'm/s' in c_lower:
            continue
        if re.search(pattern, c_lower):
            return c
    return None


def get_gyro_cols(df, df_name):
    """智能查找时间列与 X, Y, Z 陀螺仪列"""
    cols = df.columns.tolist()
    time_col = next((c for c in cols if 'time' in c.lower() or '时间' in c), None)

    gx = find_gyro_axis(cols, 'x')
    gy = find_gyro_axis(cols, 'y')
    gz = find_gyro_axis(cols, 'z')

    print(f"\n🔍 [{df_name}] 识别结果:")
    print(f"  • 时间列: [{time_col}]")
    print(f"  • Gyro X: [{gx}]")
    print(f"  • Gyro Y: [{gy}]")
    print(f"  • Gyro Z: [{gz}]")

    return time_col, gx, gy, gz


def cumtrapz_np(y, x):
    """手写梯形数值积分函数"""
    dx = np.diff(x)
    integral = np.cumsum(0.5 * (y[:-1] + y[1:]) * dx)
    return np.insert(integral, 0, 0.0)


# ==================== 3. 主流程 ====================
project_dir = Path(__file__).resolve().parent
file_data1 = project_dir / "data1" / "Raw Data.csv"
file_data2 = project_dir / "data2" / "Raw Data.csv"

if not (file_data1.exists() and file_data2.exists()):
    print("❌ 未在 data1/data2 文件夹中找到 Raw Data.csv，请检查路径及文件名！")
    exit()

print("📄 正在加载数据...")
df1 = read_csv_safe(file_data1)
df2 = read_csv_safe(file_data2)

# 独立提取两表列名
t1_col, gx1, gy1, gz1 = get_gyro_cols(df1, "data1")
t2_col, gx2, gy2, gz2 = get_gyro_cols(df2, "data2")

if None in [t2_col, gx2, gy2, gz2]:
    print("\n❌ 错误：data2 中未能匹配到完整的陀螺仪数据列！")
    exit()

# -------------------- 步骤 A: 计算静态零偏 (Bias) --------------------
if None not in [gx1, gy1, gz1]:
    print("\n✅ 在 data1 中找到了陀螺仪数据，使用 data1 全局均值计算静态零偏...")
    for col in [gx1, gy1, gz1]:
        df1[col] = pd.to_numeric(df1[col], errors='coerce')
    df1_clean = df1.dropna(subset=[gx1, gy1, gz1])
    bias_x = df1_clean[gx1].mean()
    bias_y = df1_clean[gy1].mean()
    bias_z = df1_clean[gz1].mean()
else:
    print("\n⚠️ 提示：data1 中包含的是加速度数据而非陀螺仪数据！")
    print("💡 自动启用备用方案：提取 data2 前 1 秒（静态阶段）的数据计算陀螺仪零偏...")

    for col in [t2_col, gx2, gy2, gz2]:
        df2[col] = pd.to_numeric(df2[col], errors='coerce')

    # 取 data2 前 1 秒数据
    t_start = df2[t2_col].min()
    static_df = df2[df2[t2_col] <= (t_start + 1.0)].dropna(subset=[gx2, gy2, gz2])

    bias_x = static_df[gx2].mean()
    bias_y = static_df[gy2].mean()
    bias_z = static_df[gz2].mean()

print("\n" + "=" * 50)
print("🎯【零偏校准结果 (Bias)】:")
print(f"  • X 轴零偏: {bias_x:.6f} rad/s")
print(f"  • Y 轴零偏: {bias_y:.6f} rad/s")
print(f"  • Z 轴零偏: {bias_z:.6f} rad/s")
print("=" * 50)

# -------------------- 步骤 B: 动态数据处理与积分 (data2) --------------------
for col in [t2_col, gx2, gy2, gz2]:
    df2[col] = pd.to_numeric(df2[col], errors='coerce')

df2_clean = df2.dropna(subset=[t2_col, gx2, gy2, gz2]).sort_values(t2_col)
print(f"\n📊 data2 成功提取出 {len(df2_clean)} 行有效数据！")

t = df2_clean[t2_col].values
gx_cal = df2_clean[gx2].values - bias_x
gy_cal = df2_clean[gy2].values - bias_y
gz_cal = df2_clean[gz2].values - bias_z

# 梯形数值积分求角度 (deg)
angle_x = cumtrapz_np(gx_cal, t) * (180.0 / np.pi)
angle_y = cumtrapz_np(gy_cal, t) * (180.0 / np.pi)
angle_z = cumtrapz_np(gz_cal, t) * (180.0 / np.pi)

# -------------------- 步骤 C: 双子图绘制 --------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, dpi=120)
fig.suptitle('IMU 姿态解算 - 零偏校准与累计旋转角度', fontsize=14, fontweight='bold')

# 上图：校准后角速度
ax1.plot(t, gx_cal, label='Gyro X (校准后)', alpha=0.8, linewidth=1)
ax1.plot(t, gy_cal, label='Gyro Y (校准后)', alpha=0.8, linewidth=1)
ax1.plot(t, gz_cal, label='Gyro Z (校准后)', alpha=0.8, linewidth=1)
ax1.set_ylabel('校准角速度 (rad/s)', fontsize=11)
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(loc='upper right')

# 下图：解算角度
ax2.plot(t, angle_x, label='X 轴旋转角 (°)', linewidth=1.5)
ax2.plot(t, angle_y, label='Y 轴旋转角 (°)', linewidth=1.5)
ax2.plot(t, angle_z, label='Z 轴旋转角 (°)', linewidth=1.5)
ax2.set_xlabel('时间 Time (s)', fontsize=11)
ax2.set_ylabel('累计角度 Degree (°)', fontsize=11)
ax2.grid(True, linestyle='--', alpha=0.5)
ax2.legend(loc='upper right')

plt.tight_layout()
plt.savefig('imu_angle_integration.png', dpi=300)
print("\n🎉 姿态解算图表绘制成功！正在弹出...")
plt.show()