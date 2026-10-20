import pytest
import rosbag
import os
import numpy as np

def test_eight_figure_tracking_rmse():
    """提取 Setpoint 与实际速度，通过时间戳插值对齐后计算严谨的 RMSE 追踪误差"""
    bag_path = '/workspace/tests_auto/data/flight_sample.bag'
    
    if not os.path.exists(bag_path):
        pytest.skip("未找到飞行日志，跳过此测试。")
        
    actual_t, actual_vx = [], []
    expected_t, expected_vx = [], []
    
    with rosbag.Bag(bag_path, 'r') as bag:
        for topic, msg, t in bag.read_messages(topics=['/mavros/local_position/velocity_local', '/mavros/setpoint_velocity/cmd_vel']):
            if 'local_position' in topic:
                actual_t.append(t.to_sec())
                actual_vx.append(msg.twist.linear.x)
            else:
                expected_t.append(t.to_sec())
                expected_vx.append(msg.twist.linear.x)
                
    # 容错处理：如果 bag 包里压根没录制 setpoint 话题，则优雅跳过而不是暴毙
    if not expected_t:
        pytest.skip("包内未找到 /mavros/setpoint_velocity/cmd_vel 话题，无法计算 RMSE。")
        
    # 核心算法：指令频率与传感器频率不同，利用一维线性插值将期望速度对齐到实际传感器的时间轴上
    expected_vx_aligned = np.interp(actual_t, expected_t, expected_vx)
    
    # 计算真正的时序 RMSE
    rmse = np.sqrt(np.mean((expected_vx_aligned - np.array(actual_vx))**2))
    
    # 设定严苛的 0.3 m/s 跟踪误差红线
    assert rmse < 0.3, f"X轴速度追踪 RMSE 超出 0.3m/s 安全阈值，当前为: {rmse:.4f}"
