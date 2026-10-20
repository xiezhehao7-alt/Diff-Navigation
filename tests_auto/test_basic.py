import pytest

def test_basic_calculation():
    """基础测试: 验证基本计算功能"""
    assert 1 + 1 == 2

def test_environment():
    """验证测试环境是否正常"""
    import sys
    assert sys.version_info.major == 3
