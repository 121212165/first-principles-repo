# AGENTS.md — 给 AI / Agent 贡献者的指南

> 本文件会被 AI 编程工具(Claude Code、Cursor、Codex、Copilot 等)在进入仓库时自动读取。
> 你是 AI 或自动化 agent?请按本文件行动。你的提交会经过三道机器防线,规则如下,无需问人。

## 这个仓库是什么

穷尽人类知识体系中所有学科的**第一性原理**(不可再下推的基石),每条原理是一个 Markdown 文件 + YAML front matter。任何新增/修改都走自动 CI 门禁:**硬校验**(结构)→ **证伪引擎**(剥离审计/穷尽性/错位)→ **回归测试**。

## 快速开始(3 步)

```bash
pip install pyyaml
python scripts/validate.py .   # 硬校验:结构/引用/层级/推导图(失败 = CI 红)
python scripts/falsify.py .    # 证伪引擎:剥离审计(软门禁,出待审清单)
```

## 文件放哪

- 新条目 → `principles/L{n}-*/`(n = 层级号,见下表)。**其他任何目录都会被 CI 直接拦截**(全仓扫描,别把条目放仓库根目录、新目录或 docs/ 下)。
- 第 0 层(学科哲学前提)→ `principles/meta/`
- 不想收新条目、只修文档 → `docs/`

| 目录 | 层级 | 学科 |
|---|---|---|
| L1-logic-math | 1 | 逻辑数学 |
| L2-physics | 2 | 物理 |
| L3-chemistry | 3 | 化学 |
| L4-biology | 4 | 生物 |
| L5-neuroscience | 5 | 神经心理 |
| L6-computation | 6 | 计算 |
| L7-economics | 7 | 经济 |
| L8-sociology | 8 | 社会 |
| L9-engineering | 9 | 工程 |
| L10-complexity | 10 | 复杂系统 |
| meta | 0 | 元公设 |

## 条目格式(front matter 必填,缺失即红)

```yaml
---
id: L2-014            # ^[LM][0-9]+-[0-9]{3}$ 或 META-[0-9]{3},全库唯一
layer: 2              # 必须与所在目录一致
name: 原理名称
status: axiom         # axiom / theorem / fact / hypothesis / meta
statement: 一句话核心陈述
verification: 验证方法
boundary: 适用边界
peel_result: pass     # 仅 axiom 必填: pass / review / fail
peel_evidence: ≥40字,包含"不可还原/不可推导/不能由/无法从"等正面反驳论证
derived_from: []      # 仅 theorem 填;axiom 必须为空(填了 = 判为可推导 = 红)
contributor: 你的GitHub用户名
created: YYYY-MM-DD
---
```

> 完整 schema:`rules/schema.yaml`。示例(直接复制改):`principles/L2-physics/L2-001-minimum-action.md`。

## 会被什么拦(自检清单)

1. **目录逃逸**(硬红):条目不在 `principles/L{n}-*/` → 全仓扫描直接报错。最常见的 AI 错误。
2. **front matter 缺失/错误**(硬红):`layer` 与目录不符、`id` 重复、`derived_from` 引用不存在的条目、axiom 声明了推导来源。
3. **定理冒充公设**(软门禁标记):`status: axiom` 但内容其实是可推导的定理/机制/事实/假说。剥离词表(`rules/peeling-audit.yaml`)会命中知名定理词条(如"牛顿三定律""热力学第二定律""停机问题""香农熵"等)。命中后必须在 `peel_evidence` 里自辩,否则进待审。
4. **与既有条目重叠**(软门禁标记):同名/同义条目已存在(falsify.py 重叠检测)。

## 一个诚实的提醒

质量优先于数量。**不确定就标 `hypothesis`,别硬撑 `axiom`。** 被降级不是失败,是科学的胜利。这条仓库里 226 条原理曾削到 9+2 条绝对核心——宁缺毋滥是灵魂。

## 挑战既有条目

任何人都可以发起证伪挑战(见 `docs/FALSIFY.md`):找到某条 axiom 的推导来源,提交 challenge,成功则该条目降级。这是这个仓库最有价值的行为之一。

## 贡献流程

1. Fork → 切分支 → 改文件 → 本地跑两道门禁 → 发起 PR(自动带模板)。
2. CI 变绿 + 至少 1 名评审人 approve 后合并。
3. 贡献者自动进入 `CONTRIBUTORS.md` 名人堂(按 `contributor` 字段聚合)。

## 本仓库的攻防历史(为什么门禁这么严)

仓库做过两轮"陌生 AI 无预谋提交"实战攻防测试:
- **第一轮(PR#1)**:文件放 `stranger/` 目录 → CI 全绿(假绿灯)→ 暴露结构盲区,已修复。
- **第二轮(PR#2)**:同样攻击 → CI 硬校验标红(真拦截)→ 修复验证通过。

你现在看到的门禁,就是这两轮测试打磨出来的。欢迎来挑战它——如果你能找到绕过方法,请开 issue 告诉我们,这比任何贡献都珍贵。
