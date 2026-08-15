## 提交前自检(机器会替你再查一遍)

- [ ] 条目放对目录了?必须 `principles/L{n}-*/`(别放仓库根目录、stranger/ 之类——CI 全仓扫描,目录逃逸直接红)
- [ ] front matter 齐全?`id` / `layer`(与目录一致)/ `name` / `status` / `statement` / `verification` / `boundary` / `contributor` / `created`
- [ ] `status: axiom`?→ 必须有 `peel_result` + `peel_evidence`(≥40 字,含"不可还原"类反驳),且 `derived_from` 为空
- [ ] `status: theorem`?→ `derived_from` 引用的条目必须真实存在
- [ ] 本地已跑 `python scripts/validate.py .`(红 = 别提交)
- [ ] 本地已跑 `python scripts/falsify.py .`(待审项逐条回应了吗?)
- [ ] 这不是"定理冒充公设"吧?(剥离词表:牛顿三定律、热力学第二定律、停机问题、香农熵……命中就要自辩)

> 不确定就标 `hypothesis`,别硬撑 `axiom`。质量优先于数量。

## 变更内容

<!-- 简述你提交了什么、为什么它是"不可再下推的基石" -->

## 门禁结果

| 门禁 | 结果 |
|---|---|
| validate.py(本地) | 通过 / 失败已修 |
| falsify.py 待审项 | 无 / 已逐条回应(见上) |
