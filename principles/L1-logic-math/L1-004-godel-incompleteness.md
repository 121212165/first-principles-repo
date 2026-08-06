---
id: L1-004
layer: 1
name: 哥德尔不完备性定理
status: theorem
category: proof-theory
statement: 任何一致且蕴含皮亚诺算术的正式系统,都存在既不可证又不可否证的命题;系统的"可证集"严格小于其"真集"。
verification: 哥德尔编码 + 对角线引理(1931);自指构造的严格证明。
boundary: 普雷斯伯格算术(无乘法)是完备的;更强系统不完备性更剧;它刻画的是"形式化"这种人类表达方式本身的固有上限。
derived_from:
  - L1-005
derives: []
downgrade_to: 原列为公设,经四轮审计判定为定理——由有穷语法(L1-005)+对角线引理严格证明,但"不可绕过",保留为基石定理。
contributor: example-contributor
created: 2026-08-06
reviewed_by: []
---

## 说明

本文件是 **theorem(定理)** 的示例条目,演示:

1. `status: theorem` 必须提供 `derived_from`(推导自哪些公设/更底层定理)——引用必须真实存在,否则 validate.py 硬失败。
2. 必须提供 `downgrade_to`:交代"原为公设,为何被降级"的审计轨迹。
3. `derives` 是反向边,若填写则目标条目的 `derived_from` 必须包含本 id(双向一致性校验)。

## 正文

哥德尔不完备性在本仓库中的特殊地位:它是定理(可严格证明),但具有"基石性"——它定义了形式化知识的边界,因此保留在定理区而非被彻底移除。
