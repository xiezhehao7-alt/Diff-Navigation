# 🚀 CI/CD 版本演进实验指南

这个实验将帮你理解 CI/CD 在真实开发中的工作方式。

## 📌 实验目标

模拟从基础版本逐步演进到完整功能版本的开发过程，观察 CI/CD 在每个阶段的自动化测试。

## 🎯 实验分支

已创建实验分支：`experiment/version-evolution`

## 📝 实验步骤

### 阶段 1: 推送基础版本

```bash
# 确保 SSH agent 已加载密钥
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519

# 切换到实验分支
cd /home/xzh006268/uav-ci-test
git checkout experiment/version-evolution

# 推送基础版本（已创建提交）
git push origin experiment/version-evolution
```

**观察点**：
- 访问 https://github.com/xiezhehao7-alt/Diff-Navigation/actions
- 你会看到 CI/CD 自动触发
- 观察"代码质量检查"和"构建与测试"阶段的运行

---

### 阶段 2: 添加速度跟踪测试

```bash
# 创建速度跟踪测试
cat > tests_auto/test_velocity.py << 'EOF'
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
EOF

# 提交并推送
git add tests_auto/test_velocity.py
git commit -m "feat: 添加速度跟踪和稳定性测试"
git push origin experiment/version-evolution
```

**观察点**：
- 再次访问 Actions 页面
- 新的提交会触发新一轮 CI/CD
- 观察测试数量增加，所有测试都应该通过

---

### 阶段 3: 添加 ROS 集成测试

```bash
# 创建 ROS 集成测试
cat > tests_auto/test_ros_integration.py << 'EOF'
import pytest

def test_ros_environment():
    """验证 ROS 环境"""
    import os
    ros_distro = os.environ.get('ROS_DISTRO', 'unknown')
    assert ros_distro != 'unknown', "ROS_DISTRO 未设置"

def test_dependencies():
    """验证关键依赖"""
    import numpy
    import requests
    assert numpy.__version__ is not None
    assert requests.__version__ is not None
EOF

# 提交并推送
git add tests_auto/test_ros_integration.py
git commit -m "feat: 添加 ROS 环境和依赖集成测试"
git push origin experiment/version-evolution
```

**观察点**：
- 观察 CI/CD 如何验证 ROS 环境
- 测试应该在 Docker 容器中通过

---

### 阶段 4: 添加可视化报告功能

```bash
# 更新 requirements.txt
echo "pytest-html==4.1.1" >> tests_auto/requirements.txt

# 提交并推送
git add tests_auto/requirements.txt
git commit -m "feat: 集成 pytest-html 支持测试报告可视化"
git push origin experiment/version-evolution
```

**观察点**：
- CI/CD 会自动安装新依赖
- 查看 Actions 的 Artifacts 部分，下载测试报告

---

### 阶段 5: 模拟发布 V1.4.0

```bash
# 打版本标签
git tag v1.4.0-experiment
git push origin v1.4.0-experiment
```

**观察点**：
- 🎉 这会触发**完整的发布流水线**
- 包括：代码检查 → 构建测试 → 集成测试 → 构建发布版本 → 部署
- 观察 Docker 镜像如何被构建并推送到 GitHub Container Registry

---

## 📊 查看 CI/CD 运行结果

### 方法 1: 浏览器查看（推荐）

```
https://github.com/xiezhehao7-alt/Diff-Navigation/actions
```

你会看到：
- 🟢 绿色勾：测试通过
- 🔴 红色叉：测试失败
- 🟡 黄色圈：正在运行
- 点击任意运行可查看详细日志

### 方法 2: 命令行查看

```bash
# 查看最近的运行
gh run list --limit 10

# 实时查看当前运行
gh run watch

# 查看特定运行的日志
gh run view <run-id> --log
```

---

## 🎓 关键理解点

### 1. 自动化触发
每次 `git push` 都会自动触发 CI/CD，你不需要手动执行任何测试命令。

### 2. 环境一致性
所有测试都在 Docker 容器中运行，确保本地、CI、生产环境完全一致。

### 3. 快速反馈
如果某次提交破坏了测试，GitHub 会立即显示红色 ❌，阻止有问题的代码合并。

### 4. 发布自动化
打 tag 后，构建、测试、部署全自动完成，减少人为错误。

---

## 🔄 实验后清理（可选）

如果你想清理实验分支：

```bash
# 切回 dev 分支
git checkout dev

# 删除本地实验分支
git branch -D experiment/version-evolution

# 删除远程实验分支
git push origin --delete experiment/version-evolution

# 删除实验 tag
git tag -d v1.4.0-experiment
git push origin --delete v1.4.0-experiment
```

---

## 💡 下一步

完成这个实验后，你应该能理解：
1. CI/CD 如何在每次提交时自动测试
2. 如何通过 GitHub Actions 查看测试结果
3. 版本发布流程如何自动化
4. 为什么 CI/CD 对团队协作和代码质量如此重要

现在开始实验吧！🚀
