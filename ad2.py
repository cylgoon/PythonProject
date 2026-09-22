import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['figure.dpi'] = 150


# ====================== 1. 微弱信号放大前后对比 ======================
def draw_amplification():
    t = np.linspace(0, 10, 1000)
    # 输入微弱光电流信号 (mV级)
    input_signal = 0.005 * np.sin(2 * np.pi * 0.5 * t) + 0.001 * np.random.randn(len(t))
    # 放大100倍后的输出信号
    output_signal = input_signal * 100

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 4), sharex=True)

    ax1.plot(t, input_signal, 'b-', linewidth=0.8)
    ax1.set_title('Input Photo Signal (Before Amplification)', fontsize=10)
    ax1.set_ylabel('Voltage (mV)')
    ax1.grid(alpha=0.3)

    ax2.plot(t, output_signal, 'r-', linewidth=0.8)
    ax2.set_title('Output Signal (After 100x Amplification)', fontsize=10)
    ax2.set_ylabel('Voltage (mV)')
    ax2.set_xlabel('Time (ms)')
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('amplification_compare.png', bbox_inches='tight')
    plt.close()


# ====================== 2. 滤波前后噪声对比 ======================
def draw_filter_effect():
    t = np.linspace(0, 5, 2000)
    # 原始信号：有用信号+高频噪声
    clean_signal = 0.5 * np.sin(2 * np.pi * 0.8 * t)
    high_freq_noise = 0.2 * np.sin(2 * np.pi * 20 * t) + 0.1 * np.random.randn(len(t))
    noisy_signal = clean_signal + high_freq_noise

    # 简单模拟二阶低通滤波效果
    from scipy.signal import butter, filtfilt
    b, a = butter(2, 0.02, btype='low')
    filtered_signal = filtfilt(b, a, noisy_signal)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 4), sharex=True)

    ax1.plot(t, noisy_signal, 'b-', linewidth=0.7)
    ax1.set_title('Signal Before Filter (With High Frequency Noise)', fontsize=10)
    ax1.set_ylabel('Amplitude')
    ax1.grid(alpha=0.3)

    ax2.plot(t, filtered_signal, 'r-', linewidth=0.8)
    ax2.set_title('Signal After 2nd Order Low-pass Filter', fontsize=10)
    ax2.set_ylabel('Amplitude')
    ax2.set_xlabel('Time (ms)')
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('filter_effect.png', bbox_inches='tight')
    plt.close()


# ====================== 3. ADC采样输出波形 ======================
def draw_adc_sampling():
    t_analog = np.linspace(0, 8, 1000)
    analog_signal = 1.2 + 0.8 * np.sin(2 * np.pi * 0.3 * t_analog)

    # 采样点
    sample_points = np.arange(0, 8, 0.2)
    sampled_signal = 1.2 + 0.8 * np.sin(2 * np.pi * 0.3 * sample_points)
    # 量化到16位
    adc_code = np.round((sampled_signal / 3.3) * 65535).astype(int)

    fig, ax1 = plt.subplots(figsize=(10, 3.5))

    ax1.plot(t_analog, analog_signal, 'b--', label='Analog Input', alpha=0.6)
    ax1.stem(sample_points, sampled_signal, 'r', markerfmt='ro', basefmt=' ', label='Sampled Points')
    ax1.set_title('16-bit ADC Sampling Result', fontsize=10)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Voltage (V)')
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('adc_sampling.png', bbox_inches='tight')
    plt.close()


# 执行生成
draw_amplification()
draw_filter_effect()
draw_adc_sampling()
print("采集板项目波形已生成：amplification_compare.png、filter_effect.png、adc_sampling.png")
