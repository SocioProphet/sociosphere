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
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
