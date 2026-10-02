from pathlib import Path

from backend.file_scanner import FileScanner


def test_scanner_ignores_generated_directories(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "src" / "app.ts").write_text("export const app = true", encoding="utf-8")
    (tmp_path / "node_modules" / "ignored.js").write_text("ignored", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"not source")

    files = FileScanner().scan(tmp_path)

    assert [path.relative_to(tmp_path).as_posix() for path in files] == ["src/app.ts"]


def test_scanner_ignores_boilerplate_files(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "index.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "CODE_OF_CONDUCT.md").write_text("# Code of Conduct", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")

    files = FileScanner().scan(tmp_path)
    assert [path.relative_to(tmp_path).as_posix() for path in files] == ["src/index.py"]
