from __future__ import annotations

from pathlib import Path, PurePosixPath


def _canonical_selector(selector: str) -> str:
    if not isinstance(selector, str) or not selector or "/" in selector or "\\" in selector:
        raise ValueError("source selector must be a single canonical Share filename")
    lexical = Path(selector).expanduser()
    if lexical.is_absolute() or lexical.name != selector or lexical.name in {".", ".."}:
        raise ValueError("source selector must be a single canonical Share filename")
    return lexical.name


def _existing_regular_source(selector: str, source_root: Path) -> Path:
    filename = _canonical_selector(selector)
    root = Path(source_root).expanduser().resolve(strict=True)
    candidate = root / filename
    if candidate.is_symlink():
        raise ValueError("symlink source aliases are not permitted")
    resolved = candidate.resolve(strict=True)
    if resolved.parent != root or not resolved.is_file():
        raise ValueError("source selector does not identify a direct regular file in the Share source root")
    return resolved


def resolve_share_source_path(selector: str, source_root: Path) -> Path:
    """Resolve an existing Share raw source path before package identity is available."""
    return _existing_regular_source(selector, source_root)


def resolve_package_bound_share_source(
    selector: str,
    source_root: Path,
    *,
    expected_source: str,
) -> Path:
    """Resolve an existing source and bind it to the package's canonical raw-relative path."""
    if not isinstance(expected_source, str) or not expected_source:
        raise ValueError("package-bound source path is missing or invalid")
    expected = PurePosixPath(expected_source)
    if (
        expected.is_absolute()
        or expected.parts[:3] != ("data", "raw", "分享")
        or len(expected.parts) != 4
        or expected.as_posix() != expected_source
    ):
        raise ValueError("package-bound source path must be data/raw/分享/<filename>")
    filename = _canonical_selector(selector)
    if expected.name != filename:
        raise ValueError("source selector does not match package-bound canonical source path")
    return _existing_regular_source(filename, source_root)
