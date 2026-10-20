import os

import matplotlib.pyplot as plt
import numpy as np
import pytest
import rosbag


def test_eight_figure_tracking_variance_visualized():
    """提取实际速度，验证速度波动稳定性，并生成单曲线可视化图表"""
    bag_path = "/workspace/tests_auto/data/flight_sample.bag"
    report_dir = "/workspace/tests_auto/reports"
    os.makedirs(report_dir, exist_ok=True)

    if not os.path.exists(bag_path):
        pytest.skip("未找到飞行日志，跳过此测试。")

    actual_t, actual_vx = [], []

    with rosbag.Bag(bag_path, "r") as bag:
        topics = ["/mavros/local_position/velocity_local"]
        for topic, msg, t in bag.read_messages(topics=topics):
            actual_t.append(t.to_sec())
            actual_vx.append(msg.twist.linear.x)

    if not actual_t:
        pytest.skip("未找到速度话题，无法绘图。")

    actual_vx = np.array(actual_vx)
    velocity_std = np.std(actual_vx)

    plt.figure(figsize=(10, 5))
    t_zero = actual_t[0]
    plt.plot(
        np.array(actual_t) - t_zero,
        actual_vx,
        label="Actual Velocity",
        color="#1f77b4",
        linewidth=2,
    )

    plt.title(f"X-Axis Velocity Fluctuation (Std Dev: {velocity_std:.4f} m/s)")
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.7)

    plt.savefig(f"{report_dir}/velocity_fluctuation.png")
    plt.close()

    assert velocity_std < 2.0, f"X轴速度波动异常，标准差为： {velocity_std:.4f}"


def test_imu_vibration_fft_visualized():
    """对 IMU Z轴加速度进行 FFT 频域分析，断言异常振动并生成频谱图"""
    bag_path = "/workspace/tests_auto/data/flight_sample.bag"
    report_dir = "/workspace/tests_auto/reports"

    if not os.path.exists(bag_path):
        pytest.skip("未找到飞行日志，跳过 IMU 振动分析。")

    timestamps, accel_z = [], []

    with rosbag.Bag(bag_path, "r") as bag:
        for topic, msg, t in bag.read_messages(topics=["/mavros/imu/data"]):
            timestamps.append(t.to_sec())
            accel_z.append(msg.linear_acceleration.z)

    if len(accel_z) < 10:
        pytest.skip("IMU 数据不足以进行 FFT 分析。")

    timestamps = np.array(timestamps)
    accel_z = np.array(accel_z)

    accel_z_centered = accel_z - np.mean(accel_z)
    dt = np.mean(np.diff(timestamps))
    n = len(accel_z_centered)
    freqs = np.fft.fftfreq(n, d=dt)
    fft_values = np.fft.fft(accel_z_centered)

    positive_freqs = freqs[freqs > 0]
    amplitudes = np.abs(fft_values)[freqs > 0] * 2.0 / n

    plt.figure(figsize=(10, 5))
    plt.plot(positive_freqs, amplitudes, color="purple", alpha=0.8)
    plt.title("IMU Z-Axis Vibration FFT Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (m/s²)")
    plt.grid(True)
    plt.xlim(0, 100)  # 重点关注 0-100Hz 的频段

    max_amp_idx = np.argmax(amplitudes)
    max_freq = positive_freqs[max_amp_idx]
    max_amp = amplitudes[max_amp_idx]
    plt.annotate(
        f"Peak: {max_freq:.1f}Hz, {max_amp:.2f}m/s²",
        xy=(max_freq, max_amp),
        xytext=(max_freq + 5, max_amp),
        arrowprops=dict(facecolor="black", shrink=0.05),
    )

    plt.savefig(f"{report_dir}/imu_fft_spectrum.png")
    plt.close()

    high_freq_mask = positive_freqs > 15.0
    if np.any(high_freq_mask):
        max_high_freq_amp = np.max(amplitudes[high_freq_mask])
        assert (
            max_high_freq_amp < 2.0
        ), f"检测到机架异常共振! 峰值幅值: {max_high_freq_amp:.3f} m/s²"
