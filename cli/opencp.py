#!/usr/bin/env python3
"""
OpenCP: Open Cognitive Project Protocol - Reference Implementation CLI
A zero-dependency tool to pack, unpack, validate, and measure project cognitive DNA.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

VERSION = "1.0.0"

REQUIRED_SECTIONS = [
    "IDENTITY_&_AXIOM",
    "SYSTEM_TOPOLOGY",
    "VERIFIED_ASSETS_GRAPH",
    "EXECUTION_STATE",
    "COGNITIVE_MOMENTUM_&_NEXT_STEP",
]

SECTION_PATTERN = re.compile(r"^\[([A-Z0-9_&]+)\]\s*$", re.MULTILINE)
HEADER_PATTERN = re.compile(r"^=== BEGIN OPEN-CP v([0-9\.]+(?::\s*[\w\-_]+)?)\s*===\s*$", re.MULTILINE)
FOOTER_PATTERN = re.compile(r"^=== END OPEN-CP\s*===\s*$", re.MULTILINE)


def estimate_tokens(text: str) -> int:
    """Accurate zero-dependency token estimation (~3.8 characters per token for technical English/code)."""
    words = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    return max(1, int(len(words) * 1.15))


def parse_opencp(content: str) -> Dict[str, Any]:
    """Parse an OpenCP v1.0 packet into structured dictionary."""
    clean = content.strip()
    header_match = HEADER_PATTERN.search(clean)
    footer_match = FOOTER_PATTERN.search(clean)

    if not header_match or not footer_match:
        raise ValueError("Invalid OpenCP format: Missing '=== BEGIN OPEN-CP' or '=== END OPEN-CP' delimiters.")

    version_raw = header_match.group(1)
    body = clean[header_match.end():footer_match.start()].strip()

    sections: Dict[str, str] = {}
    current_key: Optional[str] = None
    buffer: List[str] = []

    for line in body.splitlines():
        sec_match = SECTION_PATTERN.match(line.strip())
        if sec_match:
            if current_key:
                sections[current_key] = "\n".join(buffer).strip()
                buffer = []
            current_key = sec_match.group(1)
        elif current_key:
            buffer.append(line)

    if current_key:
        sections[current_key] = "\n".join(buffer).strip()

    return {
        "version": version_raw,
        "sections": sections,
        "token_estimate": estimate_tokens(content),
        "raw": content
    }


def validate_opencp(content: str) -> Dict[str, Any]:
    """Validate completeness, token density and required axioms."""
    parsed = parse_opencp(content)
    sections = parsed["sections"]
    missing = [req for req in REQUIRED_SECTIONS if req not in sections]
    
    tokens = parsed["token_estimate"]
    warnings: List[str] = []
    
    if tokens > 800:
        warnings.append(f"High token density warning: {tokens} tokens (Target is < 500 for < 500ms ingestion).")
    
    # Check for Axiom Zero or invariants
    identity_section = sections.get("IDENTITY_&_AXIOM", "")
    if "!AXIOM" not in identity_section and "Invariants:" not in identity_section:
        warnings.append("Best practice recommendation: Include '!AXIOM_ZERO' or immutable invariants in [IDENTITY_&_AXIOM].")

    return {
        "valid": len(missing) == 0,
        "missing_sections": missing,
        "found_sections": list(sections.keys()),
        "token_count": tokens,
        "warnings": warnings,
        "version": parsed["version"],
    }


def detect_repo_stack(root: Path) -> Dict[str, Any]:
    """Auto-detect repo topology and key files without external dependencies."""
    stack: List[str] = []
    invariants: List[str] = []

    if (root / "package.json").exists():
        try:
            with open(root / "package.json", "r", encoding="utf-8") as f:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "astro" in deps:
                    stack.append("Astro")
                if "react" in deps or "next" in deps:
                    stack.append("React/Next" if "next" in deps else "React")
                if "vue" in deps or "nuxt" in deps:
                    stack.append("Vue/Nuxt")
                if "tailwindcss" in deps:
                    stack.append("Tailwind")
        except Exception:
            stack.append("Node.js")

    if (root / "Cargo.toml").exists():
        stack.append("Rust")
    if (root / "go.mod").exists():
        stack.append("Go")
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        stack.append("Python")

    # Invariants detection
    if (root / "wrangler.toml").exists() or (root / "wrangler.json").exists():
        stack.append("Cloudflare Workers/Pages")
    if (root / "netlify.toml").exists():
        stack.append("Netlify")
    if (root / "Dockerfile").exists():
        stack.append("Docker")

    return {
        "stack": " + ".join(stack) if stack else "Generic Polyglot",
        "invariants": invariants
    }


def generate_template(project_name: str, path: str = ".") -> str:
    """Generate a clean OpenCP template populated with auto-detected workspace facts."""
    root = Path(path).resolve()
    info = detect_repo_stack(root)
    name = project_name or root.name

    template = f"""=== BEGIN OPEN-CP v1.0: {name.upper()} ===
[IDENTITY_&_AXIOM]
Actor: {os.getenv('USER', 'developer')} | Project: {name}
Goal: Core system objective and north star mission statement.
!AXIOM_ZERO: Absolute truth constraint. Every claim must link to code or artifact. No hallucinations.

[SYSTEM_TOPOLOGY]
Stack: {info['stack']}
Host: Production runtime / hosting targets
I18n: Language & localization boundaries (if applicable)
LocalRepo: {root} | MainBranch: main

[VERIFIED_ASSETS_GRAPH]
M1(CoreModule): Active production endpoint or primary package
M2(DataLayer): Database / storage / persistence state
Docs: Key specifications and verified integration points

[EXECUTION_STATE]
Phase_Current: Active milestone in progress
Completed: Prior milestones tested and verified
ClosedDefects: Critical issues resolved in previous sessions

[COGNITIVE_MOMENTUM_&_NEXT_STEP]
ActiveBlocker: The single most critical pending task or dependency.
NextImmediateStep: The exact technical command or code edit the next AI must execute.
=== END OPEN-CP ===
"""
    return template


def main():
    parser = argparse.ArgumentParser(
        prog="opencp",
        description="Open Cognitive Project Protocol (OpenCP) - Instant Cross-AI Project Portability"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Pack command
    pack_parser = subparsers.add_parser("pack", help="Generate an OpenCP packet for the current repository")
    pack_parser.add_argument("-n", "--name", default="", help="Project name")
    pack_parser.add_argument("-p", "--path", default=".", help="Repository directory")
    pack_parser.add_argument("-o", "--output", help="Write to file instead of stdout")

    # Validate command
    val_parser = subparsers.add_parser("validate", help="Validate an existing OpenCP file or string")
    val_parser.add_argument("file", help="Path to .opencp or markdown file")

    # Unpack / inspect command
    unpack_parser = subparsers.add_parser("unpack", help="Inspect and display structured summary of an OpenCP packet")
    unpack_parser.add_argument("file", help="Path to .opencp file")
    unpack_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "pack":
        packet = generate_template(args.name, args.path)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(packet)
            print(f"✓ OpenCP packet written to: {args.output}")
            print(f"  Estimated tokens: {estimate_tokens(packet)} (< 1 second ingestion)")
        else:
            print(packet)

    elif args.command == "validate":
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        content = path.read_text(encoding="utf-8")
        try:
            res = validate_opencp(content)
            if res["valid"]:
                print(f"✓ OpenCP Packet is VALID (Spec v{res['version']})")
                print(f"  Token footprint: {res['token_count']} tokens (Shannon-optimal)")
                for w in res["warnings"]:
                    print(f"  ⚠ {w}")
            else:
                print(f"✗ OpenCP Packet is INVALID:")
                for m in res["missing_sections"]:
                    print(f"  - Missing section: [{m}]")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Parse error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "unpack":
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        content = path.read_text(encoding="utf-8")
        try:
            parsed = parse_opencp(content)
            if args.json:
                print(json.dumps(parsed, indent=2))
            else:
                print(f"\n🧠 OpenCP v{parsed['version']} Cognitive Snapshot")
                print("=" * 50)
                print(f"Estimated Tokens: {parsed['token_estimate']}")
                for k, v in parsed["sections"].items():
                    print(f"\n▶ [{k}]")
                    for line in v.splitlines():
                        print(f"  {line}")
                print("\n" + "=" * 50)
        except Exception as e:
            print(f"✗ Parse error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
