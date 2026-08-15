#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate.py — 第一性原理仓库「硬校验器」

职责(全部为机器可判定的硬门禁,任一失败 => CI 红):
  1. 结构校验   : front matter 必填字段、字段格式、状态枚举、剥离审计字段合法性
  2. ID 唯一性  : 全库 id 无重复
  3. 层级一致性 : 文件所在目录(如 principles/L2-physics)必须与 front matter 的 layer 一致
  4. 引用完整性 : derived_from / derives 引用的 id 必须真实存在(悬空引用 = 失败)
  5. 推导图无环 : derived_from 构成的推导图不得有环(A 推导自 B,B 推导自 A 即失败)
  6. 双向一致性 : 若 A.derives 含 B,则 B.derived_from 必须含 A(反向亦然)
  7. 剥离字段规则: status=axiom 必须提供 peel_result + peel_evidence;其余状态必须提供
     downgrade_to(被降级后的去向)说明,且不得谎称 axiom。

用法:
  python3 validate.py [仓库根目录]     # 默认 ./
退出码: 0 = 通过;1 = 校验失败(供 CI 判断)
"""
import sys
import re
import os
from pathlib import Path

try:
    import yaml
except ImportError:
    print("需要 PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# ---------- 常量 ----------
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
PRINCIPLES_DIR = ROOT / "principles"
SCHEMA_PATH = ROOT / "rules" / "schema.yaml"

ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)
    print(f"  [FAIL] {msg}")


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print(f"  [WARN] {msg}")


def load_schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_front_matter(text: str) -> tuple[dict, str]:
    """解析 YAML front matter(--- ... ---),返回 (meta, body)"""
    if not text.startswith("---"):
        raise ValueError("缺少 YAML front matter 分隔符 '---'")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("front matter 未闭合(缺少第二个 '---')")
    meta = yaml.safe_load(parts[1])
    return (meta or {}, parts[2])


def collect_entries(schema: dict) -> dict[str, dict]:
    """扫描 principles/ 下所有 .md,返回 {id: entry_info}

    结构盲区治理(活体测试 PR#1 暴露):
    - 引擎只扫 principles/,陌生提交放在任意其他目录(如 stranger/)会完全绕过检查。
    - 故此处同时扫描全仓 .md,凡位于原理内容目录之外的文件一律报错,
      避免"内容绕过扫描"的假阳性 CI 绿灯。
    """
    layer_map = schema["layers"]
    allowed_dirs = set(layer_map.keys())
    # 允许的非内容目录(README/docs/tests/.github 等,它们不承载原理条目)
    non_content_dirs = {"docs", "tests", ".github", "scripts", "rules", "node_modules", ".git"}
    # 根级合法文档(不是原理条目,全仓扫描须放行)
    root_allowed_md = {"README.md", "AGENTS.md", "CONTRIBUTORS.md"}

    entries: dict[str, dict] = {}

    # 全仓 .md 扫描,拦截"目录逃逸"的条目文件
    for md in sorted(ROOT.rglob("*.md")):
        rel = md.relative_to(ROOT)
        parts = rel.parts
        if len(parts) < 2:
            # 根目录:白名单内的文档(README/AGENTS/CONTRIBUTORS)放行,其余 .md 视为可疑
            if md.name not in root_allowed_md:
                warn(f"{rel}: 位于仓库根目录的非白名单 .md 文件,请放入 principles/、docs/ 或列入白名单")
            continue
        top = parts[0]
        if top in non_content_dirs:
            continue
        if top == "principles":
            # principles/ 下:第二层必须是合法层级目录;第三层起必须是 *.md 条目
            if len(parts) >= 2 and parts[1] not in allowed_dirs and not md.name.startswith("README"):
                err(f"{rel}: 位于 principles/ 下非法子目录 '{parts[1]}',层级目录必须是 {sorted(allowed_dirs)}")
            continue
        if top not in allowed_dirs:
            # 结构盲区:出现在非原理目录(如 stranger/)的内容文件必须被拦截
            err(f"{rel}: 位于非法目录 '{top}',原理条目必须放在 principles/L{{n}}-* 下;"
                f"引擎不扫描该目录,内容将绕过剥离审计——请移动或删除")
            continue

    for subdir in PRINCIPLES_DIR.iterdir():
        if not subdir.is_dir() or subdir.name not in layer_map:
            continue
        expected_layer = layer_map[subdir.name]
        for md in subdir.glob("*.md"):
            # README 等文档跳过
            if md.name.startswith("README"):
                continue
            try:
                meta, body = parse_front_matter(md.read_text(encoding="utf-8"))
            except Exception as e:
                err(f"{md.relative_to(ROOT)}: front matter 解析失败: {e}")
                continue
            entry = {
                "path": md.relative_to(ROOT).as_posix(),
                "meta": meta,
                "body_len": len(body.strip()),
                "dir": subdir.name,
                "expected_layer": expected_layer,
            }
            # 以 front matter 的 id 作为全局唯一键(文件名只是助记)
            key = str(meta.get("id") or md.stem)
            if key in entries:
                err(f"{md.relative_to(ROOT)}: id '{key}' 与 {entries[key]['path']} 重复(ID 必须全局唯一)")
                continue
            entries[key] = entry
    return entries


def check_structure(meta: dict, entry: dict, schema: dict) -> None:
    """必填字段 + 格式规则"""
    p = entry["path"]
    for f in schema["required_fields"]:
        if f not in meta or meta[f] in (None, ""):
            err(f"{p}: 缺少必填字段 '{f}'")

    rules = schema["field_rules"]
    # id 格式
    if "id" in meta:
        pat = rules["id"]["pattern"]
        if not re.match(pat, str(meta["id"])):
            err(f"{p}: id '{meta['id']}' 不符合格式 {pat}")
    # layer 范围
    if "layer" in meta:
        lay = meta["layer"]
        if not (rules["layer"]["min"] <= lay <= rules["layer"]["max"]):
            err(f"{p}: layer {lay} 超出范围 0-10")
    # status 枚举
    if "status" in meta and meta["status"] not in schema["statuses"]:
        err(f"{p}: status '{meta['status']}' 不在枚举 {schema['statuses']}")
    # peel_result 枚举
    if "peel_result" in meta and meta["peel_result"] not in schema["peel_results"]:
        err(f"{p}: peel_result '{meta['peel_result']}' 不在枚举")


def check_layer_consistency(meta: dict, entry: dict) -> None:
    """目录必须与 layer 一致"""
    if "layer" not in meta:
        return
    if entry["expected_layer"] == 0:
        if meta["layer"] != 0:
            err(f"{entry['path']}: 位于 meta/ 目录但 layer={meta['layer']},应为 0")
    elif meta["layer"] != entry["expected_layer"]:
        err(
            f"{entry['path']}: 目录 {entry['dir']}(期望 layer={entry['expected_layer']})"
            f" 与 front matter layer={meta['layer']} 不一致"
        )


def check_refs(meta: dict, entry: dict, all_ids: set[str]) -> None:
    """引用完整性:derived_from / derives 必须真实存在"""
    p = entry["path"]
    for field in ("derived_from", "derives"):
        refs = meta.get(field, [])
        if not isinstance(refs, list):
            err(f"{p}: {field} 应为列表")
            continue
        for rid in refs:
            if rid not in all_ids:
                err(f"{p}: {field} 引用了不存在的 id '{rid}'")


def check_peel_rules(meta: dict, entry: dict, schema: dict) -> None:
    """
    剥离审计字段规则:
      - axiom: 必须带 peel_result + peel_evidence(满足最低要求)
      - 非 axiom(theorem/fact/hypothesis): 必须带 downgrade_to,且不得声称已通过剥离
    """
    p = entry["path"]
    status = meta.get("status")
    min_req = schema.get("peel_evidence_minimum", {})

    if status == "axiom":
        if "peel_result" not in meta:
            err(f"{p}: status=axiom 必须提供 peel_result(pass/review/fail)")
        elif meta["peel_result"] == "fail":
            err(f"{p}: peel_result=fail 却保持 status=axiom,自相矛盾;应降级")
        if "peel_evidence" not in meta:
            err(f"{p}: status=axiom 必须提供 peel_evidence(不可还原性论证)")
        else:
            ev = meta["peel_evidence"]
            if len(ev) < min_req.get("min_chars", 40):
                err(f"{p}: peel_evidence 过短({len(ev)}字符 < {min_req.get('min_chars', 40)}),空话不算证据")
            if min_req.get("must_rebut"):
                kws = min_req.get("suggest_rebut_keywords", [])
                if not any(k in ev for k in kws):
                    warn(f"{p}: peel_evidence 未含明确的'不可还原'反驳词(如 {kws[:4]}),评审时重点复核")
        # axiom 不应有 derived_from
        if meta.get("derived_from"):
            err(f"{p}: status=axiom 却声明 derived_from={meta['derived_from']}——可推导的东西不是公设")
    elif status in ("theorem", "fact", "hypothesis"):
        if "downgrade_to" not in meta:
            err(f"{p}: status={status} 必须提供 downgrade_to 说明(原为哪条公设/为何被降级)")
        if meta.get("peel_result") == "pass":
            warn(f"{p}: 非 axiom 却标记 peel_result=pass,语义混乱(剥离审计只针对 axiom),建议删除该字段")
    elif status == "meta":
        # 元公设:关于学科的哲学前提,不要求剥离审计
        pass


def check_cycle_and_bidirection(entries: dict[str, dict], all_ids: set[str]) -> None:
    """
    推导图无环 + 双向一致性。
    边:A.derived_from 含 B  =>  A 推导自 B(方向 A -> B? 不,是 B 推 A)
    我们建模:A.derived_from = [B] 表示 A 由 B 推导 => 边 B -> A。
    环 = 存在 B -> ... -> B。用 DFS 判环。
    双向一致性:A.derives 含 B <=> B.derived_from 含 A。
    """
    # 建图:parent -> [children]
    graph: dict[str, set[str]] = {i: set() for i in all_ids}
    for eid, entry in entries.items():
        for ref in entry["meta"].get("derived_from", []):
            if ref in all_ids:
                graph[ref].add(eid)

    # DFS 判环
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {i: WHITE for i in all_ids}

    def dfs(node: str, stack: list[str]) -> None:
        color[node] = GRAY
        stack.append(node)
        for child in graph[node]:
            if color[child] == GRAY:
                cycle = stack[stack.index(child):] + [child]
                err(f"推导图存在环: {' -> '.join(cycle)}")
            elif color[child] == WHITE:
                dfs(child, stack)
        stack.pop()
        color[node] = BLACK

    for n in all_ids:
        if color[n] == WHITE:
            dfs(n, [])

    # 双向一致性
    for eid, entry in entries.items():
        p = entry["path"]
        for ref in entry["meta"].get("derives", []):
            if ref in entries:
                if eid not in entries[ref]["meta"].get("derived_from", []):
                    err(f"{p}: 声明 derives={ref},但 {entries[ref]['path']} 的 derived_from 未包含 {eid}(双向不一致)")
        for ref in entry["meta"].get("derived_from", []):
            if ref in entries:
                if eid not in entries[ref]["meta"].get("derives", []):
                    err(f"{p}: 声明 derived_from={ref},但 {entries[ref]['path']} 的 derives 未包含 {eid}(双向不一致)")


def check_body_nonempty(entry: dict) -> None:
    if entry["body_len"] < 20:
        err(f"{entry['path']}: 正文过短({entry['body_len']}字符),仅有 front matter 不算条目")


def main() -> int:
    print(f"=== validate.py · 硬校验 仓库={ROOT.resolve()} ===")
    schema = load_schema()
    entries = collect_entries(schema)
    if not entries:
        err("principles/ 下未找到任何条目")
        return 1

    all_ids = set(entries.keys())
    print(f"扫描到 {len(entries)} 个条目")

    for eid, entry in entries.items():
        meta = entry["meta"]
        check_structure(meta, entry, schema)
        check_layer_consistency(meta, entry)
        check_refs(meta, entry, all_ids)
        check_peel_rules(meta, entry, schema)
        check_body_nonempty(entry)

    check_cycle_and_bidirection(entries, all_ids)

    print("-" * 50)
    print(f"结果: {len(ERRORS)} 错误, {len(WARNINGS)} 警告")
    if ERRORS:
        print("==> 硬校验失败(CI 将标红)。修复以上 [FAIL] 项后重跑。")
        return 1
    print("==> 硬校验通过 (OK)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
