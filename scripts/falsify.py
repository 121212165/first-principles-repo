#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
falsify.py — 第一性原理仓库「证伪引擎 / 剥离审计」(软门禁)

与 validate.py 的分工:
  validate.py = 硬门禁 —— 结构/引用/层级,机器可判定,失败 => CI 红。
  falsify.py  = 软门禁 —— 证伪报告,不阻断合并,但生成"剥离审计报告"
                作为 PR 评论/制品,要求贡献者回应。

职责:
  1. 剥离词表命中检测: 每条 status=axiom 的条目,若 statement/正文/peel_evidence
     命中 rules/peeling-audit.yaml 中本层级的"可剥离主题"(如牛顿三定律、供求定律),
     则标记为"疑似可推导",要求证明为什么这条不是该主题的展开。
  2. 同层可推导性启发式: 若某 axiom 的 name/statement 与同层另一条 axiom 存在
     明显语义重叠(按剥离词表 or 关键词),标记"疑似合并候选"。
  3. 层级错位检测: 词表中"应当属于 L_n"的主题出现在错误层级(如把熵增写进 L3),
     标记"疑似层级错位"。
  4. 生成剥离审计报告(CI artifact): 每层的通过率、待审清单、历史挑战记录。

用法:
  python3 falsify.py [仓库根目录] [--json out.json]
退出码: 0 = 完成(软门禁永不红,但退出码区分: 2 = 有"疑似可推导"待审)
"""
import sys
import re
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    print("需要 PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
AUDIT_PATH = ROOT / "rules" / "peeling-audit.yaml"
SCHEMA_PATH = ROOT / "rules" / "schema.yaml"
PRINCIPLES_DIR = ROOT / "principles"
REPORT_DIR = ROOT / ".ci-report"

# 严重度级别
SEV_SUSPECT = "suspect"      # 命中词表,疑似可推导(需贡献者回应)
SEV_OVERLAP = "overlap"      # 同层重叠,疑似合并
SEV_MISPLACE = "misplaced"   # 层级错位


def parse_front_matter(text: str) -> tuple[dict, str]:
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, ""
    return yaml.safe_load(parts[1]) or {}, parts[2]


def collect_entries() -> list[dict]:
    layer_map = {}
    if SCHEMA_PATH.exists():
        schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
        layer_map = schema.get("layers", {})
    entries = []
    for subdir in PRINCIPLES_DIR.iterdir():
        if not subdir.is_dir():
            continue
        for md in subdir.glob("*.md"):
            if md.name.startswith("README"):
                continue
            meta, body = parse_front_matter(md.read_text(encoding="utf-8"))
            entries.append({
                "id": meta.get("id", md.stem),
                "path": md.relative_to(ROOT).as_posix(),
                "meta": meta,
                "body": body,
                "dir": subdir.name,
            })
    return entries


def load_audit() -> dict:
    if not AUDIT_PATH.exists():
        print(f"[WARN] 找不到剥离词表 {AUDIT_PATH},证伪引擎空转")
        return {"layers": {}}
    return yaml.safe_load(AUDIT_PATH.read_text(encoding="utf-8"))


def hit_list(text: str, patterns: list) -> list[str]:
    hits = []
    for p in patterns:
        # 支持正则:^ 前缀表正则,其余按子串
        if isinstance(p, str):
            if p in text:
                hits.append(p)
        elif isinstance(p, dict):  # {"pattern": ..., "note": ...}
            pat = p["pattern"]
            if pat in text:
                hits.append(pat)
    return hits


def main() -> int:
    print(f"=== falsify.py · 证伪引擎 / 剥离审计 仓库={ROOT.resolve()} ===")
    audit = load_audit()
    audit_layers = audit.get("layers", {})
    entries = collect_entries()
    print(f"扫描到 {len(entries)} 个条目")

    findings = []          # 待审清单
    stats = {"axiom": 0, "theorem": 0, "fact": 0, "hypothesis": 0, "meta": 0,
             "suspect": 0, "overlap": 0, "misplaced": 0}

    # 索引: id -> entry; 层级 -> entries
    by_id = {e["id"]: e for e in entries}
    by_layer: dict[int, list] = {}
    for e in entries:
        lay = e["meta"].get("layer", 0)
        by_layer.setdefault(lay, []).append(e)
        stats[e["meta"].get("status", "?")] = stats.get(e["meta"].get("status", "?"), 0) + 1

    for e in entries:
        meta = e["meta"]
        status = meta.get("status")
        lay = meta.get("layer", 0)
        if status != "axiom":
            continue
        stats["axiom"] += 1
        text = (str(meta.get("statement", "")) + "\n" + str(meta.get("name", ""))
                + "\n" + e["body"])
        layer_audit = audit_layers.get(str(lay), {})

        # 1) 词表命中 => 疑似可推导(但若 peel_evidence 已主动回应该词,降级为 info)
        peel_topics = layer_audit.get("peel", [])
        hits = hit_list(text, peel_topics)
        ev = str(meta.get("peel_evidence", ""))
        # 自辩判定:命中词也出现在 peel_evidence 中(且证据含反驳词) => 贡献者已处理
        self_defended = [
            h for h in hits
            if h in ev and any(k in ev for k in ("不是", "推论", "区别于", "不可还原", "不可推导", "先于", "独立于"))
        ]
        unhandled = [h for h in hits if h not in self_defended]
        if unhandled:
            stats["suspect"] += 1
            findings.append({
                "severity": SEV_SUSPECT,
                "id": e["id"], "path": e["path"], "layer": lay,
                "reason": f"命中剥离词表: {unhandled[:5]}",
                "action": "请在 peel_evidence 中论证该条不是此主题的展开,或降级为 theorem/fact",
            })
        if self_defended:
            findings.append({
                "severity": "info",
                "id": e["id"], "path": e["path"], "layer": lay,
                "reason": f"提及词表主题 {self_defended[:5]} 但 peel_evidence 已自辩,评审时复核",
                "action": "无需操作(自动降级为 info)",
            })

        # 2) 词表"必留"检查: 该层级是否有人负责核心公设(软检查,防漏)
        must_have = layer_audit.get("must_cover", [])
        layer_text = " ".join(str(x["meta"].get("name", "")) for x in by_layer.get(lay, []))
        missing = [m for m in must_have if m not in layer_text]
        if missing and not layer_audit.get("allow_incomplete", False):
            stats["misplaced"] += 1
            findings.append({
                "severity": SEV_MISPLACE,
                "id": e["id"], "path": e["path"], "layer": lay,
                "reason": f"层级 {lay} 的必覆盖主题缺失: {missing}(穷尽性检查)",
                "action": "补充该主题的条目,或在词表中声明 allow_incomplete",
            })

        # 3) 层级错位: 该条目的主题是否属于别的层级的 peel 表?
        for other_lay, other_audit in audit_layers.items():
            if other_lay == str(lay):
                continue
            ohits = hit_list(text, other_audit.get("peel", []))
            if ohits:
                stats["misplaced"] += 1
                findings.append({
                    "severity": SEV_MISPLACE,
                    "id": e["id"], "path": e["path"], "layer": lay,
                    "reason": f"主题命中层级 {other_lay} 的剥离词表({ohits[:3]}),疑似层级错位",
                    "action": "确认该条目的正确层级;若属本层,请在 peel_evidence 说明跨层引用理由",
                })

        # 4) 剥离证据质量(ev 已在上方定义,直接复用)
        if len(ev) < 40:
            stats["suspect"] += 1
            findings.append({
                "severity": SEV_SUSPECT,
                "id": e["id"], "path": e["path"], "layer": lay,
                "reason": "peel_evidence 过短,无实质论证",
                "action": "补全不可还原性论证(为什么不能被更底层推导)",
            })

    # 5) 同层语义重叠(两两比较 name/statement 的关键词 Jaccard 粗略检测)
    names_by_layer = {lay: [(e["id"], str(e["meta"].get("name", ""))) for e in lst]
                      for lay, lst in by_layer.items()}
    for lay, lst in names_by_layer.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                ida, na = lst[i]
                idb, nb = lst[j]
                # 粗重叠: 共享 >2 个汉字词
                common = set(na) & set(nb)
                han_common = [c for c in common if "\u4e00" <= c <= "\u9fff"]
                if len(han_common) >= 3:
                    stats["overlap"] += 1
                    findings.append({
                        "severity": SEV_OVERLAP,
                        "id": ida, "path": f"{ida}", "layer": lay,
                        "reason": f"与 {idb}({nb}) 名称高度重叠: {''.join(han_common[:6])}",
                        "action": "确认二者是否应合并或明确区分边界",
                    })

    # 输出报告
    REPORT_DIR.mkdir(exist_ok=True)
    report = {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "stats": stats,
        "findings": findings,
        "summary": {
            "total_axioms": stats.get("axiom", 0),
            "suspect_count": stats.get("suspect", 0),
            "overlap_count": stats.get("overlap", 0),
            "misplaced_count": stats.get("misplaced", 0),
            "peel_pass_rate": round(1 - (stats.get("suspect", 0) / max(1, stats.get("axiom", 0))), 3),
        },
    }
    report_path = REPORT_DIR / "peel-audit-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n报告已生成: {report_path}")

    print("-" * 50)
    print(f"axiom 总数: {stats.get('axiom', 0)} | 疑似可推导: {stats.get('suspect', 0)}"
          f" | 疑似重叠: {stats.get('overlap', 0)} | 疑似错位: {stats.get('misplaced', 0)}")
    if findings:
        print("\n待审清单(前 15 条):")
        for f in findings[:15]:
            print(f"  [{f['severity']}] {f['id']}: {f['reason']}")
        print(f"\n...共 {len(findings)} 条待审项,详见报告。")
        print("软门禁结论: 不阻断合并,但贡献者须在 PR 中逐条回应(见 docs/FALSIFY.md)")
        return 2
    print("软门禁结论: 本批无待审项 (OK)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
