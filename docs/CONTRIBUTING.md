# 贡献协议(Contributing)

本仓库穷尽"第一性原理"及其衍生路径。**质量优先于数量**——宁缺毋滥,是全部治理规则的灵魂。

---

## 0. 一句话

> 不要提交"你认为重要的东西",只提交"**无法被更底层原理推导、且经得起剥离审计的东西**"。

---

## 1. 新增条目的流程

```
1. Fork 仓库,切分支
2. 按层级目录(principles/L{n}-*)创建 Markdown 条目
3. 本地跑两道门禁:
     python scripts/validate.py .
     python scripts/falsify.py .
4. 硬校验失败 => 修复后再提交(CI 会拦截)
5. 软门禁的"待审项"必须在 PR 描述中逐条回应
6. 发起 PR,等 CI 变绿 + 至少 1 名评审人 approve
7. 合并
```

## 2. 条目该有的样子

见示例(已入库,可直接复制改):
- 公设示例: `principles/L2-physics/L2-001-minimum-action.md`
- 定理示例: `principles/L1-logic-math/L1-004-godel-incompleteness.md`
- 被剥离示例: `principles/L2-physics/L2-030-entanglement.md`

**front matter 必填字段**(缺失 = CI 红):

| 字段 | 含义 | 说明 |
|---|---|---|
| `id` | 唯一标识 | `L2-014` / `META-001`,全库唯一 |
| `layer` | 层级号 | 0=元公设,1-10=学科层,必须与目录一致 |
| `name` | 原理名称 | 简洁准确 |
| `status` | 状态 | `axiom`(公设)/`theorem`(定理)/`fact`(事实)/`hypothesis`(假说)/`meta`(元公设) |
| `statement` | 核心陈述 | 一句话,不可证伪的底层假设或公式 |
| `verification` | 验证方法 | 科学如何证明或推导它 |
| `boundary` | 适用边界 | 什么条件下失效/被替代 |
| `contributor` | 贡献者 | GitHub 用户名 |
| `created` | 创建日期 | YYYY-MM-DD |

**status 相关字段**:

| status | 额外必填 | 约束 |
|---|---|---|
| `axiom` | `peel_result`(pass/review/fail) + `peel_evidence`(≥40字,含不可还原性论证) | `derived_from` 必须为空 |
| `theorem` | `derived_from`(推导来源)+ `downgrade_to`(降级轨迹) | 引用必须真实存在 |
| `fact` / `hypothesis` | `downgrade_to` | 明确标注非公设 |
| `meta` | 无 | 放 `principles/meta/` |

## 3. 剥离审计是强制门槛

每条 `axiom` 都必须回答同一个问题:

> **"这条能不能从更底层原理推导出来?如果能,为什么它不算那个原理的推论?"**

`peel_evidence` 就是你的回答。写不出来 = 不该是公设 = 请降级为 theorem/fact。词表见 `rules/peeling-audit.yaml`——如果你的条目主题命中词表(如"牛顿三定律""供求定律""停机问题"),falsify.py 会标记你,你必须在 `peel_evidence` 里自辩。

## 4. 什么不该提交(会被软门禁标记或评审打回)

- ❌ **定理当公设**:可推导的(完备性定理、诺特定理、停机问题…)→ 标 `theorem`
- ❌ **机制当公设**:原理上可还原的(自发对称性破缺、奖赏预测误差…)→ 标 `theorem` 或 `fact`
- ❌ **事实当公设**:观测到的(暗能量、LUCA、手性均一…)→ 标 `fact`
- ❌ **假说当公设**:未决的(自组织临界、强涌现…)→ 标 `hypothesis`
- ❌ **哲学立场当学科公设** → 放 `principles/meta/`,标 `meta`
- ❌ **概念/定义当原理**(酸碱定义、电负性数值) → 不收录

## 5. 贡献者义务

1. **自己先跑门禁**——不要用 CI 当你的本地调试器。
2. **PR 描述模板**(复制用):

```markdown
## 新增/修改条目
- [ ] 条目 ID:
- [ ] 层级:
- [ ] status:
- [ ] 剥离证据(peel_evidence)已写,核心论证一句话:
- [ ] 本地已跑 validate.py(通过 / 失败已修)
- [ ] falsify.py 待审项回应(如有):
- [ ] 引用关系已维护(derived_from / derives 双向一致):
```

## 6. 评审人义务(见 REVIEW.md)

- 评审人不等于"点赞"——你的核心任务是**尝试杀死这条公设**(找它的推导来源)。
- 每条 axiom 至少 1 名评审人 approve;核心层级(L1/L2/L5)建议 2 名。

## 7. 行为准则(简短版)

- 学术诚实第一:不确定就标 `hypothesis`,不硬撑 `axiom`。
- 尊重"剥离审计"——被降级不是失败,是科学的胜利。
- 欢迎挑战既有条目(见 FALSIFY.md 的证伪挑战协议)。
