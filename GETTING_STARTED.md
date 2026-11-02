# 从零制作、发布和使用大学复习 Skill

目标只有一个：输入大学高等数学题目，获得考点与解法、B 站讲解视频和不含答案的同类练习。当前 Skill 可路由常见高数上下册主要章节；起始题库仍只有少量基础演示题，其他考点会在本地题库不足时使用已核验的 AI 生成变式。

零基础建议先按 [高数第一版教程](BEGINNER_CALCULUS.md) 完成一次题库修改和验收，再回来发布。

Skill 由说明文件和辅助工具组成，由支持它的智能体读取并执行。本版本使用宿主已有模型，无需训练模型、购买显卡或租服务器。使用宿主模型时，仍遵循该产品的订阅或 API 计费方式。

本教程使用 Windows PowerShell。命令中的 `py` 指 Python 启动器；若你的系统使用 `python`，可在确认版本后替换。所有相对路径命令都在本仓库根目录执行。

## 第一步：准备软件

| 软件或账号 | 用途 | 是否必需 |
| --- | --- | --- |
| 支持本地 Skill、终端工具的 Codex 等智能体 | 理解题目，调用检索脚本，组织回答 | 必需 |
| [Python](https://www.python.org/downloads/) 3.10 或更新版本 | 运行两个搜索脚本 | 必需 |
| [VS Code](https://code.visualstudio.com/) 或已有的代码编辑器 | 编辑 Markdown、Python 和题库 | 选择一个即可 |
| [Git for Windows](https://git-scm.com/downloads/win) | 保存版本并上传代码 | 本教程使用 |
| [GitHub](https://github.com/) 账号 | 托管开源仓库，账号为 `lai-try` | 发布时必需 |

安装后重新打开 PowerShell，检查：

```powershell
py --version
git --version
```

两个辅助脚本只用 Python 标准库，不需要 `pip install`。GitHub CLI、Docker、数据库和云服务器都不是此版本的运行依赖。

## 第二步：打开项目，理解三个部分

用编辑器打开 `university-review-skill` 文件夹，在编辑器终端中执行后续命令。

```text
university-review-skill/
  README.md                           项目介绍
  GETTING_STARTED.md                  本教程
  LICENSE                             MIT 开源许可证
  skills/university-review/
    SKILL.md                          智能体的工作说明
    agents/openai.yaml                Codex 展示信息
    scripts/search_bilibili.py         搜索 B 站视频信息
    scripts/search_questions.py        搜索本地题库
    examples/question-bank.json       演示题库
    references/question-bank.md       题库字段说明
  tests/                              脚本测试
  .github/workflows/check.yml          提交后自动运行测试
```

- `SKILL.md` 决定什么时候使用这个 Skill，以及工作流程。
- `scripts/` 完成实际检索；写在说明里的动作，需要宿主具有相应工具才能执行。
- `question-bank.json` 保存题目、考点、答案、解析和来源。

## 第三步：编辑 Skill 说明

打开 `skills/university-review/SKILL.md`。开头必须包含名称与描述，例如：

```yaml
---
name: university-review
description: 根据大学高数题目识别考点，查找 B 站讲解视频，提供不含答案的同类练习，按需再给答案。
---
```

正文写清楚：识别课程与考点 → 讲解原题 → 搜索视频 → 检索同类题 → 内部核验练习答案，返回题目时不附答案或解析。

模板已经写好完整流程。先保留它，实际试题之后再改进匹配规则。名称使用小写英文和连字符；文本文件保存为 UTF-8。

这个 Skill 不需要写模型 API Key。理解题目和生成变式由宿主智能体完成；照片题还需要宿主支持识图。

## 第四步：运行脚本

先测试本地题库：

```powershell
py skills/university-review/scripts/search_questions.py --bank skills/university-review/examples/question-bank.json --course "高等数学" --knowledge-id CALC.INT.PARTS --exclude-id calc-parts-001 --limit 3
```

该命令把 ∫x cos x dx 作为原题，排除 `calc-parts-001`，应返回另外三道分部积分题。不要把原题再次算作练习。

完整 Skill 优先使用宿主已有的浏览器工具搜索公开网页。下面可选测试 Python 接口，需要联网；已经返回 HTTP 412 时不要反复执行：

```powershell
py skills/university-review/scripts/search_bilibili.py --query "高等数学 分部积分法 例题" --limit 3 --cache-dir "D:\university-review-skill\.cache\bilibili"
```

查看返回 JSON 的 `status`：

- `ok`：请求成功，查看 `results`。没有结果时调整关键词，不代表找到了匹配视频。
- `manual_search_required`：当前接口不可用。宿主有浏览器工具时可正常读取 `search_url`；否则由用户人工打开。该链接是搜索页，不是已核验的视频。浏览器成功不会把接口结果变成成功。
- `error`：输入参数或离线测试文件有误，按错误信息修正。

当前脚本搜索公开视频元数据，不下载视频。B 站接口可能限制访问，项目不保证实时搜索始终成功。只有标题或简介时，匹配结论须注明未核验视频内容。

最后运行自动测试：

```powershell
py -m unittest discover -s tests -v
```

应显示 `OK`。这些测试使用离线样本或模拟请求，不能证明 B 站此刻可访问，也不能证明模型每次都会正确解题。

## 第五步：安装到自己的智能体

GitHub 用来保存和分享文件；Skill 的执行发生在支持它的智能体环境中。

如果当前要求所有项目操作留在 D 盘，先按 `BEGINNER_CALCULUS.md` 第 6 节在聊天窗口直接指定 D 盘 `SKILL.md` 试用，不执行下面可能写入用户目录的通用安装示例。直接读取文件不等于已经自动注册 Skill。需要浏览器检索时，宿主必须提供浏览器工具；仅安装 VS Code 或 Python 不会自动增加该工具。

以本机 Codex 配置约定为例，个人 Skill 目录是 `$CODEX_HOME/skills`；未设置 `CODEX_HOME` 时通常使用用户目录下的 `.codex/skills`。其他智能体及不同版本请按各自说明选择目录。

首次安装可在仓库根目录运行：

```powershell
if ($env:CODEX_HOME) {
    $reviewSkillBase = Join-Path $env:CODEX_HOME 'skills'
} else {
    $reviewSkillBase = Join-Path $env:USERPROFILE '.codex\skills'
}
$reviewSkillTarget = Join-Path $reviewSkillBase 'university-review'
if (Test-Path -LiteralPath $reviewSkillTarget) {
    throw '已存在 university-review，请先检查现有版本，再决定如何更新。'
}
New-Item -ItemType Directory -Path $reviewSkillBase -Force | Out-Null
Copy-Item -LiteralPath '.\skills\university-review' -Destination $reviewSkillBase -Recurse
```

复制的是整个 `university-review` 文件夹，包含脚本、题库和参考文件。按宿主要求重新加载 Skill；若列表中未出现，重启宿主后新开对话检查。

安装并加载后，先尝试只发送题目（前提是宿主支持自动发现 Skill）：

```text
求 ∫x·cos(x) dx。
```

预期顺序是先讲考点和解题步骤，再给 B 站视频，最后给同类练习题（默认不附答案或解析）。若新对话未自动加载 Skill，在支持的宿主中显式使用 `$university-review`；只有 Skill 已加载后，题目本身才能作为完整提示。把文件留在 D 盘并不等于已安装或自动触发。检查视频链接和练习是否排除原题；用户之后索要答案时再检查答案是否正确。工具的网络与终端权限仍由宿主控制。

## 第六步：发布到 GitHub

1. 登录 `lai-try`，打开 [GitHub 新建仓库页面](https://github.com/new)。
2. 仓库名填 `university-review-skill`，可见性选 Public。Description（仓库简介）可复制下方文字。
3. 本地已有 README、许可证和 `.gitignore`，网页上不要重复初始化这些文件。
4. 创建空仓库。如果同名仓库已存在，先检查其内容，不要覆盖。
5. 在 PowerShell 中进入项目目录，执行下面的首次发布命令。

Description 是仓库首页显示的简短备注，填写：

```text
大学高数复习 Agent Skill：讲解知识点、检索 B 站视频、提供同类练习，练习默认不含答案。
```

README.md 是详细说明，上传后会自动显示在仓库首页；LICENSE 已选 MIT，无须网页再生成。

```powershell
Set-Location -LiteralPath 'D:\university-review-skill'
git init -b main
git add .
git status
git commit -m "发布高数复习 Skill 初始版本"
git remote add origin https://github.com/lai-try/university-review-skill.git
git push -u origin main
```

若当前文件夹已经有 Git 仓库，先检查 `git status`、`git remote -v` 和 `git log -1`，不要把首次发布命令整段反复执行。如果提示 `origin already exists`，先检查地址；如果推送因远端已有提交而被拒绝，先核对远端内容，不使用强制推送。

`git commit -m` 后面是这次上传的修改备注，可以使用中文。提交前通过 `git status` 检查文件。缓存和 ZIP 不会被提交，这是 `.gitignore` 的预期行为。不要提交 Cookie、令牌、个人信息或未获授权的整本题库。项目的 MIT 许可覆盖原创代码、文档与自编题目；外部视频不会因此变成 MIT 内容。

如果 Git 提示没有身份信息，用自己的信息设置 `git config user.name` 和 `git config user.email`；邮箱可使用 GitHub 账户设置提供的隐私邮箱。如果推送要求登录，按 Git 凭据管理器的提示在浏览器认证；GitHub 不使用账户密码作为 HTTPS 推送凭据。

推送成功后，仓库地址才会是：

```text
https://github.com/lai-try/university-review-skill
```

本教程中的地址是预定发布地址，不表示仓库已经创建。上传后确认首页能看到 `README.md`、`LICENSE`、`skills/` 和 `tests/`，并在 Actions 页面查看离线测试结果。若要让其他人下载完整 Skill ZIP，在 Releases 中单独上传根目录包含 `SKILL.md` 的技能包。

## 第七步：让别人使用和持续更新

别人可以克隆公开仓库，然后按第五步把 Skill 文件夹安装到自己的智能体：

```powershell
git clone https://github.com/lai-try/university-review-skill.git
cd university-review-skill
```

使用者需要自己的宿主模型环境和 Python；GitHub 不会替他们运行模型或提供聊天服务。

扩充题库时，先阅读 `skills/university-review/references/question-bank.md` 和 `skills/university-review/references/calculus-coverage.md`，添加自编或获授权的题目，复算答案。当前十六道高数演示题只用于跑通流程；考点索引范围更大，但不代表每个考点都有现成题目。

每次修改后运行测试、提交并推送：

```powershell
py -m unittest discover -s tests -v
git add .
git commit -m "Improve university review skill"
git push
```

个人 Skill 目录中的副本也需要同步更新，拉取仓库不会自动更新之前复制的文件。需要版本发布时，可在 GitHub 创建 `v0.1.0` 等 Release。未来若要让同学只打开网页就能使用，再单独开发并部署网页和后端；本教程的 Skill 本身无需云端服务。
