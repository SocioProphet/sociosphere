"""engines/ontology_engine.py

Semantic extraction engine for the SocioProphet registry.

Reads registry/canonical-repos.yaml and registry/repository-ontology.yaml,
then exposes methods to query role taxonomies, tag relationships, and
dependency semantics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


_REGISTRY_DIR = Path(__file__).parent.parent / "registry"


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class OntologyEngine:
    """Load and query the repository ontology."""

    def __init__(self, registry_dir: str | Path | None = None) -> None:
        self._dir = Path(registry_dir) if registry_dir else _REGISTRY_DIR
        self._repos: dict[str, dict[str, Any]] = {}
        self._ontology: dict[str, Any] = {}
        self._loaded = False

    # ── I/O ──────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load all registry YAML files into memory."""
        repos_raw = _load_yaml(self._dir / "canonical-repos.yaml")
        for repo in repos_raw.get("repositories", []):
            self._repos[repo["id"]] = repo

        self._ontology = _load_yaml(self._dir / "repository-ontology.yaml")
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    # ── Repo queries ──────────────────────────────────────────────────────────

    def get_repo(self, repo_id: str) -> dict[str, Any] | None:
        """Return a single repository record by id."""
        self._ensure_loaded()
        return self._repos.get(repo_id)

    def all_repos(self) -> list[dict[str, Any]]:
        """Return all repository records."""
        self._ensure_loaded()
        return list(self._repos.values())

    def repos_by_role(self, role: str) -> list[dict[str, Any]]:
        """Return all repositories with the given role."""
        self._ensure_loaded()
        return [r for r in self._repos.values() if r.get("role") == role]

    def repos_by_status(self, status: str) -> list[dict[str, Any]]:
        """Return all repositories with the given status."""
        self._ensure_loaded()
        return [r for r in self._repos.values() if r.get("status") == status]

    def repos_by_tag(self, tag: str) -> list[dict[str, Any]]:
        """Return all repositories that carry the given tag."""
        self._ensure_loaded()
        return [r for r in self._repos.values() if tag in (r.get("tags") or [])]

    def repos_by_language(self, language: str) -> list[dict[str, Any]]:
        """Return all repositories whose primary_language matches."""
        self._ensure_loaded()
        return [
            r for r in self._repos.values()
            if r.get("primary_language") == language
        ]

    # ── Ontology queries ──────────────────────────────────────────────────────

    def get_role_definition(self, role: str) -> dict[str, Any] | None:
        """Return the ontology definition for a role."""
        self._ensure_loaded()
        return self._ontology.get("roles", {}).get(role)

    def all_roles(self) -> list[str]:
        """Return all defined role names."""
        self._ensure_loaded()
        return list(self._ontology.get("roles", {}).keys())

    def get_relationship_definition(self, rel: str) -> dict[str, Any] | None:
        """Return the ontology definition for a relationship type."""
        self._ensure_loaded()
        return self._ontology.get("relationships", {}).get(rel)

    def all_relationships(self) -> list[str]:
        """Return all defined relationship names."""
        self._ensure_loaded()
        return list(self._ontology.get("relationships", {}).keys())

    # ── Extraction helpers ────────────────────────────────────────────────────

    def extract_tag_cloud(self) -> dict[str, int]:
        """Count how many repos carry each tag across the entire registry."""
        self._ensure_loaded()
        counts: dict[str, int] = {}
        for repo in self._repos.values():
            for tag in repo.get("tags") or []:
                counts[tag] = counts.get(tag, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))

    def extract_role_summary(self) -> dict[str, int]:
        """Count how many repos exist per role."""
        self._ensure_loaded()
        summary: dict[str, int] = {}
        for repo in self._repos.values():
            role = repo.get("role", "unknown")
            summary[role] = summary.get(role, 0) + 1
        return dict(sorted(summary.items(), key=lambda kv: kv[1], reverse=True))

    def extract_language_summary(self) -> dict[str, int]:
        """Count how many repos use each primary language."""
        self._ensure_loaded()
        summary: dict[str, int] = {}
        for repo in self._repos.values():
            lang = repo.get("primary_language") or "unknown"
            summary[lang] = summary.get(lang, 0) + 1
        return dict(sorted(summary.items(), key=lambda kv: kv[1], reverse=True))

    def validate_repos_against_ontology(self) -> list[str]:
        """
        Check that every repo's role exists in the ontology.

        Returns a list of warning strings (empty means no issues).
        """
        self._ensure_loaded()
        known_roles = set(self._ontology.get("roles", {}).keys())
        warnings: list[str] = []
        for repo_id, repo in self._repos.items():
            role = repo.get("role")
            if role and role not in known_roles:
                warnings.append(
                    f"repo '{repo_id}' has unknown role '{role}'"
                )
        return warnings
#!/usr/bin/env python3
"""
engines/ontology_engine.py

Scan each repository, extract controlled vocabulary, build topic models,
and update registry/repository-ontology.yaml.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
"""ontology_engine.py — OntologyEngine for the SocioProphet workspace registry.

Queries canonical-repos.yaml and repository-ontology.yaml to answer:
  - Which repos have a given role / tag / layer?
  - Which repos govern / depend on a given repo?
  - What is the full ontological description of a repo?

Stdlib + PyYAML only.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
ONTOLOGY_FILE = REGISTRY_DIR / "repository-ontology.yaml"
CANONICAL_REPOS_FILE = REGISTRY_DIR / "canonical-repos.yaml"

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
                pass
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
    """
    Lightweight topic extraction using term co-occurrence clusters.

    This is a deterministic approximation of LSA/LDA that runs without any
    external ML dependencies.  For a production deployment, replace with
    scikit-learn TruncatedSVD or gensim LDA.
    """
    text = _read_text_files(
        repo_path,
        (".py", ".go", ".ts", ".md", ".yaml"),
    )
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
    vocab = extract_vocabulary(repo_path)
    topics = extract_topics(repo_path)
    return {
        "controlled_vocabulary": vocab,
        "lsa_topics": topics,
    }


def load_ontology() -> dict[str, Any]:
    """Load the current repository-ontology.yaml."""
    if not ONTOLOGY_FILE.exists():
        return {"ontologies": {}}
    raw = ONTOLOGY_FILE.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(raw) or {"ontologies": {}}
    # Minimal fallback: return skeleton if PyYAML unavailable.
    return {"ontologies": {}}


def save_ontology(data: dict[str, Any]) -> None:
    """Persist ontology data back to registry/repository-ontology.yaml."""
    if yaml is None:
        print("WARN: PyYAML not installed — skipping ontology write", file=sys.stderr)
        return
    ONTOLOGY_FILE.write_text(
        yaml.dump(data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def run(repo_names: list[str] | None = None) -> int:
    """
    Main entry point.  If repo_names is None, analyse every repo path that
    exists as a sub-directory of ROOT.
    """
    ontology = load_ontology()
    ontologies: dict[str, Any] = ontology.get("ontologies", {})

    candidates: list[Path]
    if repo_names:
        candidates = [ROOT / name for name in repo_names]
    else:
        # Look for any directory that looks like a repo (has a README or src/
        # subdirectory).
        candidates = [
            p
            for p in ROOT.iterdir()
            if p.is_dir()
            and not p.name.startswith(".")
            and (p / "README.md").exists()
        ]

    updated = 0
    for repo_path in candidates:
        if not repo_path.exists():
            print(f"SKIP: {repo_path.name} — directory not found", file=sys.stderr)
            continue
        print(f"Analysing {repo_path.name} …")
        result = analyze_repo(repo_path)
        existing = ontologies.get(repo_path.name, {})
        # Merge: preserve hand-written semantic_bindings and top_topics if present.
        merged: dict[str, Any] = {**existing}
        if result["controlled_vocabulary"]:
            merged["controlled_vocabulary"] = result["controlled_vocabulary"]
        if result["lsa_topics"]:
            merged["lsa_topics"] = result["lsa_topics"]
        ontologies[repo_path.name] = merged
        updated += 1

    ontology["ontologies"] = ontologies
    save_ontology(ontology)
    print(f"OK: updated {updated} ontolog{'y' if updated == 1 else 'ies'}")
    import yaml
except ImportError:
    print("ERROR: PyYAML required (pip install pyyaml)", file=sys.stderr)
    raise

REGISTRY_DIR = Path(__file__).resolve().parents[1] / "registry"


def _load(filename: str) -> Any:
    return yaml.safe_load((REGISTRY_DIR / filename).read_text("utf-8"))


class OntologyEngine:
    """Role/tag/layer query engine for the canonical-repos registry."""

    def __init__(self) -> None:
        data = _load("canonical-repos.yaml")
        self._repos: list[dict] = data.get("repos", [])
        ont = _load("repository-ontology.yaml")
        self._roles: dict[str, dict] = {r["id"]: r for r in ont.get("roles", [])}
        self._layers: dict[str, dict] = {la["id"]: la for la in ont.get("layers", [])}
        self._bindings: list[dict] = ont.get("semantic_bindings", [])
        # Index repos by name
        self._by_name: dict[str, dict] = {r["name"]: r for r in self._repos}

    # ── Repo queries ──────────────────────────────────────────────────────────

    def all_repos(self) -> list[dict]:
        return list(self._repos)

    def repo(self, name: str) -> dict | None:
        return self._by_name.get(name)

    def repos_by_layer(self, layer: str) -> list[dict]:
        return [r for r in self._repos if r.get("layer") == layer]

    def repos_by_role(self, role: str) -> list[dict]:
        return [r for r in self._repos if r.get("role") == role]

    def repos_by_tag(self, tag: str) -> list[dict]:
        return [r for r in self._repos if tag in r.get("tags", [])]

    def repos_by_priority(self, priority: str) -> list[dict]:
        return [r for r in self._repos if r.get("priority") == priority]

    def repos_with_open_prs(self) -> list[dict]:
        return [r for r in self._repos if r.get("open_prs", 0) > 0]

    def dedup_candidates(self) -> list[dict]:
        return [r for r in self._repos if r.get("dedup_candidate")]

    def single_branch_exempt(self) -> list[dict]:
        return [r for r in self._repos if r.get("single_branch_exempt")]

    # ── Relationship queries ──────────────────────────────────────────────────

    def dependents_of(self, name: str) -> list[str]:
        """Return repos that declare a depends_on edge to `name`."""
        return [
            b["subject"]
            for b in self._bindings
            if b.get("predicate") == "depends_on" and b.get("object") == name
        ]

    def dependencies_of(self, name: str) -> list[str]:
        """Return repos that `name` depends on."""
        return [
            b["object"]
            for b in self._bindings
            if b.get("predicate") == "depends_on" and b.get("subject") == name
        ]

    def governed_by(self, name: str) -> list[str]:
        """Return standards repos that govern `name`."""
        return [
            b["object"]
            for b in self._bindings
            if b.get("predicate") == "governed_by" and b.get("subject") == name
        ]

    def governs(self, name: str) -> list[str]:
        """Return repos governed by `name`."""
        return [
            b["subject"]
            for b in self._bindings
            if b.get("predicate") == "governed_by" and b.get("object") == name
        ]

    # ── Validation ────────────────────────────────────────────────────────────

    def validate_all_roles(self) -> list[str]:
        """Validate every repo role is declared in the ontology."""
        known = set(self._roles.keys())
        errors: list[str] = []
        for r in self._repos:
            role = r.get("role", "")
            if role and role not in known:
                errors.append(f"{r['name']}: unknown role '{role}'")
        return errors

    def validate_all_layers(self) -> list[str]:
        """Validate every repo layer is declared in the ontology."""
        known = set(self._layers.keys())
        errors: list[str] = []
        for r in self._repos:
            layer = r.get("layer", "")
            if layer and layer not in known:
                errors.append(f"{r['name']}: unknown layer '{layer}'")
        return errors

    # ── Summary ───────────────────────────────────────────────────────────────

    def summary(self) -> dict:
        layers: dict[str, int] = {}
        roles: dict[str, int] = {}
        priorities: dict[str, int] = {}
        statuses: dict[str, int] = {}
        total_open_prs = 0
        for r in self._repos:
            layers[r.get("layer", "unknown")] = layers.get(r.get("layer", "unknown"), 0) + 1
            roles[r.get("role", "unknown")] = roles.get(r.get("role", "unknown"), 0) + 1
            priorities[r.get("priority", "unknown")] = priorities.get(r.get("priority", "unknown"), 0) + 1
            statuses[r.get("status", "unknown")] = statuses.get(r.get("status", "unknown"), 0) + 1
            total_open_prs += r.get("open_prs", 0)
        return {
            "total_repos": len(self._repos),
            "total_open_prs": total_open_prs,
            "by_layer": layers,
            "by_role": roles,
            "by_priority": priorities,
            "by_status": statuses,
            "dedup_candidates": len(self.dedup_candidates()),
        }


def main() -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="OntologyEngine CLI")
    p.add_argument("cmd", choices=["summary", "validate", "list", "repo", "layer", "role", "tag"])
    p.add_argument("--arg", default=None, help="Argument for repo/layer/role/tag queries")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()

    engine = OntologyEngine()

    if args.cmd == "summary":
        result = engine.summary()
    elif args.cmd == "validate":
        role_errors = engine.validate_all_roles()
        layer_errors = engine.validate_all_layers()
        result = {"role_errors": role_errors, "layer_errors": layer_errors, "ok": not (role_errors or layer_errors)}
        if result["ok"]:
            print("OK: all roles and layers valid")
        else:
            for e in role_errors + layer_errors:
                print(f"ERROR: {e}", file=sys.stderr)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    elif args.cmd == "list":
        result = [{"name": r["name"], "layer": r.get("layer"), "role": r.get("role"), "status": r.get("status"), "open_prs": r.get("open_prs", 0)} for r in engine.all_repos()]
    elif args.cmd == "repo":
        if not args.arg:
            print("ERROR: --arg <repo-name> required", file=sys.stderr)
            return 2
        result = engine.repo(args.arg)
        if result is None:
            print(f"ERROR: repo '{args.arg}' not found", file=sys.stderr)
            return 1
    elif args.cmd == "layer":
        if not args.arg:
            print("ERROR: --arg <layer> required", file=sys.stderr)
            return 2
        result = [r["name"] for r in engine.repos_by_layer(args.arg)]
    elif args.cmd == "role":
        if not args.arg:
            print("ERROR: --arg <role> required", file=sys.stderr)
            return 2
        result = [r["name"] for r in engine.repos_by_role(args.arg)]
    elif args.cmd == "tag":
        if not args.arg:
            print("ERROR: --arg <tag> required", file=sys.stderr)
            return 2
        result = [r["name"] for r in engine.repos_by_tag(args.arg)]
    else:
        return 2

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if isinstance(result, dict):
            for k, v in result.items():
                print(f"  {k}: {v}")
        elif isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    print(f"  {item.get('name', item)}")
                else:
                    print(f"  {item}")
        else:
            print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
