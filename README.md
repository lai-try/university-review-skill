# University Review Skill · 大学高数复习助手

给支持 Skill 的智能体发送一道大学高数题，按顺序获得**知识点与原题解法 → B 站讲解视频 → 同类练习题**。练习默认不附答案或解析，用户主动索要时再提供。

这是供现有智能体加载的工作说明、题库和 Python 检索工具，不是独立聊天网站，也不会训练新模型。

## 范围与当前状态

- 考点索引面向常见高数上下册：极限与连续、导数与微分、积分、级数、多元函数、重积分、曲线曲面积分、向量分析、空间解析几何和常微分方程。完整标签见[考点索引](skills/university-review/references/calculus-coverage.md)。索引不代表每个考点都经过完整实测。
- 本地题库目前是 **16 道自编演示题、4 类基础考点**：基本极限、基础求导、换元积分和分部积分。其他考点缺少本地题目时，宿主可生成并核验变式，明确标注“AI 生成变式”。
- 视频检索需要宿主已有的浏览器或联网工具。仅依据标题或简介时会标明“未核验视频内容”；没有可靠结果时会说明原因，不编造视频链接。
- 豆包网页版已做导入尝试，**仅发题目就自动完成“讲解→视频→练习”的流程尚未验证通过**。上传文件不等于技能已启用，也不会自动增加浏览器、联网搜索或 Python 执行能力。
- 当前不包含线性代数、概率论、复变函数、偏微分方程和数学分析专题。

第一次制作和发布 Skill，请按 [Windows 新手上手教程](GETTING_STARTED.md) 操作，包含软件安装、本地运行、GitHub 发布和 Skill 安装。

完全零基础可先读 [高等数学第一版教程](BEGINNER_CALCULUS.md)，按“整理题库 → 检索测试 → 完整试题验收”跑通一个考点。

## 使用条件

- 支持加载 Skill 的智能体。完整流程还需具备读取随附题库和检索视频的工具；本项目的脚本检索方式需要 Python 执行能力。用户自己的浏览器能访问 B 站，不代表宿主已有浏览器工具。
- Python 3.10 或更新版本；工具仅使用 Python 标准库。
- 输入照片时，宿主智能体需要具备识图能力；工具本身不提供图片识别。

## 安装

仓库发布后，可以克隆到本地：

```bash
git clone https://github.com/lai-try/university-review-skill.git
cd university-review-skill
```

将整个 `skills/university-review` 文件夹复制到所用智能体支持的本地 Skill 目录，按宿主要求重新加载。Codex 用户可根据本地配置使用 `$CODEX_HOME/skills` 或 `~/.codex/skills`。不需要安装其他 Skill。

安装并加载 Skill 后，如果宿主支持自动发现，直接发送一道高等数学题即可，例如：

> 求不定积分 ∫x·cos(x) dx。

Skill 会按“考点与解题步骤 → B 站讲解视频 → 同类练习题”的顺序回答；练习默认不附答案，用户之后索要时再给。若宿主没有自动加载它，在支持的环境中显式启用 `$university-review` 后再发送题目。单纯把仓库放在 D 盘不会让宿主自动加载；题目信息不完整时，智能体会先询问影响解题的必要条件。

宿主若支持上传 Skill 文件夹或 ZIP，选择 **`skills/university-review` 这一层**，使 `SKILL.md` 位于上传根目录，并带上 `examples/`、`references/` 和 `scripts/`。只上传 `SKILL.md` 不会带上题库。各宿主对技能启用、随附文件读取和工具执行的支持不同，导入后仍需实测。

## 工具用法

完整 Skill 优先使用宿主的浏览器工具读取 B 站公开搜索页，提取页面实际显示的视频链接；如果网页要求验证或拒绝访问，停止自动操作。没有浏览器工具时，可选用以下接口脚本。在仓库根目录运行：

```bash
python skills/university-review/scripts/search_bilibili.py --query '高等数学 分部积分法 例题' --limit 3 --cache-dir .cache/bilibili
```

接口脚本返回 JSON，`status` 为 `ok` 或 `manual_search_required`。搜索接口受限时，会提供真实的 B 站搜索页链接；宿主可用正常浏览器工具读取，或由用户人工打开。浏览器检索成功不改变脚本的失败状态，也不表示已核验视频内容。B 站接口的可用性可能变化，本项目不保证接口长期稳定，不绕过风控、不下载视频，也不捏造字幕或讲解时间戳。

检索本地题库：

```bash
python skills/university-review/scripts/search_questions.py --bank skills/university-review/examples/question-bank.json --course 高等数学 --knowledge-id CALC.INT.PARTS --limit 3
```

示例题库目前包含 16 道自编高数演示题，覆盖四类基础考点；完整考点路由见[大学高数考点索引](skills/university-review/references/calculus-coverage.md)，题库本身不代表完整课程题库。原题恰好在库中时，用 `--exclude-id` 排除其 ID。匹配不足 3 题时，按实际数量返回；智能体可以另行生成、校验并明确标注变式题，不将其冒充为检索结果。扩充题库时请参阅[题库格式说明](skills/university-review/references/question-bank.md)。

## 目录

```text
skills/university-review/
  SKILL.md
  scripts/
  references/
  examples/
tests/
```

## 本地验证

```bash
python -m unittest discover -s tests -v
```

现有 33 项离线测试检查检索、题库格式和网络失败处理等脚本行为，不证明高数所有考点都能正确解答，也不证明当前 B 站或某个宿主一定可用。

## 发布到 GitHub

按 [新手教程第六步](GETTING_STARTED.md#第六步发布到-github) 在 GitHub 网页创建空仓库，再用 Git 上传；不需要安装 GitHub CLI。文档中的 `lai-try/university-review-skill` 是预定地址，不表示仓库已创建。

仓库简介可填写：

> 大学高数复习 Agent Skill：讲解知识点、检索 B 站视频、提供同类练习，练习默认不含答案。

首次提交说明可填写：`发布高数复习 Skill 初始版本`。

缓存、Python 字节码和 ZIP 已通过 `.gitignore` 排除，不随源码提交。若要提供可直接导入的 Skill ZIP，可单独附在 GitHub Release；ZIP 根目录应直接包含 `SKILL.md`。只把 ZIP 上传到仓库不会自动展开成源码。

## 贡献与许可

欢迎提交最小、可测试的改进，见 [CONTRIBUTING.md](CONTRIBUTING.md)。本项目原创代码、文档与自编示例题采用 [MIT 许可证](LICENSE)。第三方视频及外部题目不纳入本项目许可，其权利归各自权利人所有。
