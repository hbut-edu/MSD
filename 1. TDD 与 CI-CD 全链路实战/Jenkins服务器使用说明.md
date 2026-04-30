# 实验主题 1：Jenkins 服务器版 CI/CD 使用说明

## 适用说明

本说明用于替代原实验手册中“开启 Gitee Go 服务”和“编写 `.workflow/python-ci.yml`”相关步骤。同学们仍然使用 Gitee 或 GitHub 保存代码，但 CI/CD 流水线统一改为使用课程 Jenkins 服务器执行。

课程 Jenkins 地址：

```text
http://116.62.141.25:1989/
```

本实验统一使用 Jenkins 任务：

```text
topic1-tdd-ci
```

学生统一使用任课教师提供的受限账号登录。该账号只用于完成实验构建，不具备系统管理、项目创建、项目配置修改或项目删除权限。

课堂账号：

```text
用户名：student
密码：向老师询问
```

进入 Jenkins 后，同学们只需要打开 `topic1-tdd-ci` 并点击“Build with Parameters”或“使用参数构建”。不要尝试新建 Jenkins 项目，也不要使用管理员账号完成实验。

学生账号权限范围：

| 权限项 | 是否开放 | 说明 |
| --- | --- | --- |
| 登录 Jenkins | 是 | 可进入课程 Jenkins 页面 |
| 查看 `topic1-tdd-ci` | 是 | 可查看统一实验任务 |
| 触发构建 | 是 | 可填写参数并运行实验流水线 |
| 查看构建结果与日志 | 是 | 可查看 Console Output 并截图 |
| 查看 Workspace | 是 | 用于排查构建产物和临时工作目录 |
| 新建 Jenkins 项目 | 否 | 本实验不要求学生新建项目 |
| 修改任务配置 | 否 | 防止误改统一实验任务 |
| 删除任务或构建记录 | 否 | 防止影响其他同学实验 |
| Jenkins 系统管理 | 否 | 仅教师使用管理员账号维护 |

## 一、实验前准备

同学们需要先完成原实验手册中的本地 Git、SSH、公钥配置和仓库创建步骤。与原手册不同的是，不需要开通 Gitee Go。

每位同学的仓库建议保持如下约定：

| 项目 | 要求 |
| --- | --- |
| 仓库名称 | `genshin-gacha-tdd` |
| 仓库可见性 | 公开仓库 |
| 实验分支 | `develop` |
| 依赖文件 | `requirements.txt` |
| pytest 配置 | `pytest.ini` |
| 测试文件 | `test_business_logic.py` |
| 业务代码 | `business_logic.py` |

`requirements.txt` 至少包含：

```text
pytest>=7.0.0
flake8>=5.0.0
```

## 二、Jenkins 构建参数

进入 `topic1-tdd-ci` 后，点击“Build with Parameters”或“使用参数构建”，填写以下参数：

| 参数名 | 填写内容 | 示例 |
| --- | --- | --- |
| `STUDENT_ID` | 学号 | `20260001` |
| `STUDENT_NAME` | 姓名 | `张三` |
| `REPO_URL` | 公开 Git 仓库 HTTPS 地址 | `https://gitee.com/your-name/genshin-gacha-tdd.git` |
| `BRANCH` | 实验分支 | `develop` |

注意：`REPO_URL` 建议填写 HTTPS 地址，不要填写账号密码、Token 或任何私人密钥。

## 三、第一次构建：观察 CI/CD 拦截失败

第一轮实验只提交测试用例，不提交完整业务逻辑，用来观察 CI/CD 如何拦截错误提交。

推荐操作流程：

1. 在 `develop` 分支提交 `requirements.txt`、`pytest.ini` 和 `test_business_logic.py`。
2. 暂时不要提交完整的 `business_logic.py`，或者只提交一个无法通过测试的空实现。
3. 推送到远程仓库：

```bash
git add .
git commit -m "test: add failing tdd cases"
git push origin develop
```

4. 打开 Jenkins 的 `topic1-tdd-ci`。
5. 填写学号、姓名、仓库地址和分支。
6. 点击构建。
7. 打开本次构建记录，查看 Console Output。

如果测试用例正确拦截了未完成业务代码，本次构建应显示失败。实验报告中需要保留本次失败截图。

## 四、第二次构建：实现代码并让 CI/CD 通过

第二轮实验补全业务逻辑，让测试通过。

推荐操作流程：

1. 编写或使用 Trae AI 辅助生成 `business_logic.py`。
2. 在本地先运行：

```bash
python -m pip install -r requirements.txt
pytest test_business_logic.py -v
```

3. 本地通过后提交并推送：

```bash
git add .
git commit -m "feat: implement gacha probability logic"
git push origin develop
```

4. 回到 Jenkins，再次使用相同参数构建。
5. 打开 Console Output，确认 `flake8` 和 `pytest` 均通过。

构建日志末尾如果出现如下提示，表示本次 CI/CD 验证通过：

```text
===== Topic 1 TDD CI Build Passed =====
```

实验报告中需要保留本次成功截图。

## 五、Jenkins 实际执行内容

Jenkins 会自动完成以下动作：

1. 根据 `REPO_URL` 和 `BRANCH` 克隆同学的仓库。
2. 创建 Python 虚拟环境。
3. 使用清华 PyPI 镜像安装依赖。
4. 执行语法和严重错误检查：

```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

5. 执行测试：

```bash
pytest test_business_logic.py -v
```

Jenkins 构建环境只用于验证代码，不保存同学的本地文件，也不需要同学上传密码或密钥。

## 六、课堂使用建议

本课程 Jenkins 服务器性能有限，为保证 60 人左右能够稳定完成实验，请按教师安排分批构建。

建议按课堂座位、小组、提交进度或教师现场点名顺序分批。每一批同学完成代码推送后，再进入 Jenkins 触发构建；未轮到的同学先在本地完成测试与提交准备。

可采用如下轮次：

| 轮次 | 参与对象 | 操作 |
| --- | --- | --- |
| 第 1 轮 | 教师指定的一组同学 | 提交并构建 |
| 第 2 轮 | 教师指定的一组同学 | 提交并构建 |
| 第 3 轮 | 教师指定的一组同学 | 提交并构建 |

Jenkins 同一时间只运行少量构建任务。如果看到任务处于 Queue 中，请等待前面的构建完成，不要重复点击构建按钮。

## 七、常见问题

### Q1：Jenkins 提示没有权限怎么办？

使用教师提供的 `student` 账号登录。学生账号只具备查看 `topic1-tdd-ci` 和触发构建的权限，不具备系统管理权限。

如果看到 Jenkins 管理页面或新建任务页面提示无权限，这是正常现象。本实验不要求同学们新建 Jenkins 项目。

### Q2：构建时报 `REPO_URL 必须填写` 怎么办？

返回“Build with Parameters”页面，确认 `REPO_URL` 已填写完整仓库地址，例如：

```text
https://gitee.com/your-name/genshin-gacha-tdd.git
```

### Q3：构建时报 `缺少 requirements.txt` 怎么办？

说明仓库根目录没有提交 `requirements.txt`，或 Jenkins 拉取的分支不是当前实验分支。请确认文件位于仓库根目录，并确认 `BRANCH` 填写为 `develop`。

### Q4：构建时报 `缺少 test_business_logic.py` 怎么办？

说明测试文件未提交，或文件名不符合实验要求。请在仓库根目录创建并提交：

```text
test_business_logic.py
```

### Q5：第一次构建失败是不是错误？

不是。TDD 实验要求先写测试，再让 CI/CD 拦截未完成的业务代码。第一次失败是本实验的重要证据之一。

### Q6：依赖安装很慢怎么办？

Jenkins 已经使用清华 PyPI 镜像加速依赖安装。若仍然较慢，请等待当前构建完成，不要重复触发多个构建。

### Q7：构建长时间没有结束怎么办？

本任务设置了构建超时保护，单次测试阶段最长约 240 秒。若超时失败，请检查代码中是否存在死循环、长时间等待或网络请求。

## 八、实验报告截图要求

使用 Jenkins 服务器后，原实验报告中关于 Gitee Go 的截图改为提交 Jenkins 截图：

| 原要求 | Jenkins 服务器版替代材料 |
| --- | --- |
| Gitee Go 服务开启截图 | Jenkins `topic1-tdd-ci` 任务页面截图 |
| Gitee Go 流水线失败截图 | Jenkins 第一次构建失败的 Console Output 截图 |
| Gitee Go 流水线成功截图 | Jenkins 第二次构建成功的 Console Output 截图 |
| `.workflow/python-ci.yml` 文件 | 本实验不再要求提交该文件 |

其他 Git、分支、测试用例、业务代码和实验总结要求保持不变。
