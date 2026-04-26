# 《现代软件开发技术》上机实验手册：AI 赋能下的 TDD 与 CI/CD 全链路实践

## 实验主题

AI时代的工程安全网——Git协同、CI/CD与TDD测试驱动开发

## 实验目标

1. 理解AI时代软件工程的自动化验证思维
2. 掌握Git版本控制与协同开发流程
3. 学会配置Gitee平台及SSH密钥认证
4. 掌握CI/CD流水线的配置与使用方法
5. 理解并实践TDD测试驱动开发方法论
6. 学会编写测试用例并进行代码验证
7. 掌握代码质量检查与自动化测试流程
8. 建立对AI生成代码的正确性约束能力

## 📅 课程概览 (Total: 240 Mins)

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
Trae 是一款原生的 AI IDE，深度集成了大语言模型，是本次实验“指挥 AI 写代码”的主控台。
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
3.  点击 **"开通服务"**。开通成功后，无需使用页面上的模板，直接关闭页面，本实验将使用代码（Pipeline as Code）来定义流水线。

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

### 步骤 0：创建项目配置文件

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

## ❓ 常见问题 FAQ

### 环境配置相关

#### Q1: Git安装失败怎么办？
**A:** 
- 检查系统要求：Windows 10/11
- 确认下载的是Windows版本安装包
- 查看Git官方文档：https://git-scm.com/
- 检查是否有杀毒软件阻止安装

#### Q2: SSH密钥配置失败怎么办？
**A:** 
- 检查密钥是否正确生成（`ls ~/.ssh/`）
- 确认公钥内容完整复制（从 `ssh-ed25519` 开始到邮箱结束）
- 测试SSH连接：`ssh -T git@gitee.com`

#### Q3: Trae IDE安装或登录问题？
**A:**
- 检查网络连接是否正常
- 确认下载的是对应操作系统的版本
- 尝试重新启动Trae IDE
- 查看Trae官方文档获取帮助

---

### Git相关

#### Q4: Git克隆仓库失败？
**A:**
- 确认使用正确的SSH地址（git@gitee.com:...）
- 检查SSH密钥是否正确配置
- 尝试使用HTTPS地址克隆
- 检查网络连接是否稳定

#### Q5: Git提交时出现身份验证错误？
**A:**
- 确认已配置user.name和user.email：`git config --list`
- 检查SSH密钥是否正确添加到Gitee
- 尝试重新测试SSH连接：`ssh -T git@gitee.com`
- 确认使用的是SSH地址而不是HTTPS地址

#### Q6: Git推送失败？
**A:**
- 检查是否有提交权限
- 确认远程仓库地址正确：`git remote -v`
- 先拉取远程更新再推送：`git pull origin develop`
- 检查网络连接是否正常

---

### CI/CD相关

#### Q7: Gitee Go服务无法开通？
**A:**
- 确认已完成Gitee账号实名认证
- 检查仓库是否公开
- 尝试刷新页面或稍后再试
- 查看Gitee Go官方文档

#### Q8: CI/CD流水线一直失败？
**A:**
- 检查 `.workflow/python-ci.yml` 配置是否正确
- 确认 `requirements.txt` 包含所有依赖
- 查看流水线日志，定位具体错误原因
- 确认Python版本设置正确（3.9）

#### Q9: 如何查看流水线日志？
**A:**
- 在Gitee仓库页面点击 `Gitee Go`
- 点击对应的流水线执行记录
- 查看每个步骤的详细日志输出
- 可以下载完整的日志文件

#### Q10: 流水线超时怎么办？
**A:**
- 优化依赖安装速度（使用清华源）
- 减少测试用例数量（先测试核心功能）
- 检查是否有无限循环或长时间运行的代码
- 联系Gitee技术支持

#### Q11: flake8代码检查失败？
**A:**
- 查看flake8错误信息，了解具体问题
- 修正代码格式和风格问题
- 可以在本地先运行flake8检查：`flake8 .`
- 必要时可以调整flake8规则

---

### TDD相关

#### Q12: pytest测试运行失败？
**A:**
- 检查测试文件命名是否正确（test_*.py）
- 确认测试函数命名正确（test_*）
- 查看错误信息，定位具体问题
- 在本地先运行测试：`pytest -v`

#### Q13: AI生成的代码通不过测试？
**A:**
- 检查测试用例是否正确
- 重新生成更详细的提示词
- 手动调试和修正AI生成的代码
- 考虑将测试失败的用例反馈给AI，让它重新生成

#### Q14: 什么是"测试先行"？为什么要先写测试？
**A:**
- "测试先行"是TDD的核心理念：先写测试，再写实现
- 好处1：明确需求边界，避免过度设计
- 好处2：提供即时反馈，快速验证代码正确性
- 好处3：建立回归测试，防止代码退化
- 好处4：驱动代码设计，产生更可测试的代码

#### Q15: 测试用例写多少才够？
**A:**
- 覆盖正常流程（Happy Path）
- 覆盖边界条件（如第1抽、第74抽、第90抽）
- 覆盖异常情况（如0抽、负数抽、超过90抽）
- 遵循80/20原则：重点测试核心功能
- 根据实际需求和时间安排调整

---

### AI辅助开发相关

#### Q16: AI生成的代码质量如何？
**A:**
- AI生成的代码质量参差不齐，需要仔细审查
- 优点：快速生成基础框架，提供实现思路
- 缺点：可能存在逻辑错误，边界条件处理不完善
- 建议：使用TDD方法，用测试验证AI生成的代码
- 重要：人工审查和修正始终是必要的

#### Q17: 如何写好AI提示词？
**A:**
- 明确需求：详细描述功能和约束
- 提供示例：给出输入输出示例
- 规范格式：指定函数名、参数、返回值
- 强调边界：特别说明异常情况如何处理
- 迭代优化：根据AI输出不断调整提示词

#### Q18: AI生成的代码可以直接用吗？
**A:**
- 不建议直接使用生产环境
- 必须经过测试验证
- 建议人工审查代码逻辑
- 考虑安全性和性能问题
- TDD是验证AI代码的好方法

---

### 实验报告相关

#### Q19: 没有Trae IDE可以完成实验吗？
**A:**
- 可以！可以使用其他IDE（如VSCode、PyCharm）
- 可以手动编写代码，不使用AI辅助
- 核心是理解TDD和CI/CD的理念
- 在报告中说明使用的工具

#### Q20: 实验步骤可以简化吗？
**A:**
- 核心功能必须完成：Git、CI/CD、TDD流程
- 可以根据实际情况调整测试用例复杂度
- 如遇技术问题，及时向任课教师或助教求助
- 在报告中说明遇到的问题和解决方案

#### Q21: 代码需要完全自己写吗？
**A:**
- 可以参考实验文档中的代码示例
- 鼓励使用AI辅助编程，但要理解代码逻辑
- 必须能够解释代码的工作原理
- 建议添加自己的注释和修改
- 独立完成实验报告

#### Q22: 遇到技术问题无法解决怎么办？
**A:**
- 先仔细阅读错误信息，尝试自己解决
- 查看常见问题部分是否有解决方案
- 搜索相关技术文档和教程
- 向同学请教（但不要直接复制代码）
- 及时向任课教师或助教求助
- 在实验报告中说明遇到的问题和尝试的解决方案

---

### Git提交相关

#### Q23: Git提交信息怎么写？
**A:**
- 使用约定式提交规范：`<类型>: <描述>`
- 常用类型：feat(新功能)、fix(修复)、docs(文档)、style(格式)、refactor(重构)、test(测试)、chore(构建)
- 示例：`feat: 添加抽卡概率计算`、`fix: 修复边界条件处理`
- 用中文或英文都可以，保持一致即可
- 提交信息要简洁明了

#### Q24: 需要提交多少次commit？
**A:**
- 至少5次有意义的commit
- 建议按照功能模块分阶段提交
- 每次commit对应一个明确的改动
- 不要把所有代码一次性提交
- 良好的提交历史有助于代码审查和版本回滚

---

### 扩展学习相关

#### Q25: 想深入学习，有什么推荐资源？
**A:**
- Git官方文档：https://git-scm.com/doc
- pytest官方文档：https://docs.pytest.org/
- Gitee Go文档：https://help.gitee.com/gitee-go
- TDD相关书籍：《测试驱动开发》、《敏捷软件开发》
- CI/CD相关：《持续集成》、《持续交付》

#### Q26: 可以尝试其他CI/CD平台吗？
**A:**
- 可以。除了Gitee Go，还有很多选择
- 推荐尝试：GitHub Actions、GitLab CI、Jenkins等
- 对比不同平台的特点和优势
- 在实验报告中分享个人发现
- 注意平台配置可能有所不同

---

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
