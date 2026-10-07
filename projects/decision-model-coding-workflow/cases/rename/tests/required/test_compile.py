import importlib.util
import pathlib


def test_every_source_module_compiles():
    package_dir = pathlib.Path(importlib.util.find_spec("document_api").origin).parent
    sources = sorted(package_dir.rglob("*.py"))
    assert sources
    for path in sources:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
