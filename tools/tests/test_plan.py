import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "plan", Path(__file__).resolve().parents[2] / "bootstrap" / "plan.py"
)
plan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plan)

DATA = {
    "package": [
        {"name": "sh", "tier": "mandatory", "apt": "dash"},
        {"name": "nopkg-tool-x", "tier": "mandatory", "fallback": "https://example.invalid"},
        {"name": "nopkg-tool-y", "tier": "mandatory"},
        {"name": "has-pkg-z", "tier": "recommended", "apt": "zed", "bins": ["not-installed-z"]},
        {"name": "opt-w", "tier": "optional", "apt": "w", "bins": ["not-installed-w"]},
    ]
}


def test_installed_tools_are_skipped():
    assert all(a[1] != "sh" for a in plan.plan(DATA, "apt", {"mandatory", "recommended"}))


def test_each_kind_of_action():
    kinds = {a[1]: a[0] for a in plan.plan(DATA, "apt", {"mandatory", "recommended"})}
    assert kinds == {"nopkg-tool-x": "fallback", "nopkg-tool-y": "unavailable", "has-pkg-z": "pkg"}


def test_tiers_filter():
    names = {a[1] for a in plan.plan(DATA, "apt", {"optional"})}
    assert names == {"opt-w"}


def test_manager_without_an_id_falls_back():
    kinds = {a[1]: a[0] for a in plan.plan(DATA, "pacman", {"recommended"})}
    assert kinds == {"has-pkg-z": "unavailable"}
