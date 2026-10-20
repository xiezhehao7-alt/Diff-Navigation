import pytest
import rosbag
import os
import numpy as np

def test_eight_figure_tracking_accuracy():
    """从真实 rosbag 中提取 8 字航线的速度数据，验证跟踪 RMSE"""
    bag_path = '/workspace/tests_auto/data/flight_sample.bag'
    
    # 如果当前 CI 环境还没放进去真实的 bag，就先跳过这个测试，防止流水线直接报错
    if not os.path.exists(bag_path):
        pytest.skip(f"未找到飞行日志 {bag_path}，跳过此测试。请上传包含 /mavros 话题的截取包。")
        
    actual_vx = []
    
    # 直接利用 rosbag API 离线解析数据，非常稳定且速度极快
    with rosbag.Bag(bag_path, 'r') as bag:
        for topic, msg, t in bag.read_messages(topics=['/mavros/local_position/velocity_local']):
            actual_vx.append(msg.twist.linear.x)
            
    # 假设这里引入你计算参考速度的逻辑（此处用简化的基准值演示）
    actual_vx = np.array(actual_vx)
    expected_vx = np.ones_like(actual_vx) * 1.5  # 假设期望 X 轴速度为 1.5m/s
    
    rmse = np.sqrt(np.mean((expected_vx - actual_vx)**2))
    
    # 严格把控航线追踪质量
    assert rmse < 0.2, f"8 字航线 X 轴速度跟踪 RMSE 超标: {rmse:.4f}"
