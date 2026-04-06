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
