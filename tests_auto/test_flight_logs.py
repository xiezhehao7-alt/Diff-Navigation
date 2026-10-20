import pytest
import rosbag
import os
import numpy as np
import matplotlib.pyplot as plt

def test_eight_figure_tracking_rmse():
    bag_path = '/workspace/tests_auto/data/flight_sample.bag'
    report_dir = '/workspace/tests_auto/reports'
    os.makedirs(report_dir, exist_ok=True)
    
    if not os.path.exists(bag_path):
        pytest.skip("未找到飞行日志，跳过此测试。")
        
    actual_t, actual_vx, expected_t, expected_vx = [], [], [], []
    
    with rosbag.Bag(bag_path, 'r') as bag:
        for topic, msg, t in bag.read_messages(topics=['/mavros/local_position/velocity_local', '/mavros/setpoint_velocity/cmd_vel']):
            if 'local_position' in topic:
                actual_t.append(t.to_sec())
                actual_vx.append(msg.twist.linear.x)
            else:
                expected_t.append(t.to_sec())
                expected_vx.append(msg.twist.linear.x)
                
    if not expected_t:
        pytest.skip("包内未找到 setpoint 话题，无法计算 RMSE。")
        
    # 时间戳对齐与 RMSE 计算
    expected_vx_aligned = np.interp(actual_t, expected_t, expected_vx)
    rmse = np.sqrt(np.mean((expected_vx_aligned - np.array(actual_vx))**2))
    
    # --- 新增：可视化绘图逻辑 ---
    plt.figure(figsize=(10, 5))
    # 为了图表美观，将时间轴归零
    t_zero = actual_t[0] 
    plt.plot(np.array(actual_t) - t_zero, expected_vx_aligned, label='Expected Velocity (cmd_vel)', linestyle='--')
    plt.plot(np.array(actual_t) - t_zero, actual_vx, label='Actual Velocity (local_position)', alpha=0.7)
    
    plt.title(f'X-Axis Velocity Tracking (RMSE: {rmse:.4f} m/s)')
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (m/s)')
    plt.legend()
    plt.grid(True)
    
    # 保存图表到报告文件夹
    plt.savefig(f'{report_dir}/velocity_tracking.png')
    plt.close()
    
    assert rmse < 0.3, f"X轴速度追踪 RMSE 超出安全阈值: {rmse:.4f}"

def test_imu_vibration_fft_visualized():
    """对 IMU Z轴加速度进行 FFT 频域分析，断言异常振动并生成频谱图"""
    bag_path = '/workspace/tests_auto/data/flight_sample.bag'
    report_dir = '/workspace/tests_auto/reports'
    
    if not os.path.exists(bag_path):
        pytest.skip("未找到飞行日志，跳过 IMU 振动分析。")
        
    timestamps, accel_z = [], []
    
    with rosbag.Bag(bag_path, 'r') as bag:
        for topic, msg, t in bag.read_messages(topics=['/mavros/imu/data']):
            timestamps.append(t.to_sec())
            accel_z.append(msg.linear_acceleration.z)
            
    if len(accel_z) < 10:
        pytest.skip("IMU 数据不足以进行 FFT 分析。")
        
    timestamps = np.array(timestamps)
    accel_z = np.array(accel_z)
    
    # 消除重力直流分量并计算 FFT
    accel_z_centered = accel_z - np.mean(accel_z)
    dt = np.mean(np.diff(timestamps))
    n = len(accel_z_centered)
    freqs = np.fft.fftfreq(n, d=dt)
    fft_values = np.fft.fft(accel_z_centered)
    
    positive_freqs = freqs[freqs > 0]
    amplitudes = np.abs(fft_values)[freqs > 0] * 2.0 / n
    
    # 绘图逻辑：生成 FFT 频谱图
    plt.figure(figsize=(10, 5))
    plt.plot(positive_freqs, amplitudes, color='purple', alpha=0.8)
    plt.title('IMU Z-Axis Vibration FFT Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (m/s²)')
    plt.grid(True)
    plt.xlim(0, 100) # 重点关注 0-100Hz 的频段
    
    # 标出峰值
    max_amp_idx = np.argmax(amplitudes)
    max_freq = positive_freqs[max_amp_idx]
    max_amp = amplitudes[max_amp_idx]
    plt.annotate(f'Peak: {max_freq:.1f}Hz, {max_amp:.2f}m/s²', 
                 xy=(max_freq, max_amp), xytext=(max_freq+5, max_amp),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.savefig(f'{report_dir}/imu_fft_spectrum.png')
    plt.close()
    
    # 业务断言：高频段（>15Hz）振动幅值不能超过 2.0
    high_freq_mask = positive_freqs > 15.0
    if np.any(high_freq_mask):
        max_high_freq_amp = np.max(amplitudes[high_freq_mask])
        assert max_high_freq_amp < 2.0, f"检测到机架异常共振! 峰值幅值: {max_high_freq_amp:.3f} m/s²"

def test_imu_vibration_fft_visualized():
    """对 IMU Z轴加速度进行 FFT 频域分析，断言异常振动并生成频谱图"""
    bag_path = '/workspace/tests_auto/data/flight_sample.bag'
    report_dir = '/workspace/tests_auto/reports'
    
    if not os.path.exists(bag_path):
        pytest.skip("未找到飞行日志，跳过 IMU 振动分析。")
        
    timestamps, accel_z = [], []
    
    with rosbag.Bag(bag_path, 'r') as bag:
        for topic, msg, t in bag.read_messages(topics=['/mavros/imu/data']):
            timestamps.append(t.to_sec())
            accel_z.append(msg.linear_acceleration.z)
            
    if len(accel_z) < 10:
        pytest.skip("IMU 数据不足以进行 FFT 分析。")
        
    timestamps = np.array(timestamps)
    accel_z = np.array(accel_z)
    
    # 消除重力直流分量并计算 FFT
    accel_z_centered = accel_z - np.mean(accel_z)
    dt = np.mean(np.diff(timestamps))
    n = len(accel_z_centered)
    freqs = np.fft.fftfreq(n, d=dt)
    fft_values = np.fft.fft(accel_z_centered)
    
    positive_freqs = freqs[freqs > 0]
    amplitudes = np.abs(fft_values)[freqs > 0] * 2.0 / n
    
    # 绘图逻辑：生成 FFT 频谱图
    plt.figure(figsize=(10, 5))
    plt.plot(positive_freqs, amplitudes, color='purple', alpha=0.8)
    plt.title('IMU Z-Axis Vibration FFT Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (m/s²)')
    plt.grid(True)
    plt.xlim(0, 100) # 重点关注 0-100Hz 的频段
    
    # 标出峰值
    max_amp_idx = np.argmax(amplitudes)
    max_freq = positive_freqs[max_amp_idx]
    max_amp = amplitudes[max_amp_idx]
    plt.annotate(f'Peak: {max_freq:.1f}Hz, {max_amp:.2f}m/s²', 
                 xy=(max_freq, max_amp), xytext=(max_freq+5, max_amp),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.savefig(f'{report_dir}/imu_fft_spectrum.png')
    plt.close()
    
    # 业务断言：高频段（>15Hz）振动幅值不能超过 2.0
    high_freq_mask = positive_freqs > 15.0
    if np.any(high_freq_mask):
        max_high_freq_amp = np.max(amplitudes[high_freq_mask])
        assert max_high_freq_amp < 2.0, f"检测到机架异常共振! 峰值幅值: {max_high_freq_amp:.3f} m/s²"
