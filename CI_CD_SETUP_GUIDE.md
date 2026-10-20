# 🚀 从零开始搭建 CI/CD 流水线指南

## 📋 项目概况

**项目名称**: Diff-Navigation (无人机差分导航系统)  
**当前版本**: V1.4.0  
**技术栈**: ROS Noetic + Python + Docker

---

## 🎯 CI/CD 流水线设计

### 流水线阶段

```
┌─────────────────┐
│ 代码质量检查     │ ← Black, Flake8, Pylint
└────────┬────────┘
         ↓
┌─────────────────┐
│ 构建与测试       │ ← Docker 构建, ROS 编译, pytest
└────────┬────────┘
         ↓
┌─────────────────┐
│ 集成测试         │ ← 完整飞行流程验证
└────────┬────────┘
         ↓
┌─────────────────┐
│ 构建发布版本     │ ← 仅 tag 触发, 推送到 GHCR
└────────┬────────┘
         ↓
┌─────────────────┐
│ 部署             │ ← 自动化部署
└─────────────────┘
```

### 触发条件

- **push** 到 `dev` 或 `main` 分支
- **pull_request** 到 `dev` 或 `main` 分支
- **打 tag** (格式: `v*`)
- **手动触发** (workflow_dispatch)

---

## 📝 当前项目测试文件

```
tests_auto/
├── Dockerfile              # Docker 构建文件
├── requirements.txt        # Python 依赖
├── test_nav_logic.py       # 速度跟踪 RMSE 测试
└── test_flight_logs.py     # ROS bag 数据分析测试
    └── test_eight_figure_tracking_variance_visualized()
    └── test_imu_vibration_fft_visualized()
```

---

## ✅ 完整 CI/CD 配置

你的 CI/CD 配置文件位于: `.github/workflows/ci.yml`

### 配置要点

1. **使用 Docker 确保环境一致性**
   - 基础镜像: `osrf/ros:noetic-desktop-focal`
   - 包含 ROS Noetic + Python 3 + pytest

2. **多阶段流水线**
   - 代码质量检查独立运行
   - 构建测试依赖代码质量检查通过
   - 集成测试依赖构建测试通过
   - 发布和部署仅在打 tag 时触发

3. **测试报告自动化**
   - 生成 HTML 测试报告
   - 生成测试覆盖率报告
   - 自动归档为 Artifacts (保留 30 天)

4. **Docker 缓存优化**
   - 使用 GitHub Actions 缓存
   - 加速构建过程

---

## 🚀 使用流程

### 日常开发流程

```bash
# 1. 修改代码
vim tests_auto/test_nav_logic.py

# 2. 本地测试 (可选但推荐)
docker build -t diff-nav-test:latest -f tests_auto/Dockerfile .
docker run --rm diff-nav-test:latest /bin/bash -c \
  "source /opt/ros/noetic/setup.bash && pytest /workspace/tests_auto/ -v"

# 3. 提交并推送
git add .
git commit -m "feat: 优化速度跟踪算法"
git push origin dev

# 4. 查看 CI/CD 运行结果
# 访问: https://github.com/你的用户名/Diff-Navigation/actions
```

### 发布新版本流程

```bash
# 1. 确保所有测试通过
git push origin dev

# 2. 打版本标签
git tag v1.5.0
git push origin v1.5.0

# 3. GitHub Actions 自动执行:
#    ✅ 所有测试
#    ✅ 构建 Docker 镜像
#    ✅ 推送到 GitHub Container Registry
#    ✅ 自动部署
```

---

## 📊 查看 CI/CD 结果

### 浏览器查看

访问: `https://github.com/你的用户名/Diff-Navigation/actions`

你会看到:
- 🟢 绿色勾: 测试通过
- 🔴 红色叉: 测试失败
- 🟡 黄色圈: 正在运行

点击任意运行可查看详细日志和下载测试报告。

### 命令行查看

```bash
# 安装 GitHub CLI (如果还没安装)
# 参考: https://cli.github.com/

# 查看最近的运行
gh run list --limit 10

# 实时查看当前运行
gh run watch

# 查看特定运行的日志
gh run view <run-id> --log
```

---

## 🎓 CI/CD 的核心价值

### 1. **自动化测试**
- 每次提交都自动运行所有测试
- 防止有问题的代码合并到主分支
- 无需记住手动运行测试的步骤

### 2. **环境一致性**
- Docker 确保本地、CI、生产环境完全一致
- 避免"在我机器上能跑"的问题

### 3. **快速反馈**
- 代码推送后立即知道是否通过测试
- 问题及早发现,修复成本更低

### 4. **发布自动化**
- 打 tag 后自动构建、测试、部署
- 减少人为错误,提高发布效率

### 5. **代码质量保证**
- 自动检查代码格式和风格
- 确保团队代码风格一致

---

## 🔧 故障排查

### 测试失败怎么办?

1. **查看失败日志**
   - 在 Actions 页面点击失败的运行
   - 查看哪个阶段失败
   - 阅读详细错误信息

2. **本地复现**
   ```bash
   # 使用完全相同的 Docker 环境
   docker build -t diff-nav-test:latest -f tests_auto/Dockerfile .
   docker run --rm diff-nav-test:latest /bin/bash -c \
     "source /opt/ros/noetic/setup.bash && pytest /workspace/tests_auto/ -v"
   ```

3. **修复并重新推送**
   ```bash
   # 修复问题
   vim tests_auto/test_nav_logic.py
   
   # 重新提交
   git add .
   git commit -m "fix: 修复速度跟踪测试失败"
   git push origin dev
   ```

### Docker 构建缓慢?

- GitHub Actions 已启用缓存
- 首次构建较慢 (3-5 分钟)
- 后续构建使用缓存 (1-2 分钟)

---

## 📚 相关资源

- **GitHub Actions 文档**: https://docs.github.com/actions
- **Docker 官方文档**: https://docs.docker.com/
- **ROS Noetic 文档**: http://wiki.ros.org/noetic
- **pytest 文档**: https://docs.pytest.org/

---

## 🎯 下一步

1. **推送代码触发 CI/CD**
   ```bash
   git push origin dev
   ```

2. **访问 Actions 页面观察运行**
   ```
   https://github.com/你的用户名/Diff-Navigation/actions
   ```

3. **测试发布流程**
   ```bash
   git tag v1.4.0
   git push origin v1.4.0
   ```

祝你的 CI/CD 之旅顺利! 🚀
