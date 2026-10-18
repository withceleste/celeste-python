"""Rendered catalogs must work during a fresh package import."""

import os
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path


def test_rendered_catalog_imports_during_package_initialization(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    template = (
        root
        / "templates/modalities/{modality_slug}/providers/{provider_slug}/models.py.template"
    ).read_text()
    for placeholder, value in {
        "{Provider}": "XAI",
        "{modality}": "images",
        "{Modality}": "Image",
        "{MODALITY}": "IMAGES",
        "{PROVIDER}": "XAI",
        "{model_id}": "template-catalog-test",
        "{Model Display Name}": "Template Catalog Test",
    }.items():
        template = template.replace(placeholder, value)

    package = tmp_path / "celeste"
    shutil.copytree(
        root / "src/celeste", package, ignore=shutil.ignore_patterns("__pycache__")
    )
    (package / "modalities/images/providers/xai/models.py").write_text(template)

    # Pytest has already imported celeste; use a fresh interpreter with fixed code.
    result = subprocess.run(  # nosec B603
        [
            sys.executable,
            "-c",
            "import celeste; "
            "model = celeste.get_model('template-catalog-test', provider=celeste.Provider.XAI); "
            "assert model.display_name == 'Template Catalog Test'",
        ],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
