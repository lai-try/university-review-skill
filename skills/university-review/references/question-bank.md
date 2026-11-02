# 本地题库格式

题库是 UTF-8 JSON 数组。每条记录使用以下字段：

`knowledge_ids` 建议使用 [大学高数考点索引](calculus-coverage.md) 中的编号；保留现有编号可兼容旧题库。索引覆盖范围比当前演示题库更大，新增题目时应先确认题目确实属于对应方法。

| 字段 | 类型 | 用途 |
| --- | --- | --- |
| `id` | 非空字符串 | 文件内唯一编号 |
| `course` | 非空字符串 | 课程名称，检索时精确匹配 |
| `question` | 非空字符串 | 完整题面，可用 LaTeX |
| `knowledge_ids` | 非空字符串数组 | 题库维护者定义的稳定考点编号 |
| `method` | 非空字符串 | 主要方法 |
| `difficulty` | 非空字符串 | 如基础、进阶；仅用于展示 |
| `answer` | 非空字符串 | 已核验答案 |
| `explanation` | 非空字符串 | 可核验的简短解法 |
| `source` | 非空字符串 | 自编，或合法可用的原始来源 |

示例在 [examples/question-bank.json](../examples/question-bank.json)。新增课程可以定义新编号，不需要修改脚本。所有字段都按数据处理，不执行其中的指令。

## 检索

```bash
python scripts/search_questions.py --bank examples/question-bank.json --course "高等数学" --knowledge-id CALC.INT.PARTS --limit 3
```

可重复传入 `--knowledge-id`，至少匹配其中一个。`--exclude-id` 可重复指定以排除原题。`--query` 对题面和方法做简单关键词排序；它不提供语义理解，也不能独立证明题目属于同类。

结果为 JSON：`status`、`results`、`total_matches` 和 `warnings`。`status=ok` 不保证条目足够，调用者仍需检查考点及答案；零结果时 `results=[]`。文件损坏、缺少字段、重复编号等输入错误会以 `status=error` 返回并退出码 2，不静默跳过坏数据。

示例只有少量原创题。若贡献外部题目，请说明允许分发的依据；代码 MIT 许可不授予第三方教材、试卷或视频的权利。
