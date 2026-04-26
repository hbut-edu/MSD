import pytest
# 尝试导入尚未被创建的模块和函数
from gacha_calculator import calculate_five_star_probability

def test_base_probability():
    """测试 1-73 抽的基础概率区间"""
    assert calculate_five_star_probability(1) == 0.006
    assert calculate_five_star_probability(73) == 0.006

def test_soft_pity_probability():
    """测试 74 抽及之后的软保底概率递增区间"""
    # 第 74 抽：0.006 + 0.06 = 0.066
    assert calculate_five_star_probability(74) == 0.066
    assert calculate_five_star_probability(75) == 0.126

def test_hard_pity_probability():
    """测试 90 抽的绝对硬保底"""
    assert calculate_five_star_probability(90) == 1.0

def test_invalid_pulls():
    """测试非法输入的异常处理边界"""
    with pytest.raises(ValueError):
        calculate_five_star_probability(0)
    with pytest.raises(ValueError):
        calculate_five_star_probability(91)
