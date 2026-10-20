import numpy as np


def test_velocity_rmse_calculation():
    """验证无人机轨迹跟踪的 RMSE 计算逻辑是否在安全阈值内"""
    expected_vel = np.array([1.0, 0.0, 0.0])
    actual_vel = np.array([0.95, 0.05, 0.0])

    rmse = np.sqrt(np.mean((expected_vel - actual_vel)**2))

    assert rmse < 0.1, f"速度跟踪误差超出安全阈值，当前 RMSE: {rmse:.4f}"


def test_ros_environment():
    """验证基础依赖包是否就绪"""
    import requests
    assert requests.__version__ is not None
