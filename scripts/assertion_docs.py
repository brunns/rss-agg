# Copyright 2024-2026 Simon Brunning
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Compile every hamcrest `assert_that` in a test suite into a single HTML docs page.

Usage: uv run assertion_docs.py [--tests tests] [--output build/assertion_docs.html] [--matcher-package mylib]

Standard library only, and independent of the project it documents. Test files and matcher libraries are parsed
with `ast`, never imported, so the page builds even when the test suite (or a matcher library) can't be imported.
Matcher docstrings are found in the project's `.venv` if there is one, otherwise on the running interpreter's path.
"""

from __future__ import annotations

import argparse
import ast
import html
import importlib.machinery
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path

MATCHER_PACKAGES = ("hamcrest", "brunns")
WORDS = {"inanyorder": "in any order"}
ACRONYMS = {
    "cli": "CLI",
    "rss": "RSS",
    "s3": "S3",
    "url": "URL",
    "urls": "URLs",
    "xml": "XML",
    "guid": "GUID",
    "http": "HTTP",
    "api": "API",
    "id": "ID",
    "json": "JSON",
    "html": "HTML",
    "sql": "SQL",
}

type Linker = Callable[[Path, int], str]


@dataclass(frozen=True)
class MatcherNode:
    """One matcher in a nested matcher expression: its words, its literal arguments, and any nested matchers."""

    label: str
    values: tuple[str, ...] = ()
    children: tuple[MatcherNode, ...] = ()


@dataclass(frozen=True)
class Assertion:
    line: int
    source: str
    actual: str
    tree: MatcherNode | None
    matchers: tuple[str, ...]
    warning: str | None


@dataclass
class TestCase:
    name: str
    line: int
    doc: str | None
    assertions: list[Assertion] = field(default_factory=list)
    other_checks: tuple[str, ...] = ()


@dataclass
class TestFile:
    path: Path
    tests: list[TestCase]
    matchers: dict[str, str]


@dataclass(frozen=True)
class MatcherInfo:
    name: str
    module: str
    uses: int
    doc: str | None


@dataclass(frozen=True)
class GitInfo:
    sha: str | None
    dirty: bool
    linker: Linker


def build_assertion_docs(test_root: Path, matcher_packages: tuple[str, ...] = MATCHER_PACKAGES) -> str:
    """Parse all tests under `test_root` and return a self-contained HTML page documenting their assertions."""
    root = repo_root(test_root)
    paths = sorted({*test_root.rglob("test_*.py"), *test_root.rglob("*_test.py")})
    files = [parsed for path in paths if (parsed := parse_test_file(path, root, matcher_packages))]
    return render_page(files, collect_matchers(files, root), git_info(root, test_root))


def repo_root(test_root: Path) -> Path:
    """The git work tree containing the tests, or the directory above them when they aren't in git."""
    top = git(test_root.resolve(), "rev-parse", "--show-toplevel")
    return Path(top).resolve() if top else test_root.resolve().parent


def parse_test_file(path: Path, root: Path, matcher_packages: tuple[str, ...]) -> TestFile | None:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Skipping {path}: {e}", file=sys.stderr)  # noqa: T201
        return None
    relative = path.resolve().relative_to(root)
    matchers = asserted_matchers(tree, ".".join(relative.with_suffix("").parts)) | imported_matchers(
        tree, matcher_packages
    )
    tests = [parse_test_case(node, source, matchers) for node in test_functions(tree)]
    return TestFile(relative, tests, matchers) if tests else None


def imports(tree: ast.Module) -> dict[str, str]:
    """Map names brought in with `from x import y` to their source module."""
    return {
        alias.asname or alias.name: node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
        for alias in node.names
        if alias.name != "assert_that"
    }


def imported_matchers(tree: ast.Module, matcher_packages: tuple[str, ...]) -> dict[str, str]:
    """Names imported from a known matcher package, or from any module with "matcher" in its name."""
    return {
        name: module
        for name, module in imports(tree).items()
        if module.split(".")[0] in matcher_packages or "matcher" in module.lower()
    }


def asserted_matchers(tree: ast.Module, own_module: str) -> dict[str, str]:
    """Anything called as the second argument to `assert_that` is a matcher, wherever it's defined.

    This picks up a project's own matchers, from a helper module or defined in the test file itself.
    """
    imported = imports(tree)
    roots = (chain_root(call.args[1]) for call in ast.walk(tree) if is_assert_that(call) and len(call.args) > 1)
    return {name: imported.get(name, own_module) for name in roots if name}


def chain_root(node: ast.AST) -> str | None:
    """The function name at the start of a matcher call chain: `is_rss_feed().with_title(x)` -> `is_rss_feed`."""
    while isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        node = node.func.value
    return node.func.id if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) else None


def test_functions(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    functions = (ast.FunctionDef, ast.AsyncFunctionDef)
    top_level = [node for node in tree.body if isinstance(node, functions)]
    in_classes = [
        node
        for cls in tree.body
        if isinstance(cls, ast.ClassDef) and cls.name.startswith("Test")
        for node in cls.body
        if isinstance(node, functions)
    ]
    return sorted((f for f in top_level + in_classes if f.name.startswith("test")), key=lambda f: f.lineno)


def parse_test_case(func: ast.FunctionDef | ast.AsyncFunctionDef, source: str, matchers: dict[str, str]) -> TestCase:
    calls = sorted((node for node in ast.walk(func) if is_assert_that(node)), key=lambda node: node.lineno)
    return TestCase(
        name=func.name,
        line=func.lineno,
        doc=ast.get_docstring(func),
        assertions=[parse_assertion(call, source, matchers) for call in calls],
        other_checks=other_checks(func),
    )


def other_checks(func: ast.AST) -> tuple[str, ...]:
    """Describe non-hamcrest checks in a test, so tests without `assert_that` can say what they rely on instead."""
    found = {
        "plain assert" if isinstance(node, ast.Assert) else f"{call_name(node)}()"
        for node in ast.walk(func)
        if isinstance(node, ast.Assert) or call_name(node) in {"raises", "verify", "verifyNoMoreInteractions"}
    }
    return tuple(sorted(found))


def call_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    return func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None


def is_assert_that(node: ast.AST) -> bool:
    return call_name(node) == "assert_that"


def parse_assertion(call: ast.Call, source: str, matchers: dict[str, str]) -> Assertion:
    actual, *rest = call.args or [ast.Constant(None)]
    matcher = rest[0] if rest else None
    names = (n.func.id for n in ast.walk(call) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name))
    return Assertion(
        line=call.lineno,
        source=ast.get_source_segment(source, call) or ast.unparse(call),
        actual=ast.unparse(actual),
        tree=matcher_tree(matcher, matchers) if is_matcher(matcher, matchers) else None,
        matchers=tuple(dict.fromkeys(name for name in names if name in matchers)),
        warning=misuse_warning(matcher, matchers),
    )


def is_matcher(node: ast.AST | None, matchers: dict[str, str]) -> bool:
    """True for a call to an imported matcher, including chained builder calls such as `is_rss_feed().with_title()`."""
    while isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        node = node.func.value
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in matchers


def misuse_warning(matcher: ast.AST | None, matchers: dict[str, str]) -> str | None:
    if matcher is None or is_matcher(matcher, matchers):
        return None
    if isinstance(matcher, ast.Constant) and isinstance(matcher.value, str):
        return None
    return (
        f"Second argument <code>{html.escape(ast.unparse(matcher))}</code> is not a matcher. Hamcrest treats it as "
        "the failure reason and only checks that the actual value is truthy. Did you mean "
        f"<code>equal_to({html.escape(ast.unparse(matcher))})</code>?"
    )


def matcher_tree(node: ast.AST | None, matchers: dict[str, str]) -> MatcherNode:
    """Build a tree from a matcher expression. Chained builder calls become children of the matcher they configure.

    `is_rss_feed().with_entries(has_length(3))` -> `is rss feed` / `with entries has length 3`
    """
    if not isinstance(node, ast.Call):
        return MatcherNode(ast.unparse(node) if node else "")
    if isinstance(node.func, ast.Attribute):
        base = matcher_tree(node.func.value, matchers)
        return replace(base, children=(*base.children, matcher_step(node.func.attr, node, matchers)))
    return matcher_step(ast.unparse(node.func), node, matchers)


def matcher_step(name: str, call: ast.Call, matchers: dict[str, str]) -> MatcherNode:
    args = [(None, arg) for arg in call.args] + [(kw.arg, kw.value) for kw in call.keywords]
    values = tuple(
        f"{key}={ast.unparse(arg)}" if key else ast.unparse(arg) for key, arg in args if not is_matcher(arg, matchers)
    )
    children = tuple(matcher_tree(arg, matchers) for _, arg in args if is_matcher(arg, matchers))
    return collapse(MatcherNode(humanise(name), values, children))


def collapse(node: MatcherNode) -> MatcherNode:
    """Fold a matcher that only wraps one other into a single line, e.g. `not` + `has length 1` -> `not has length 1`."""
    if node.values or len(node.children) != 1:
        return node
    (child,) = node.children
    return MatcherNode(f"{node.label} {child.label}", child.values, child.children)


def humanise(identifier: str) -> str:
    return " ".join(WORDS.get(word, word) for word in identifier.strip("_").split("_"))


def test_title(name: str) -> str:
    words = [ACRONYMS.get(word, word) for word in humanise(re.sub(r"^tests?_?", "", name)).split()]
    title = " ".join(words)
    return title[:1].upper() + title[1:]


def collect_matchers(files: list[TestFile], root: Path) -> list[MatcherInfo]:
    uses = Counter(name for f in files for t in f.tests for a in t.assertions for name in a.matchers)
    modules = {name: module for f in files for name, module in f.matchers.items()}
    search_path = [str(root), *map(str, sorted(root.glob(".venv/lib/python*/site-packages"))), *sys.path]
    return [
        MatcherInfo(name, modules[name], count, matcher_docstring(name, modules[name], search_path))
        for name, count in sorted(uses.items(), key=lambda item: (-item[1], item[0]))
    ]


def matcher_docstring(name: str, module: str, search_path: list[str]) -> str | None:
    """Find a matcher's docstring by parsing its package's source, without importing it."""
    for path in package_sources(module, search_path):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError, UnicodeDecodeError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return ast.get_docstring(node)
    return None


def package_sources(module: str, search_path: list[str]) -> list[Path]:
    top, *_ = module.split(".")
    spec = importlib.machinery.PathFinder.find_spec(top, search_path)
    if spec is None:
        return []
    roots = [Path(p) for p in spec.submodule_search_locations or []] or [Path(spec.origin or "").parent]
    exact = [root.joinpath(*module.split(".")[1:]).with_suffix(".py") for root in roots]
    return [p for p in exact if p.is_file()] + sorted(p for root in roots for p in root.rglob("*.py"))


def git(repo: Path, *args: str) -> str | None:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False)  # noqa: S603, S607
    return result.stdout.strip() if result.returncode == 0 else None


def git_info(repo: Path, test_root: Path) -> GitInfo:
    """Link to the file at the current commit on GitHub or GitLab, otherwise open it locally in VS Code."""
    sha = git(repo, "rev-parse", "HEAD")
    dirty = bool(git(repo, "status", "--porcelain", "--", str(test_root.resolve())))
    remote = web_url(git(repo, "remote", "get-url", "origin") or "")
    blob = "/-/blob/" if "gitlab" in remote else "/blob/"
    if sha and re.match(r"https://(github\.com|gitlab\.com)/", remote):
        return GitInfo(sha, dirty, lambda path, line: f"{remote}{blob}{sha}/{path}#L{line}")
    return GitInfo(sha, dirty, lambda path, line: f"vscode://file/{repo / path}:{line}")


def web_url(remote: str) -> str:
    """Turn a git remote (`git@host:o/r.git`, `ssh://git@host/o/r`, `https://user@host/o/r`) into a web URL."""
    url = re.sub(r"^(?:ssh://)?git@([^:/]+)[:/]", r"https://\1/", remote)
    return re.sub(r"^https://[^@/]+@", "https://", url).removesuffix(".git")


def first_paragraph(doc: str | None) -> str:
    return (doc or "").strip().split("\n\n")[0].replace("\n", " ")


def anchor(path: Path, test: str = "") -> str:
    return "f-" + re.sub(r"[^A-Za-z0-9]+", "-", f"{path}-{test}".rstrip("-"))


def render_page(files: list[TestFile], matchers: list[MatcherInfo], git_state: GitInfo) -> str:
    tests = [t for f in files for t in f.tests]
    assertions = sum(len(t.assertions) for t in tests)
    tiles = (
        render_tile("all", len(tests), "Tests", f"{assertions} assertions"),
        render_tile("warnings", sum(1 for t in tests if has_warning(t)), "Warnings", "misused matchers", warn=True),
        render_tile(
            "unasserted", sum(1 for t in tests if not t.assertions), "No assert_that", "other checks", warn=True
        ),
        render_tile("matchers", len(matchers), "Matchers", "filter by matcher"),
    )
    docs = {m.name: m.doc for m in matchers}
    return PAGE.format(
        generated=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        commit=render_commit(git_state),
        tiles="".join(tiles),
        options="".join(f'<option value="{m.name}">{m.name} ({m.uses})</option>' for m in matchers),
        nav=f'<button type="button" class="file-filter" data-file="" aria-pressed="true">All files'
        f'<span class="count">{len(tests)}</span></button>'
        + "".join(
            f'<button type="button" class="file-filter" data-file="{anchor(f.path)}" aria-pressed="false">'
            f'<span class="dir">{html.escape(f.path.parent.name)}/</span><span class="name">{html.escape(f.path.name)}'
            f'</span><span class="count">{len(f.tests)}</span></button>'
            for f in files
        ),
        files="".join(render_file(f, git_state.linker, docs) for f in files),
        matchers="".join(render_matcher(m) for m in matchers),
    )


def has_warning(test: TestCase) -> bool:
    return any(a.warning for a in test.assertions)


def render_commit(git_state: GitInfo) -> str:
    if not git_state.sha:
        return ""
    dirty = ' <span class="badge" title="Source links may be off by a few lines">uncommitted changes</span>'
    return f" at <code>{git_state.sha[:7]}</code>{dirty if git_state.dirty else ''}"


def render_tile(key: str, value: int, label: str, hint: str, *, warn: bool = False) -> str:
    classes = "stat warn" if warn and value else "stat"
    disabled = "" if value else " disabled"
    return (
        f'<button type="button" class="{classes}" data-status="{key}" aria-pressed="false"{disabled}>'
        f"<b>{value}</b><span>{label}</span><small>{hint}</small></button>"
    )


def rst_to_html(text: str) -> str:
    return re.sub(r"``(.+?)``", r"<code>\1</code>", html.escape(text))


def unasserted_reason(test: TestCase) -> str:
    if not test.other_checks:
        return "No assertions found. This test only fails if something raises."
    checks = ", ".join(f"<code>{html.escape(check)}</code>" for check in test.other_checks)
    return f"No <code>assert_that</code>. Relies on {checks}."


def render_file(test_file: TestFile, linker: Linker, docs: dict[str, str | None]) -> str:
    return (
        f'<section class="file" id="{anchor(test_file.path)}">'
        f'<h2><a href="{html.escape(linker(test_file.path, 1))}">{html.escape(str(test_file.path))}</a></h2>'
        + "".join(render_test(test_file.path, t, linker, docs) for t in test_file.tests)
        + "</section>"
    )


def render_test(path: Path, test: TestCase, linker: Linker, docs: dict[str, str | None]) -> str:
    doc = f'<p class="doc">{html.escape(test.doc)}</p>' if test.doc else ""
    body = (
        '<ol class="assertions">' + "".join(render_assertion(path, a, linker, docs) for a in test.assertions) + "</ol>"
        if test.assertions
        else f'<p class="reason">{unasserted_reason(test)}</p>'
    )
    matchers = " ".join(dict.fromkeys(m for a in test.assertions for m in a.matchers))
    flags = f"{' data-warn' if has_warning(test) else ''}{'' if test.assertions else ' data-unasserted'}"
    return (
        f'<article class="test{"" if test.assertions else " unasserted"}" id="{anchor(path, test.name)}" '
        f'data-file="{anchor(path)}" data-matchers="{matchers}"{flags}>'
        f"<header><h3>{html.escape(test_title(test.name))}</h3>"
        f'<a class="src" href="{html.escape(linker(path, test.line))}">L{test.line} ↗</a></header>{doc}{body}</article>'
    )


def render_assertion(path: Path, assertion: Assertion, linker: Linker, docs: dict[str, str | None]) -> str:
    chips = "".join(
        f'<button type="button" class="chip" data-matcher="{m}" '
        f'title="{html.escape(first_paragraph(docs.get(m)).replace("``", ""))}">{m}</button>'
        for m in assertion.matchers
    )
    warning = f'<p class="warning">{assertion.warning}</p>' if assertion.warning else ""
    tree = assertion.tree or MatcherNode("is truthy")
    return (
        f'<li class="{"has-warning" if assertion.warning else ""}">'
        f'<p class="reading"><code class="subject">{html.escape(assertion.actual)}</code> {render_node_line(tree)}</p>'
        f"{render_children(tree)}{warning}"
        f'<div class="meta">{chips}<a class="src" href="{html.escape(linker(path, assertion.line))}">'
        f"L{assertion.line} ↗</a></div>"
        f"<details><summary>Source</summary><pre><code>{html.escape(assertion.source)}</code></pre></details></li>"
    )


def render_node_line(node: MatcherNode) -> str:
    values = "".join(f' <code class="value">{html.escape(value)}</code>' for value in node.values)
    return f'<span class="words">{html.escape(node.label)}</span>{values}'


def render_children(node: MatcherNode) -> str:
    if not node.children:
        return ""
    return (
        '<ul class="tree">'
        + "".join(f"<li>{render_node_line(child)}{render_children(child)}</li>" for child in node.children)
        + "</ul>"
    )


def render_matcher(matcher: MatcherInfo) -> str:
    doc = rst_to_html(first_paragraph(matcher.doc)) or "<em>No docstring.</em>"
    uses = f"{matcher.uses} use{'s' if matcher.uses != 1 else ''}"
    return (
        f'<div class="matcher" data-info="{matcher.name}" hidden><header><code>{matcher.name}</code>'
        f'<span class="module">{html.escape(matcher.module)}</span><span class="uses">{uses}</span></header>'
        f"<p>{doc}</p></div>"
    )


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Test Assertions</title>
<style>
:root {{
  --bg: #f7f7f5; --surface: #fff; --text: #1d1d1b; --muted: #6b6b66; --border: #e3e2dd;
  --accent: #2f5bd3; --accent-soft: #e8eefc; --code-bg: #ecebe6; --warn: #9a5200; --warn-soft: #fff3e0;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #141413; --surface: #1d1d1b; --text: #ecebe6; --muted: #9b9a93; --border: #33332f;
    --accent: #8aa8ff; --accent-soft: #232c45; --code-bg: #2e2e2a; --warn: #ffb35c; --warn-soft: #3a2a14;
  }}
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--text); font: 15px/1.55 system-ui, sans-serif; }}
code, pre {{ font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 13px; }}
a {{ color: var(--accent); }}
button, select {{ font: inherit; color: inherit; }}
button {{ cursor: pointer; }}
.layout {{ display: grid; grid-template-columns: 280px 1fr; max-width: 1240px; margin: 0 auto; }}
nav {{
  position: sticky; top: 0; height: 100vh; overflow-y: auto; padding: 24px 16px;
  border-right: 1px solid var(--border);
}}
nav h2 {{ margin: 0 0 8px 10px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }}
.file-filter {{
  display: flex; width: 100%; gap: 2px; padding: 6px 10px; border: 0; border-radius: 6px;
  background: none; text-align: left; font-size: 14px;
}}
.file-filter:hover {{ background: var(--accent-soft); }}
.file-filter[aria-pressed="true"] {{ background: var(--accent-soft); color: var(--accent); font-weight: 500; }}
.file-filter.empty {{ opacity: 0.4; }}
.file-filter .dir {{ color: var(--muted); }}
.file-filter .name {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.file-filter .count {{ margin-left: auto; padding-left: 8px; color: var(--muted); font-variant-numeric: tabular-nums; }}
main {{ padding: 32px 32px 80px; min-width: 0; }}
h1 {{ margin: 0 0 4px; font-size: 28px; letter-spacing: -0.02em; }}
.sub {{ color: var(--muted); margin: 0 0 24px; }}
.badge {{
  display: inline-block; padding: 0 8px; border-radius: 99px; background: var(--warn-soft); color: var(--warn);
  font-size: 12px; line-height: 20px; cursor: help;
}}
.stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }}
.stat {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 12px 14px; text-align: left;
}}
.stat:hover:not(:disabled) {{ border-color: var(--accent); }}
.stat b {{ display: block; font-size: 24px; font-variant-numeric: tabular-nums; }}
.stat span {{ font-size: 13px; font-weight: 500; }}
.stat small {{ display: block; color: var(--muted); font-size: 12px; }}
.stat.warn {{ border-color: var(--warn); background: var(--warn-soft); color: var(--warn); }}
.stat.warn small {{ color: var(--warn); opacity: 0.8; }}
.stat[aria-pressed="true"] {{ outline: 2px solid var(--accent); outline-offset: 1px; border-color: var(--accent); }}
.stat:disabled {{ cursor: default; opacity: 0.5; }}
.toolbar {{ position: sticky; top: 0; z-index: 1; background: var(--bg); padding: 8px 0; }}
.controls {{ display: flex; gap: 8px; }}
.controls input, .controls select {{
  padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px; background: var(--surface); color: var(--text);
}}
.controls input {{ flex: 1; min-width: 0; }}
.controls select {{ max-width: 40%; }}
.controls select.active {{ border-color: var(--accent); color: var(--accent); }}
.results {{
  display: flex; gap: 8px; align-items: center; flex-wrap: wrap; min-height: 28px; margin-top: 8px;
  color: var(--muted); font-size: 13px;
}}
.pill {{
  display: inline-flex; gap: 6px; align-items: center; padding: 0 4px 0 10px; border: 0; border-radius: 99px;
  background: var(--accent-soft); color: var(--accent); font-size: 12px; line-height: 22px;
}}
.pill::after {{ content: "\\00d7"; font-size: 14px; width: 16px; }}
.clear {{ border: 0; background: none; color: var(--accent); padding: 0; font-size: 13px; }}
.matcher {{
  background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent);
  border-radius: 8px; padding: 10px 14px; margin-top: 8px;
}}
.matcher header {{ display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }}
.matcher header code {{ font-weight: 600; font-size: 14px; }}
.module {{ color: var(--muted); font-size: 12px; font-family: ui-monospace, monospace; }}
.uses {{ margin-left: auto; color: var(--muted); font-size: 12px; }}
.matcher p {{ margin: 4px 0 0; color: var(--muted); font-size: 14px; }}
.matcher p code {{ font-size: 12px; }}
.empty-state {{ padding: 48px 0; text-align: center; color: var(--muted); }}
.file h2 {{ font-size: 15px; font-family: ui-monospace, monospace; margin: 24px 0 12px; font-weight: 600; }}
.file h2 a {{ color: var(--text); text-decoration: none; }}
.file h2 a:hover {{ color: var(--accent); }}
.test {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 16px 18px; margin-bottom: 12px;
}}
.test.unasserted {{ border-style: dashed; }}
.test header {{ display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }}
.test h3 {{ margin: 0; font-size: 16px; }}
.src {{
  font-family: ui-monospace, monospace; font-size: 12px; color: var(--muted); text-decoration: none; white-space: nowrap;
}}
.src:hover {{ color: var(--accent); }}
.doc {{ color: var(--muted); margin: 4px 0 0; }}
.reason {{ margin: 10px 0 0; color: var(--warn); font-size: 14px; }}
.assertions {{ margin: 12px 0 0; padding-left: 22px; }}
.assertions:has(> li:only-child) {{ list-style: none; padding-left: 0; }}
.assertions > li {{ margin: 10px 0; }}
.reading {{ margin: 0; }}
code.subject, code.value {{ background: var(--code-bg); padding: 1px 6px; border-radius: 4px; }}
.words {{ font-weight: 500; }}
.tree {{ list-style: none; margin: 2px 0 0 4px; padding-left: 16px; border-left: 2px solid var(--border); }}
.tree li {{ margin: 3px 0; }}
.meta {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-top: 6px; }}
.chip {{
  background: var(--accent-soft); color: var(--accent); padding: 0 8px; border-radius: 99px; border: 0;
  font-size: 12px; line-height: 20px; font-family: ui-monospace, monospace;
}}
.chip:hover {{ filter: brightness(1.15); }}
.chip[aria-pressed="true"] {{ background: var(--accent); color: var(--surface); }}
details summary {{ cursor: pointer; color: var(--muted); font-size: 12px; margin-top: 4px; width: fit-content; }}
pre {{ background: var(--code-bg); padding: 12px; border-radius: 8px; overflow-x: auto; margin: 6px 0 0; }}
.warning {{
  margin: 6px 0 0; padding: 8px 12px; background: var(--warn-soft); color: var(--warn);
  border-radius: 6px; font-size: 14px;
}}
button:focus-visible, input:focus-visible, select:focus-visible, a:focus-visible {{
  outline: 2px solid var(--accent); outline-offset: 2px;
}}
[hidden], .hidden {{ display: none !important; }}
@media (max-width: 760px) {{
  .layout {{ grid-template-columns: 1fr; }}
  nav {{
    position: static; height: auto; display: flex; gap: 6px; overflow-x: auto; padding: 12px 16px;
    border-right: 0; border-bottom: 1px solid var(--border);
  }}
  nav h2 {{ display: none; }}
  .file-filter {{ width: auto; flex: none; white-space: nowrap; }}
  main {{ padding: 20px 16px 60px; }}
  .stats {{ grid-template-columns: 1fr 1fr; }}
  .controls {{ flex-direction: column; }}
  .controls select {{ max-width: none; }}
}}
</style>
</head>
<body>
<div class="layout">
<nav aria-label="Filter by file"><h2>Files</h2>{nav}</nav>
<main>
<h1>Test assertions</h1>
<p class="sub">Every hamcrest <code>assert_that</code> in the suite{commit} · generated {generated}</p>
<div class="stats">{tiles}</div>
<div id="results-top"></div>
<div class="toolbar">
  <div class="controls">
    <input type="search" placeholder="Search tests, matchers or code  ( / )" aria-label="Search">
    <select aria-label="Filter by matcher"><option value="">All matchers</option>{options}</select>
  </div>
  <div class="results" aria-live="polite"></div>
  {matchers}
</div>
{files}
<p class="empty-state" hidden>No tests match these filters.</p>
</main>
</div>
<script>
const FACETS = ["status", "file", "matcher", "q"];
const params = new URLSearchParams(location.search);
const state = Object.fromEntries(FACETS.map(key => [key, params.get(key) || ""]));
const input = document.querySelector(".controls input");
const select = document.querySelector(".controls select");
const tests = [...document.querySelectorAll(".test")];
const statusLabels = {{ warnings: "With warnings", unasserted: "Without assert_that" }};
const fileLabel = id => document.querySelector(`.file-filter[data-file="${{id}}"] .name`)?.textContent;

function visible(test) {{
  if (state.status === "warnings" && !("warn" in test.dataset)) return false;
  if (state.status === "unasserted" && !("unasserted" in test.dataset)) return false;
  if (state.file && test.dataset.file !== state.file) return false;
  if (state.matcher && !test.dataset.matchers.split(" ").includes(state.matcher)) return false;
  return !state.q || test.textContent.toLowerCase().includes(state.q.toLowerCase());
}}

function pill(facet, label) {{
  const button = document.createElement("button");
  Object.assign(button, {{ type: "button", className: "pill", textContent: label, title: "Remove filter" }});
  button.dataset.clear = facet;
  return button;
}}

function render() {{
  const shown = tests.filter(test => !test.classList.toggle("hidden", !visible(test))).length;
  document.querySelectorAll(".file").forEach(file => {{
    file.classList.toggle("hidden", !file.querySelector(".test:not(.hidden)"));
  }});
  document.querySelectorAll(".file-filter").forEach(button => {{
    const id = button.dataset.file;
    const count = tests.filter(test => (!id || test.dataset.file === id) && visibleIgnoringFile(test)).length;
    button.querySelector(".count").textContent = count;
    button.classList.toggle("empty", !count);
    button.setAttribute("aria-pressed", id === state.file);
  }});
  document.querySelectorAll("[data-status]").forEach(tile => {{
    tile.setAttribute("aria-pressed", tile.dataset.status === (state.status || "all") && !state.matcher && !state.file);
  }});
  document.querySelectorAll(".chip").forEach(chip => chip.setAttribute("aria-pressed", chip.dataset.matcher === state.matcher));
  document.querySelectorAll("[data-info]").forEach(info => {{ info.hidden = info.dataset.info !== state.matcher; }});
  select.value = state.matcher;
  select.classList.toggle("active", !!state.matcher);

  const results = document.querySelector(".results");
  const pills = [
    state.status && pill("status", statusLabels[state.status]),
    state.file && pill("file", fileLabel(state.file)),
    state.matcher && pill("matcher", state.matcher),
    state.q && pill("q", `“${{state.q}}”`),
  ].filter(Boolean);
  results.replaceChildren(`${{shown}} of ${{tests.length}} tests`, ...pills);
  if (pills.length > 1) {{
    const clear = Object.assign(document.createElement("button"), {{ type: "button", className: "clear", textContent: "Clear all" }});
    clear.dataset.clear = "all";
    results.append(clear);
  }}
  document.querySelector(".empty-state").hidden = shown > 0;
  const query = new URLSearchParams(Object.entries(state).filter(([, value]) => value));
  history.replaceState(null, "", query.size ? `?${{query}}` : location.pathname);
}}

function visibleIgnoringFile(test) {{
  const file = state.file;
  state.file = "";
  const result = visible(test);
  state.file = file;
  return result;
}}

// Change filters without moving what the reader is looking at: keep `keep` at the same screen position if it's
// still shown, otherwise start the results just under the sticky toolbar (only if we were already below it).
function update(changes, keep) {{
  const before = keep?.getBoundingClientRect().top;
  Object.assign(state, changes);
  render();
  if (keep && !keep.classList.contains("hidden")) {{
    window.scrollBy(0, keep.getBoundingClientRect().top - before);
    return;
  }}
  const top = document.getElementById("results-top").getBoundingClientRect().top + window.scrollY;
  if (window.scrollY > top) window.scrollTo(0, top);
}}

document.addEventListener("click", event => {{
  const target = event.target.closest("[data-status], .file-filter, .chip, [data-clear]");
  if (!target) return;
  if ("status" in target.dataset) {{
    const status = target.dataset.status;
    if (status === "matchers") {{ select.focus(); select.showPicker?.(); return; }}
    update(status === "all" ? {{ status: "", file: "", matcher: "", q: "" }} : {{ status: state.status === status ? "" : status }});
    if (status === "all") input.value = "";
  }} else if (target.classList.contains("file-filter")) {{
    update({{ file: state.file === target.dataset.file ? "" : target.dataset.file }});
  }} else if (target.classList.contains("chip")) {{
    update({{ matcher: state.matcher === target.dataset.matcher ? "" : target.dataset.matcher }}, target.closest(".test"));
  }} else {{
    const facet = target.dataset.clear;
    update(facet === "all" ? Object.fromEntries(FACETS.map(key => [key, ""])) : {{ [facet]: "" }});
    if (facet === "all" || facet === "q") input.value = "";
  }}
}});
select.addEventListener("change", () => update({{ matcher: select.value }}));
input.addEventListener("input", () => update({{ q: input.value }}));
document.addEventListener("keydown", event => {{
  if (event.key === "/" && !["INPUT", "SELECT"].includes(document.activeElement.tagName)) {{
    event.preventDefault();
    input.focus();
  }} else if (event.key === "Escape") {{
    input.value = "";
    update(Object.fromEntries(FACETS.map(key => [key, ""])));
  }}
}});
input.value = state.q;
render();
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tests", type=Path, default=Path("tests"), help="Test directory to scan.")
    parser.add_argument("--output", type=Path, default=Path("build/assertion_docs.html"), help="HTML file to write.")
    parser.add_argument(
        "--matcher-package",
        action="append",
        default=[],
        help=f"Extra package whose imports are matchers (repeatable). Always included: {', '.join(MATCHER_PACKAGES)}.",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    page = build_assertion_docs(args.tests, (*MATCHER_PACKAGES, *args.matcher_package))
    args.output.write_text(page, encoding="utf-8")
    print(f"Wrote {args.output}")  # noqa: T201


if __name__ == "__main__":
    main()
