#!/usr/bin/env python3
"""Validate every stack template against the rules in core/writing-agent-files.md.

Usage: python3 tools/check_templates.py [repo-root]
Exit 1 on any error. Warnings are printed but do not fail the run.
"""
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
STACKS_DIR = os.path.join(ROOT, "stacks")

TARGET_LINES = 150
HARD_LINES = 200
CHAIN_BYTES = 32 * 1024
WINDSURF_CHARS = 6000
MAX_LINKS = 12

REQUIRED_SECTIONS = ["Commands", "Architecture", "Testing", "Observability", "Boundaries", "Where to look"]
REQUIRED_BOUNDARY_WORDS = ["Always", "Ask first", "Never"]
REQUIRED_DOCS = ["architecture.md", "testing.md", "observability.md", "gates.md"]

PLATITUDES = [
    "write clean code", "clean code", "best practices", "be helpful", "high quality", "high-quality",
    "follow good", "be careful", "make sure to", "as needed", "appropriately", "properly", "robust",
    "well-structured", "maintainable code", "you are a senior", "you are an expert",
]
STYLE_LEAK = [
    r"\bindent", r"\btabs?\b", r"\bsemicolons?\b", r"trailing comma", r"line length", r"\bcamelCase\b",
    r"\bsnake_case\b(?!\s*\()", r"\bPascalCase\b", r"\bbraces?\b", r"spaces? around",
]
STYLE_LEAK_ALLOW = ["linter", "formatter", "lint", "format", "detekt", "swiftlint", "ruff", "biome", "eslint",
                    "ktlint", "clippy", "gofmt", "dart format", "analysis_options", ".editorconfig", "event", "catalogue"]
IMPERATIVE = re.compile(r"^\s*[-*]\s+(\*\*)?(Always|Never|Use|Run|Prefer|Do not|Don't|Avoid|Put|Keep|Add|Write|Emit)\b", re.I)
CONCRETE = re.compile(r"`[^`]+`|\]\(|https?://|\d")

errors = []
warnings = []


def err(path, msg):
    errors.append(f"{os.path.relpath(path, ROOT)}: {msg}")


def warn(path, msg):
    warnings.append(f"{os.path.relpath(path, ROOT)}: {msg}")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def check_agents_md(stack_dir):
    path = os.path.join(stack_dir, "AGENTS.md")
    if not os.path.isfile(path):
        err(stack_dir, "AGENTS.md missing")
        return
    text = read(path)
    lines = text.splitlines()
    n = len(lines)
    if n > HARD_LINES:
        err(path, f"{n} lines, over the hard limit of {HARD_LINES}")
    elif n > TARGET_LINES:
        warn(path, f"{n} lines, over the {TARGET_LINES}-line target")
    if len(text) > WINDSURF_CHARS:
        warn(path, f"{len(text)} chars, over the Windsurf per-file cap of {WINDSURF_CHARS}")

    # chain size: root plus every local doc it links
    chain = len(text.encode("utf-8"))
    for m in re.finditer(r"\]\(([^)]+)\)|`(agent_docs/[^`]+)`", text):
        rel = m.group(1) or m.group(2)
        if rel.startswith("http") or rel.startswith("#"):
            continue
        target = os.path.join(stack_dir, rel.split("#")[0])
        if os.path.isfile(target):
            chain += os.path.getsize(target)
    if chain > CHAIN_BYTES:
        err(path, f"root plus linked docs = {chain} bytes, over {CHAIN_BYTES}")

    headings = [re.sub(r"^#+\s*", "", line).strip() for line in lines if line.startswith("#")]
    for sec in REQUIRED_SECTIONS:
        if not any(h.lower().startswith(sec.lower()) for h in headings):
            err(path, f"missing section '{sec}'")
    for word in REQUIRED_BOUNDARY_WORDS:
        if word not in text:
            err(path, f"boundaries must contain '{word}'")

    links = len(re.findall(r"\]\([^)]+\)", text)) + len(re.findall(r"`agent_docs/[^`]+`", text))
    if links > MAX_LINKS:
        warn(path, f"{links} links out of the root, target is at most {MAX_LINKS}")

    if "CONSTITUTION.md" not in text:
        err(path, "must reference CONSTITUTION.md")
    if re.search(r"\bTODO\b|\bTBD\b|\bFIXME\b", text):
        err(path, "contains TODO/TBD/FIXME")

    low = text.lower()
    for p in PLATITUDES:
        if p in low:
            err(path, f"platitude '{p}' - replace with a concrete, checkable instruction or delete")

    for i, line in enumerate(lines, 1):
        l = line.lower()
        if any(re.search(rx, line, re.I) for rx in STYLE_LEAK) and not any(a in l for a in STYLE_LEAK_ALLOW):
            err(path, f"line {i}: style rule in the agent file; move it to the linter or formatter config")
        if IMPERATIVE.search(line) and not CONCRETE.search(line):
            warn(path, f"line {i}: directive names nothing concrete (no path, command, link or number): {line.strip()[:80]}")
        if re.match(r"^\s*[-*]\s+(\*\*)?Never\b", line, re.I) and not CONCRETE.search(line):
            err(path, f"line {i}: a Never without the alternative (path, command or link)")
        if "—" in line or "–" in line or "→" in line:
            err(path, f"line {i}: em/en dash or arrow; use '-' and '=>'")


def check_companions(stack_dir):
    claude = os.path.join(stack_dir, "CLAUDE.md")
    if not os.path.isfile(claude):
        err(stack_dir, "CLAUDE.md missing (should be '@AGENTS.md')")
    elif read(claude).strip() != "@AGENTS.md":
        err(claude, "must contain exactly '@AGENTS.md'")
    copilot = os.path.join(stack_dir, ".github", "copilot-instructions.md")
    if not os.path.isfile(copilot):
        err(stack_dir, ".github/copilot-instructions.md missing")
    elif "AGENTS.md" not in read(copilot):
        err(copilot, "must point at AGENTS.md")
    for d in REQUIRED_DOCS:
        p = os.path.join(stack_dir, "agent_docs", d)
        if not os.path.isfile(p):
            err(stack_dir, f"agent_docs/{d} missing")
        elif len(read(p)) > CHAIN_BYTES:
            err(p, f"over {CHAIN_BYTES} bytes")
    readme = os.path.join(stack_dir, "README.md")
    if not os.path.isfile(readme):
        warn(stack_dir, "README.md missing (adoption notes)")


def main():
    if not os.path.isdir(STACKS_DIR):
        print("no stacks/ directory yet - nothing to check")
        return 0
    stacks = sorted(d for d in os.listdir(STACKS_DIR) if os.path.isdir(os.path.join(STACKS_DIR, d)))
    for s in stacks:
        d = os.path.join(STACKS_DIR, s)
        check_agents_md(d)
        check_companions(d)
    const = os.path.join(ROOT, "CONSTITUTION.md")
    if not os.path.isfile(const):
        errors.append("CONSTITUTION.md missing at repo root")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"checked {len(stacks)} stack(s): {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
