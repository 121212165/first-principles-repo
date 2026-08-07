#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_gates.py — 门禁回归测试(陌生人提交模拟)

把"完整性测试"固化为可持续回归:每次 CI 都验证两道门禁对
"无上下文陌生人提交"的拦截能力,防止词表/引擎退化。

设计:
- 在临时目录重建迷你仓库(rules/ + scripts/ + principles/ 示例)
- 注入 tests/stranger-submission/ 的陌生人提交
- 断言:阶段 A 8 条原生提交被 validate 全拦;阶段 B 3 条合规提交
  通过 validate 但被 falsify 抓出内容问题;缺 status 条目被 info 点名。

用法:
  python -m unittest discover -s tests -p "test_*.py" -v
  python tests/test_gates.py -v
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STRANGER = REPO / "tests" / "stranger-submission"

# 阶段 A:8 条原生陌生人提交 -> 目标层级目录
PHASE_A = {
    "godel-theorem.md": "L1-logic-math",
    "heisenberg-uncertainty.md": "L2-physics",
    "equivalent-principle.md": "L2-physics",
    "born-rule.md": "L2-physics",
    "physicalism.md": "L5-neuroscience",
    "scarcity.md": "L7-economics",
    "emergence.md": "L10-complexity",
    "universal-darwinism.md": "L10-complexity",
}

# 阶段 B:3 条格式合规但内容有问题的提交
PHASE_B = {
    "phase-b/godel-compliant.md": "L1-logic-math",      # 哥德尔不完备当公设
    "phase-b/heisenberg-compliant.md": "L2-physics",    # 海森堡不确定性当公设
    "phase-b/shannon-compliant.md": "L6-computation",   # 香农熵当公设(立场冲突)
}


def build_tmp_repo() -> Path:
    """在临时目录重建迷你仓库"""
    tmp = Path(tempfile.mkdtemp(prefix="fp-gates-"))
    for d in ("rules", "scripts"):
        shutil.copytree(REPO / d, tmp / d)
    shutil.copytree(REPO / "principles", tmp / "principles")
    return tmp


def run_tool(tool: str, cwd: Path) -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, f"scripts/{tool}", "."],
        cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=120,
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def inject(tmp: Path, mapping: dict[str, str]) -> None:
    for src, lay in mapping.items():
        shutil.copy(STRANGER / src, tmp / "principles" / lay / Path(src).name)


class TestPhaseA_HardGate(unittest.TestCase):
    """阶段 A:原生陌生人提交必须被 validate 全拦"""

    def test_all_eight_blocked(self):
        tmp = build_tmp_repo()
        try:
            inject(tmp, PHASE_A)
            code, out = run_tool("validate.py", tmp)
            self.assertNotEqual(code, 0, "硬校验应拦截全部 8 条陌生人提交")
            for f in PHASE_A:
                self.assertIn(f, out, f"{f} 未被硬校验点名")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_invisible_status_hinted(self):
        """缺 status 的条目应被 falsify 以 info 点名(隐形条目治理)"""
        tmp = build_tmp_repo()
        try:
            inject(tmp, PHASE_A)
            code, out = run_tool("falsify.py", tmp)
            self.assertIn("隐形条目", out, "缺 status 条目应被 info 点名")
            self.assertIn("info", out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestPhaseB_SoftGate(unittest.TestCase):
    """阶段 B:格式合规但内容错误,validate 放过、falsify 必须抓出"""

    def test_compliant_pass_validate(self):
        tmp = build_tmp_repo()
        try:
            inject(tmp, PHASE_B)
            code, out = run_tool("validate.py", tmp)
            self.assertEqual(code, 0, f"阶段 B 条目应通过硬校验:\n{out}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_falsify_catches_theorem_as_axiom(self):
        """哥德尔/海森堡(定理冒充公设)必须被 falsify 标记"""
        tmp = build_tmp_repo()
        try:
            inject(tmp, PHASE_B)
            code, out = run_tool("falsify.py", tmp)
            self.assertIn("L1-099", out, "哥德尔当公设未被标记")
            self.assertIn("L2-099", out, "海森堡当公设未被标记")
            # 至少出现 suspect(词表命中)或 overlap(与既有条目重复)
            self.assertTrue("suspect" in out or "overlap" in out,
                            "内容错误应有 suspect/overlap 标记")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_falsify_catches_shannon(self):
        """香农熵(词表立场冲突)必须被 falsify 标记,不得因命名变体漏网"""
        tmp = build_tmp_repo()
        try:
            inject(tmp, {"phase-b/shannon-compliant.md": "L6-computation"})
            code, out = run_tool("falsify.py", tmp)
            self.assertIn("L6-099", out, "香农熵当公设未被标记")
            self.assertTrue("suspect" in out or "overlap" in out,
                            "香农熵应有 suspect/overlap 标记")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestBaseline(unittest.TestCase):
    """基线:干净仓库(仅示例条目)应通过 validate"""

    def test_baseline_clean(self):
        tmp = build_tmp_repo()
        try:
            code, out = run_tool("validate.py", tmp)
            self.assertEqual(code, 0, f"基线应通过硬校验:\n{out}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
