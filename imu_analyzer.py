import pandas as pd
import matplotlib.pyplot as plt

# 1. 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 2. 读取合并后的数据
df = pd.read_csv('merged_all_data.csv')

# 3. 按“来源批次”分别画图（解决多文件拼接导致的时间突变）
batches = df['来源批次'].unique() if '来源批次' in df.columns else ['默认批次']

for batch in batches:
    # 筛选当前批次的数据
    sub_df = df[df['来源批次'] == batch].copy() if '来源批次' in df.columns else df.copy()

    # 确保数值列转为 numeric
    numeric_cols = []
    for col in sub_df.columns:
        if col not in ['来源批次', '来源文件名']:
            sub_df[col] = pd.to_numeric(sub_df[col], errors='coerce')
            if pd.api.types.is_numeric_dtype(sub_df[col]):
                numeric_cols.append(col)

    # 确定 X 轴：如果存在 Time (s) 则用时间做 X 轴，否则用 index
    x_data = sub_df['Time (s)'] if 'Time (s)' in sub_df.columns else sub_df.index
    x_label = '时间 Time (s)' if 'Time (s)' in sub_df.columns else '采样点序列 (Index)'

    # 自动归类加速度列与角速度列（排除时间列）
    acc_cols = [c for c in numeric_cols if ('acc' in c.lower() or 'm/s' in c.lower()) and 'time' not in c.lower()]
    gyro_cols = [c for c in numeric_cols if ('gyro' in c.lower() or 'rad' in c.lower()) and 'time' not in c.lower()]

    # 如果没匹配到关键字，就把除去 Time (s) 的前 3 列当加速度，后 3 列当角速度
    if not acc_cols and not gyro_cols:
        other_cols = [c for c in numeric_cols if 'time' not in c.lower()]
        acc_cols = other_cols[:3]
        gyro_cols = other_cols[3:6]

    # 4. 创建上下分屏的双子图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, dpi=120)
    fig.suptitle(f'IMU 传感器波形图 - [{batch}]', fontsize=14, fontweight='bold')

    # 上图：绘制加速度
    for col in acc_cols:
        ax1.plot(x_data, sub_df[col], label=col, alpha=0.85, linewidth=1.2)
    ax1.set_ylabel('加速度 (m/s²)', fontsize=11)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right')

    # 下图：绘制角速度
    for col in gyro_cols:
        ax2.plot(x_data, sub_df[col], label=col, alpha=0.85, linewidth=1.2)
    ax2.set_xlabel(x_label, fontsize=11)
    ax2.set_ylabel('角速度 (rad/s)', fontsize=11)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')

    plt.tight_layout()

    # 保存并弹窗显示
    out_name = f'imu_plot_{batch}.png'
    plt.savefig(out_name, dpi=300)
    print(f"🎉 成功生成 [{batch}] 的分栏波形图: {out_name}")
    plt.show()