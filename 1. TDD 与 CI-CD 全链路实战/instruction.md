# 《现代软件开发技术》上机实验手册：AI 赋能下的 TDD 与 CI/CD 全链路实践

# 实验主题

AI时代的工程安全网——Git协同、CI/CD与TDD测试驱动开发

# 实验目标

1. 理解AI时代软件工程的自动化验证思维
2. 掌握Git版本控制与协同开发流程
3. 学会配置Gitee平台及SSH密钥认证
4. 掌握CI/CD流水线的配置与使用方法
5. 理解并实践TDD测试驱动开发方法论
6. 学会编写测试用例并进行代码验证
7. 掌握代码质量检查与自动化测试流程
8. 建立对AI生成代码的正确性约束能力

# 📅 课程概览 (Total: 240 Mins)

| 时间段 | 教学环节 | 核心目标 | 关键技术栈 |
| :--- | :--- | :--- | :--- |
| **0-30'** | **模块一：环境基建与理论导入** | 完成Git、Trae IDE安装配置，理解AI时代软件工程新范式。 | Git, Trae IDE, Gitee |
| **30-70'** | **模块二：云端平台与仓库搭建** | 注册Gitee账号，配置SSH密钥，创建项目仓库。 | Gitee, SSH密钥, 仓库管理 |
| **70-110'** | **模块三：CI/CD流水线配置** | 开启Gitee Go服务，编写流水线配置文件。 | Gitee Go, YAML, 自动化 |
| **110-150'** | **模块四：TDD测试驱动开发** | 实践测试先行方法论，编写测试用例和业务代码。 | pytest, TDD, 单元测试 |
| **150-190'** | **模块五：AI辅助开发与验证** | 使用Trae AI生成代码，建立自动化验证约束。 | AI辅助编程, 代码审查 |
| **190-240'** | **模块六：综合实战与结课** | 完成完整项目实战，构建工程化思维。 | 项目实战, 工程化思维 |

---

## 实验环境与先决条件
*   **操作系统**：Windows 10/11 或 macOS
*   **网络要求**：全过程需保持互联网畅通
*   **核心工具链**：Git、Trae IDE、Gitee、Gitee Go

---

## 第一阶段：本地开发环境基建 (软件安装与配置)

### 1. 安装与配置版本控制系统 Git
Git 是现代软件工程的基石。
*   **Windows 环境**：访问 Git 官网下载并按默认选项安装 Git for Windows。
*   **macOS 环境**：打开终端（Terminal），输入 `git --version`，若未安装，系统会自动弹出命令行开发者工具安装提示，按提示安装即可。

**全局变量配置**：
打开命令行（Windows 使用 Git Bash，macOS 使用 Terminal），执行以下命令配置身份信息（将记录在每一次代码提交中）：
```bash
git config --global user.name "你的真实姓名"
git config --global user.email "你的邮箱@example.com"
# 配置默认分支名，推荐统一使用 master
git config --global init.defaultBranch master
```

### 2. 配置 SSH 公钥（工业界免密通信标准）
为了实现本地 IDE 到云端代码库的免密推送，必须配置 SSH 密钥对。
1.  在本地命令行中生成密钥（一路回车默认即可）：
    ```bash
    ssh-keygen -t ed25519 -C "你的邮箱@example.com"
    ```
2.  查看并复制生成的公钥内容：
    *   Windows: `cat ~/.ssh/id_ed25519.pub`
    *   macOS: `cat ~/.ssh/id_ed25519.pub`
3.  **后续步骤**：在注册 Gitee 后，将此公钥内容配置到 Gitee 账号中。

### 3. 安装字节跳动 Trae IDE
Trae 是一款原生的 AI IDE，深度集成了大语言模型，是我们本次"指挥 AI 写代码"的主控台。
*   访问 Trae 官方网站，下载对应操作系统的安装包并完成安装。
*   启动 Trae，注册并登录账号以获取完整的 AI 辅助配额。

---

## 第二阶段：云端基础设施搭建 (Gitee 平台配置)

### 1. 注册 Gitee 账号与实名认证
*   访问 Gitee 官网 (gitee.com) 完成账号注册。
*   进入个人设置中心，**完成实名认证**。Gitee Go（云端流水线）必须在账号实名认证后才能分配免费的云计算资源和构建时长。
*   进入设置 -> **SSH 公钥**，将第一阶段复制的公钥内容粘贴进去并保存。

### 2. 创建课程项目仓库
1.  在 Gitee 首页点击右上角的 **"+"** -> **"新建仓库"**。
2.  仓库名称填写：`genshin-gacha-tdd`。
3.  设为**公开**。
4.  **注意**：不要勾选任何"初始化仓库"选项（如 README 或 .gitignore），创建一个纯空仓库。

### 3. 开启 Gitee Go 云端流水线服务
1.  进入刚创建好的 `genshin-gacha-tdd` 仓库主页。
2.  点击仓库顶部导航栏的 **"Gitee Go 或 流水线"** 标签。
3.  点击 **"开通服务"**。开通成功后，无需使用页面上的模板，直接关闭页面，我们将使用代码（Pipeline as Code）来定义流水线。

---

## 第三阶段：项目克隆、分支管理与 CI/CD 剧本装配

本阶段提供**命令行（CLI）**与**IDE可视化（GUI）**两种操作方式，实际开发中可结合使用。

### 1. 在 Trae IDE 中拉取代码并创建分支

**方式 A：命令行操作 (推荐理解底层逻辑)**
1. 打开 Trae IDE，点击菜单栏 `Terminal` -> `New Terminal`。
2. 执行克隆与分支创建：
```bash
# 替换为你的 SSH 仓库地址
git clone git@gitee.com:你的用户名/genshin-gacha-tdd.git
cd genshin-gacha-tdd

# 初始化首次提交
echo "# 原神抽卡 TDD 实验" > README.md
git add README.md
git commit -m "docs: add Initial README"
git branch -M master
git push -u origin master

# 创建并切换到日常开发分支
git checkout -b develop
```

**方式 B：Trae IDE 可视化操作 (进阶效率首选)**
1. **克隆**：按 `Ctrl+Shift+P` (Win) 或 `Cmd+Shift+P` (Mac) 唤醒命令面板，输入 `Git: Clone`，粘贴 SSH 仓库地址，选择本地文件夹保存，点击弹出的 **Open** 打开项目。
2. **建分支**：点击 IDE 左下角的状态栏分支名（如 `master`），选择 **+ Create new branch...**，输入 `develop` 并回车，完成分支创建与切换。

### 2. 编写 CI/CD 流水线剧本
在项目根目录下创建一个名为 `.workflow` 的文件夹，并在其中新建文件 `python-ci.yml`。输入以下 Gitee Go 流水线配置：

```yaml
version: '1.0'
name: gacha-tdd-pipeline
displayName: 原神抽卡逻辑 TDD 自动化流水线
triggers:
  trigger: auto
  push:
    branches:
      - develop
stages:
  - name: stage-ci
    displayName: 语法与逻辑测试
    strategy: naturally
    trigger: auto
    executor: []
    steps:
      - step: build@python
        name: run-pytest
        displayName: 执行测试拦截
        pythonVersion: 3.9
        working-directory: .  # 添加工作目录配置，确保CI/CD能正确找到测试文件
        commands:
          # 使用清华源加速依赖安装
          - pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
          # 检查代码规范，阻断严重语法错误
          - flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          # 运行 pytest，不通过则流水线标红失败
          - pytest test_business_logic.py -v
```

---

## 第四阶段：TDD 测试驱动对抗实验

**业务需求：开发《原神》祈愿保底概率计算器**
1. 基础五星角色出率为 0.6%。
2. 最多 90 次祈愿必定获取五星角色（硬保底）。
3. 从第 74 抽开始，五星出率每抽递增 6%（软保底）。

### 步骤 0：创建项目配置文件 <!-- ai修正: 添加项目配置文件创建步骤 -->

#### 创建依赖管理文件
在项目根目录创建 `requirements.txt`，内容如下：
```
pytest>=7.0.0
flake8>=5.0.0
```

#### 创建 pytest 配置文件
在项目根目录创建 `pytest.ini`，内容如下：
```ini
[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

#### 创建 .gitignore 文件
在项目根目录创建 `.gitignore`，内容如下：
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

### 步骤 1：编写测试用例（先写测试，后写实现）

在项目根目录创建 `test_business_logic.py`，内容如下：

```python
import pytest
from business_logic import calculate_gacha_probability

class TestGachaProbability:
    def test_base_probability(self):
        """测试基础概率：1-73抽应为0.6%"""
        for pull in range(1, 74):
            prob = calculate_gacha_probability(pull)
            assert prob == 0.006, f"第{pull}抽概率错误"

    def test_soft_pity_start(self):
        """测试软保底开始：第74抽概率应为6.6%"""
        prob = calculate_gacha_probability(74)
        assert prob == 0.066, "第74抽概率错误"

    def test_soft_pity_increase(self):
        """测试软保底递增：第74-89抽每抽递增6%"""
        expected_prob = 0.066
        for pull in range(74, 90):
            prob = calculate_gacha_probability(pull)
            assert prob == expected_prob, f"第{pull}抽概率错误"
            expected_prob += 0.06

    def test_hard_pity_guarantee(self):
        """测试硬保底：第90抽必定获取（概率100%）"""
        prob = calculate_gacha_probability(90)
        assert prob == 1.0, "第90抽概率错误"

    def test_invalid_pull_number(self):
        """测试无效的抽数：0或负数应抛出异常"""
        with pytest.raises(ValueError):
            calculate_gacha_probability(0)
        
        with pytest.raises(ValueError):
            calculate_gacha_probability(-1)

    def test_pull_over_90(self):
        """测试超过90抽：超过90抽应重置为新一轮保底"""
        prob = calculate_gacha_probability(91)
        assert prob == 0.006, "第91抽（新一轮第1抽）概率错误"
```

### 步骤 2：提交测试用例，触发 CI/CD 拦截

1. **提交测试用例到 develop 分支**：
```bash
git add requirements.txt pytest.ini .gitignore test_business_logic.py
git commit -m "test: add gacha probability test cases"
git push origin develop
```

2. **观察 CI/CD 流水线**：
   - 访问 Gitee 仓库页面，点击 `Gitee Go` 标签
   - **预期结果**：流水线标红失败（因为 `business_logic.py` 还不存在）
   - **验证要点**：确认 CI/CD 能够正确拦截错误提交

### 步骤 3：使用 AI 生成业务逻辑实现

1. 在项目根目录创建 `business_logic.py` 文件
2. 使用 Trae IDE 的 AI 功能，根据业务需求生成实现代码
3. **AI 提示词参考**：
```
请帮我实现一个原神抽卡概率计算器，需求如下：
1. 基础五星角色出率为 0.6%（0.006）
2. 最多 90 次祈愿必定获取五星角色（硬保底）
3. 从第 74 抽开始，五星出率每抽递增 6%（软保底）
4. 超过 90 抽后重置为新一轮保底
5. 输入为抽数（正整数），输出为当前抽的概率

要求：
- 函数名为 calculate_gacha_probability(pull_num)
- 参数 pull_num 为正整数
- 返回值为 float 类型，表示概率
- 对于无效输入（0或负数）抛出 ValueError 异常
```

### 步骤 4：本地验证 AI 生成代码

在本地运行测试用例，验证 AI 生成的代码是否正确：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest test_business_logic.py -v
```

**预期结果**：所有测试用例都应该通过。

### 步骤 5：提交业务逻辑，触发 CI/CD 验证

1. **提交业务逻辑到 develop 分支**：
```bash
git add business_logic.py
git commit -m "feat: implement gacha probability calculation"
git push origin develop
```

2. **观察 CI/CD 流水线**：
   - 访问 Gitee 仓库页面，点击 `Gitee Go` 标签
   - **预期结果**：流水线全部通过（绿色）
   - **验证要点**：确认 AI 生成的代码符合测试用例要求

### 步骤 6：创建 Pull Request 并合并到 master

1. **创建 Pull Request**：
   - 在 Gitee 仓库页面，点击 `Pull Requests` -> `新建 Pull Request`
   - 源分支：`develop`，目标分支：`master`
   - 填写标题和描述，点击 `创建`

2. **代码审查与合并**：
   - 审查代码变更
   - 确认所有 CI/CD 检查通过
   - 点击 `合并` 按钮

---

## 第五阶段：实验总结与思考

### 实验成果验证

1. ✅ Git 版本控制环境配置完成
2. ✅ Gitee 平台配置完成（SSH 密钥、仓库、流水线）
3. ✅ CI/CD 流水线配置完成并成功运行
4. ✅ TDD 测试驱动开发流程实践完成
5. ✅ AI 生成代码通过测试验证

### 关键思考问题

1. **为什么要先写测试用例，再写实现代码？**
2. **CI/CD 流水线在 AI 时代的作用是什么？**
3. **如何确保 AI 生成的代码符合业务需求和质量标准？**
4. **TDD 测试驱动开发对 AI 辅助编程有什么约束作用？**

### 实验延伸与拓展

1. **尝试更复杂的业务逻辑**：例如实现武器池保底、角色池继承保底等高级功能
2. **添加更多测试用例**：增加边界测试、性能测试、异常测试
3. **优化 CI/CD 流水线**：添加代码覆盖率报告、性能测试、安全扫描
4. **实践团队协作**：邀请同学加入项目，模拟真实团队开发流程

---

## 常见问题与解决方案

### Q1: SSH 密钥配置失败怎么办？
**A**: 
- 检查密钥是否正确生成（`ls ~/.ssh/`）
- 确认公钥内容完整复制（从 `ssh-ed25519` 开始到邮箱结束）
- 测试 SSH 连接：`ssh -T git@gitee.com`

### Q2: CI/CD 流水线一直失败？
**A**:
- 检查 `.workflow/python-ci.yml` 配置是否正确
- 确认 `requirements.txt` 包含所有依赖
- 查看流水线日志，定位具体错误原因

### Q3: AI 生成的代码通不过测试？
**A**:
- 检查测试用例是否正确
- 重新生成更详细的提示词
- 手动调试和修正 AI 生成的代码
- 考虑将测试失败的用例反馈给 AI，让它重新生成

### Q4: 如何查看流水线日志？
**A**:
- 在 Gitee 仓库页面点击 `Gitee Go`
- 点击对应的流水线执行记录
- 查看每个步骤的详细日志输出

---

## 附录：常用 Git 命令参考

```bash
# 查看仓库状态
git status

# 查看提交历史
git log --oneline --graph

# 创建并切换分支
git checkout -b <branch-name>

# 切换分支
git checkout <branch-name>

# 查看所有分支
git branch -a

# 提交代码
git add <files>
git commit -m "message"
git push origin <branch-name>

# 拉取远程更新
git pull origin <branch-name>

# 合并分支
git merge <source-branch>
```

---

**实验完成时间**：建议 4-6 课时
**难度等级**：中等
**前置知识**：Python 基础语法、Git 基础操作