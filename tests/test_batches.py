"""Phase 6: batch tool (tools/batches.py) - dialogue pages compose back into the entry's codes, layout strings keep
their codes, glossary terms match whole katakana runs only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import font  # noqa: E402
import windows  # noqa: E402

DLG = {"id": "ch99.000000", "box": "upper", "ptrs": [],
       "jp": "{clr}{pos:00000000}{full}リアド・・・{wait}{clr}{pos:00000000}{full}ダメだ{nl}もどれ！{wait}"}
LAYOUT = {"id": "system.999999", "ptrs": [], "jp": "{pos:02000000}{half}つかう{pos:02000100}うる"}


def check(e, text):
    gl, w = batches.glossary(), font.widths()
    return batches.check_entry(e, text, gl, windows.load(), w, set(w) | {" "})


def test_dialogue_pages_compose():
    assert batches.form(DLG) == "dlg"
    en = batches.compose(DLG, "Riad... || No! Go back!")
    assert en == "{clr}{pos:00000000}{full}Riad...{wait}{clr}{pos:00000000}{full}No! Go back!{wait}"
    assert check(DLG, "Riad... || No! Go back!") == []
    assert any("pages" in x for x in check(DLG, "Riad... No! Go back!"))


def test_layout_keeps_codes():
    assert batches.form(LAYOUT) == "layout"
    assert any("control codes" in x for x in check(LAYOUT, "{pos:02000000}{half}Use Sell"))


def test_katakana_whole_run():
    assert batches.term_in("カイ", "カイ、行くぞ")
    assert not batches.term_in("カイ", "カイザーペンギン")
