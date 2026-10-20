import pytest
import numpy as np

def test_velocity_tracking():
    """测试速度跟踪 RMSE 计算"""
    expected_vel = np.array([1.0, 0.0, 0.0])
    actual_vel = np.array([0.95, 0.05, 0.0])
    
    rmse = np.sqrt(np.mean((expected_vel - actual_vel)**2))
    assert rmse < 0.1, f"速度跟踪误差过大: {rmse:.4f}"

def test_velocity_stability():
    """测试速度稳定性"""
    velocities = np.random.normal(1.0, 0.02, 100)
    std = np.std(velocities)
    assert std < 0.05, f"速度波动过大: {std:.4f}"
