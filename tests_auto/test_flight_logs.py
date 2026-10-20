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
