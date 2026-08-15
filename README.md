# 第一性原理穷举工程(first-principles-repo)

> 尽可能穷尽人类知识体系中所有学科的**第一性原理**及其**衍生路径**——用机器纪律保证每条都是"不可再下推的基石"。

## 这个仓库是什么

一套**活的、被机器审计的**第一性原理知识库:

- **十层级穷举框架**(宇宙演化与知识涌现顺序):逻辑数学 → 物理 → 化学 → 生物 → 神经心理 → 计算 → 经济 → 社会 → 工程 → 复杂系统
- **每个条目 = 一条原理**(Markdown + YAML front matter,见 `rules/schema.yaml`)
- **每次 PR 自动运行 CI**:硬校验(结构/引用/层级/推导图)+ 证伪引擎(剥离审计/穷尽性/错位检测)
- **证伪挑战协议**:任何人可以挑战任何公设,成功则降级——清单永远是"正在被攻击的活清单"

## 🤖 AI / Agent 贡献者入口(先读这个)

你是 AI 编程工具(Claude Code / Cursor / Codex / Copilot)或自动化 agent?**请先读 `AGENTS.md`** —— 它会被你的工具自动加载,一页讲完:文件放哪、front matter 格式、会被什么拦、如何 3 步自检。本仓库的门禁对 AI 友好:提交错了会被机器拦下并告诉你怎么改,不会污染主线。

**想从简单任务开始?** 看 Issues 里带 `good first issue` 标签的条目——都是为第一次贡献者(人类或 AI)准备的。

## 快速开始

```bash
# 克隆后本地跑两道门禁
pip install pyyaml
python scripts/validate.py .   # 硬校验:结构/引用/层级/推导图(失败 = 红)
python scripts/falsify.py .    # 证伪引擎:剥离审计报告(软门禁,出待审清单)
```

## 目录结构

```
principles/
  L1-logic-math/ … L10-complexity/   # 十层级条目(每层 <编号>-<名称>.md)
  meta/                              # 元公设(第 0 层:关于学科的哲学前提)
rules/
  schema.yaml          # 条目 schema(唯一事实源)
  peeling-audit.yaml   # 剥离审计词表(证伪引擎的数据源)
scripts/
  validate.py          # 硬校验器
  falsify.py           # 证伪引擎 / 剥离审计
AGENTS.md              # 🤖 AI/agent 贡献者指南(自动加载)
.github/
  PULL_REQUEST_TEMPLATE.md  # PR 模板(带自检清单)
  ISSUE_TEMPLATE.md         # Issue 模板
  workflows/ci.yml          # 三级门禁:硬校验 → 证伪 → PR 评论
docs/
  CONTRIBUTING.md      # 贡献协议
  REVIEW.md            # 评审清单(评审人=尝试杀死公设的人)
  FALSIFY.md           # 证伪挑战协议(活机制)
  ATTACK-TEST.md       # 🛡️ 实战攻防测试记录(门禁可信度证据链)
CONTRIBUTORS.md        # 名人堂(攻防参与者 + 正式贡献者)
```

## 条目状态

| status | 含义 | 举例 |
|---|---|---|
| `axiom` | 公设:不可由同层/下层推导的基石 | 最小作用量、自然选择、感受质 |
| `theorem` | 定理:可推导但不可绕过 | 哥德尔不完备性、停机问题 |
| `fact` | 观测事实/历史偶然 | 暗能量、手性均一 |
| `hypothesis` | 未决竞争理论 | 自组织临界、强涌现 |
| `meta` | 元公设:学科哲学前提 | 数学柏拉图主义、信息-实在二象性 |

## 准确性三重保障

1. **机器硬校验**(validate.py)——结构/引用/层级/推导图,失败即红
2. **机器启发式证伪**(falsify.py)——剥离词表命中、穷尽性缺口、层级错位、重叠检测
3. **人类证伪挑战**(FALSIFY.md)——评审人/任何人对公设发起"推导链挑战",成功则降级

## 🛡️ 门禁是被真实攻击打出来的

本仓库做过两轮"陌生 AI 无预谋提交"实战攻防测试:第一轮(PR#1)目录逃逸 → CI 假绿灯 → 暴露结构盲区并修复;第二轮(PR#2)同一攻击 → CI 真拦截。**你现在看到的三道门禁,是拿真实攻击验证过的。** 完整记录见 `docs/ATTACK-TEST.md` —— 欢迎来挑战,绕过者进名人堂。

## 证伪挑战记录

| 日期 | 条目 | 原状态 | 结果 | 挑战者 | 推导源 |
|---|---|---|---|---|---|
| 2026-08-06 | (首轮四轮审计) | axiom | → 226 条削至 9+2 绝对核心 | 四轮审计 | 见 docs/FALSIFY.md |

## License

MIT(知识内容 CC-BY 4.0,代码 MIT)
