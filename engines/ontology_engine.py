"""Ontology engine for registry queries and lightweight semantic extraction."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

_REGISTRY_DIR = Path(__file__).resolve().parents[1] / "registry"


# Common English stop-words to exclude from vocabulary extraction.
_STOP_WORDS = frozenset(
    [
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "should", "could", "may", "might", "can", "not", "no", "nor", "so",
        "yet", "both", "either", "neither", "each", "few", "more", "most",
        "other", "some", "such", "than", "then", "that", "this", "these",
        "those", "it", "its", "they", "their", "there", "here", "where",
        "when", "which", "who", "what", "how", "all", "any", "if", "into",
        "as", "up", "out", "about", "after", "before", "between", "through",
        "during", "until", "while", "although", "because", "since", "unless",
    ]
)


def _tokenise(text: str) -> list[str]:
    """Split text into lowercase tokens, stripping punctuation."""
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]*", text)
    return [t.lower() for t in tokens if len(t) > 2 and t.lower() not in _STOP_WORDS]


def _read_text_files(repo_path: Path, extensions: tuple[str, ...]) -> str:
    """Read all files with the given extensions under repo_path."""
    parts: list[str] = []
    for ext in extensions:
        for p in repo_path.rglob(f"*{ext}"):
            if ".git" in p.parts:
                continue
            try:
                parts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
    return "\n".join(parts)


def extract_vocabulary(repo_path: Path, top_n: int = 20) -> list[str]:
    """Return the top N domain terms found in a repository's text files."""
    text = _read_text_files(
        repo_path,
        (".py", ".go", ".ts", ".js", ".md", ".yaml", ".yml", ".json", ".txt", ".ttl"),
    )
    tokens = _tokenise(text)
    counts = Counter(tokens)
    return [term for term, _ in counts.most_common(top_n)]


def extract_topics(repo_path: Path, n_topics: int = 3) -> list[dict[str, Any]]:
    """Deterministic lightweight topic extraction."""
    text = _read_text_files(repo_path, (".py", ".go", ".ts", ".md", ".yaml", ".yml"))
    tokens = _tokenise(text)
    counts = Counter(tokens)
    top_terms = [t for t, _ in counts.most_common(50)]

    topics: list[dict[str, Any]] = []
    chunk = max(1, len(top_terms) // n_topics)
    for i in range(n_topics):
        cluster = top_terms[i * chunk : (i + 1) * chunk][:5]
        if cluster:
            label = "-".join(cluster[:2])
            topics.append({"topic": label, "terms": cluster})
    return topics


def analyze_repo(repo_path: Path) -> dict[str, Any]:
    """Run vocabulary and topic extraction for a single repository path."""
    return {
        "controlled_vocabulary": extract_vocabulary(repo_path),
        "lsa_topics": extract_topics(repo_path),
    }


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for ontology registry operations")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


class OntologyEngine:
    """Load and query the repository ontology."""

    def __init__(self, registry_dir: str | Path | None = None) -> None:
        self._dir = Path(registry_dir) if registry_dir else _REGISTRY_DIR
        self._repos: dict[str, dict[str, Any]] = {}
        self._ontology: dict[str, Any] = {}
        self._loaded = False

    def load(self) -> None:
        repos_raw = _load_yaml(self._dir / "canonical-repos.yaml")
        repos: dict[str, dict[str, Any]] = {}
        for repo in repos_raw.get("repositories", []):
            if not isinstance(repo, dict):
                continue
            repo_id = repo.get("id") or repo.get("name")
            if not repo_id:
                continue
            repos[repo_id] = repo
        self._repos = repos
        self._ontology = _load_yaml(self._dir / "repository-ontology.yaml")
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def get_repo(self, repo_id: str) -> dict[str, Any] | None:
        self._ensure_loaded()
        return self._repos.get(repo_id)

    def all_repos(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return list(self._repos.values())

    def repos_by_role(self, role: str) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return [r for r in self._repos.values() if r.get("role") == role]

    def repos_by_status(self, status: str) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return [r for r in self._repos.values() if r.get("status") == status]

    def repos_by_tag(self, tag: str) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return [r for r in self._repos.values() if tag in (r.get("tags") or [])]

    def repos_by_language(self, language: str) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return [r for r in self._repos.values() if r.get("primary_language") == language]

    def get_role_definition(self, role: str) -> dict[str, Any] | None:
        self._ensure_loaded()
        roles = self._ontology.get("roles", {})
        if isinstance(roles, dict):
            return roles.get(role)
        if isinstance(roles, list):
            for item in roles:
                if not isinstance(item, dict):
                    continue
                rid = item.get("id")
                if rid == role:
                    return item
        return None

    def all_roles(self) -> list[str]:
        self._ensure_loaded()
        roles = self._ontology.get("roles", {})
        if isinstance(roles, dict):
            return list(roles.keys())
        if isinstance(roles, list):
            return [r.get("id") for r in roles if isinstance(r, dict) and r.get("id")]
        return []

    def get_relationship_definition(self, rel: str) -> dict[str, Any] | None:
        self._ensure_loaded()
        rels = self._ontology.get("relationships", {})
        if isinstance(rels, dict):
            return rels.get(rel)
        if isinstance(rels, list):
            for item in rels:
                if not isinstance(item, dict):
                    continue
                rid = item.get("id")
                if rid == rel:
                    return item
        return None

    def all_relationships(self) -> list[str]:
        self._ensure_loaded()
        rels = self._ontology.get("relationships", {})
        if isinstance(rels, dict):
            return list(rels.keys())
        if isinstance(rels, list):
            return [r.get("id") for r in rels if isinstance(r, dict) and r.get("id")]
        return []

    def extract_tag_cloud(self) -> dict[str, int]:
        self._ensure_loaded()
        counts: dict[str, int] = {}
        for repo in self._repos.values():
            for tag in repo.get("tags") or []:
                counts[tag] = counts.get(tag, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))

    def extract_role_summary(self) -> dict[str, int]:
        self._ensure_loaded()
        summary: dict[str, int] = {}
        for repo in self._repos.values():
            role = repo.get("role", "unknown")
            summary[role] = summary.get(role, 0) + 1
        return dict(sorted(summary.items(), key=lambda kv: kv[1], reverse=True))

    def extract_language_summary(self) -> dict[str, int]:
        self._ensure_loaded()
        summary: dict[str, int] = {}
        for repo in self._repos.values():
            lang = repo.get("primary_language") or "unknown"
            summary[lang] = summary.get(lang, 0) + 1
        return dict(sorted(summary.items(), key=lambda kv: kv[1], reverse=True))

    def validate_repos_against_ontology(self) -> list[str]:
        self._ensure_loaded()
        known_roles = set(self.all_roles())
        warnings: list[str] = []
        for repo_id, repo in self._repos.items():
            role = repo.get("role")
            if role and role not in known_roles:
                warnings.append(f"repo '{repo_id}' has unknown role '{role}'")
        return warnings


def run(repo_names: list[str] | None = None) -> int:
    """Analyze local repositories and print extraction summary."""
    root = Path(__file__).resolve().parents[1]
    candidates = [root / name for name in repo_names] if repo_names else [
        p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".") and (p / "README.md").exists()
    ]

    updated = 0
    for repo_path in candidates:
        if not repo_path.exists():
            print(f"SKIP: {repo_path.name} — directory not found", file=sys.stderr)
            continue
        result = analyze_repo(repo_path)
        print(f"Analysed {repo_path.name}: vocab={len(result['controlled_vocabulary'])} topics={len(result['lsa_topics'])}")
        updated += 1

    print(f"OK: updated {updated} ontolog{'y' if updated == 1 else 'ies'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="OntologyEngine CLI")
    parser.add_argument("cmd", choices=["summary", "validate", "list", "repo", "role", "tag", "language", "extract"])
    parser.add_argument("--arg", default=None, help="Argument for repo/role/tag/language queries")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.cmd == "extract":
        repo_names = [args.arg] if args.arg else None
        return run(repo_names)

    engine = OntologyEngine()
    engine.load()

    if args.cmd == "validate":
        warnings = engine.validate_repos_against_ontology()
        ok = not warnings
        if warnings:
            for warning in warnings:
                print(f"ERROR: {warning}", file=sys.stderr)
        else:
            print("OK: all roles and layers valid")
        if args.format == "json":
            print(json.dumps({"ok": ok, "warnings": warnings}, indent=2))
        return 0 if ok else 1

    if args.cmd == "summary":
        result: Any = {
            "total_repos": len(engine.all_repos()),
            "role_summary": engine.extract_role_summary(),
            "language_summary": engine.extract_language_summary(),
            "tag_cloud": engine.extract_tag_cloud(),
        }
    elif args.cmd == "list":
        result = engine.all_repos()
    elif args.cmd == "repo":
        if not args.arg:
            print("ERROR: --arg <repo-id> required", file=sys.stderr)
            return 2
        result = engine.get_repo(args.arg)
        if result is None:
            print(f"ERROR: repo '{args.arg}' not found", file=sys.stderr)
            return 1
    elif args.cmd == "role":
        if not args.arg:
            print("ERROR: --arg <role> required", file=sys.stderr)
            return 2
        result = engine.repos_by_role(args.arg)
    elif args.cmd == "tag":
        if not args.arg:
            print("ERROR: --arg <tag> required", file=sys.stderr)
            return 2
        result = engine.repos_by_tag(args.arg)
    else:  # language
        if not args.arg:
            print("ERROR: --arg <language> required", file=sys.stderr)
            return 2
        result = engine.repos_by_language(args.arg)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if isinstance(result, list):
            for item in result:
                print(item.get("id", item))
        elif isinstance(result, dict):
            for k, v in result.items():
                print(f"{k}: {v}")
        else:
            print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
