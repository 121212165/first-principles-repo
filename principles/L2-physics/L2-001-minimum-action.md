---
id: L2-001
layer: 2
name: 最小作用量原理
status: axiom
category: dynamics
statement: 物理系统的实际演化使作用量 S=∫L dt 取驻值;全部经典力学、电磁学、引力与量子理论皆可由此单一表述导出。
verification: 从它推出牛顿方程、麦克斯韦方程、爱因斯坦场方程;费曼路径积分将其推广为量子原理;拉格朗日力学的全部实验验证。
boundary: 量子层级中"取驻值"退化为"所有路径等权叠加",极值不再是规律而是 ħ→0 的近似;若存在不可积约束或非拉格朗日动力学,表述需修改。
peel_result: pass
peel_evidence: 不可还原——它是牛顿力学的更深基础而非其推论(牛顿方程由它导出,反向不能),且先于"力"概念(力是它的衍生概念);没有任何更底层原理能推导出"作用量取驻值"这一假设本身,它是对物理规律形式的元假设。
derives: []
contributor: example-contributor
created: 2026-08-06
reviewed_by: []
---

## 说明

本文件是 **axiom(公设)** 的示例条目,演示:

1. `status: axiom` 必须同时提供 `peel_result: pass` + `peel_evidence`(长度 ≥40 字符且含"不可还原"类反驳词)。
2. axiom 的 `derived_from` 必须为空——若声明了推导来源,validate.py 会判定"可推导的东西不是公设"。
3. 正文可以任意展开,但 front matter 是机器校验的唯一依据。

## 正文

最小作用量原理的地位:它是物理学的"宪法第一条款"——不描述任何具体力,而规定"物理定律必须采取驻值形式"。这一规定无法从任何实验事实推出(它是公设),却能推出全部动力学。
