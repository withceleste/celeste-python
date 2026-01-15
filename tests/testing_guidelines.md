# Python Unit Testing Best Practices

This guide is a practical, drop‑in reference for writing, organizing, and running tests in modern Python projects.

---

## 0) Scope & prerequisites

- **Test runner**: `pytest` 8.x
- **Python**: **≥ 3.12**
- **Layout**: prefer the **`src/` layout** with tests in a top‑level `tests/` directory.
- **Config home**: configure `pytest` via **`pyproject.toml`** under `[tool.pytest.ini_options]` (recommended).

---

## 1) Project layout & discovery

**Recommended structure**
```
pyproject.toml
src/
  yourpkg/
    __init__.py
    core.py
tests/
  test_core.py
  conftest.py
```

**Discovery rules (defaults)**
- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*` (no `__init__`)
- Test functions: `test_*`
- Can be customized with `python_files`, `python_classes`, `python_functions`

**Minimal `pyproject.toml`**
```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = "-ra --strict-markers --strict-config"
markers = [
  "slow: marks tests as slow (deselect with '-m "not slow"')",
  "smoke: quick checks for critical paths",
]
```

> Use `--strict-markers` to catch typos in marker names and `--strict-config` to fail on unknown config keys.

---

## 2) Writing clean, maintainable tests

- Prefer **AAA** (Arrange–Act–Assert) and **expressive names**, e.g. `test_user_cannot_login_with_invalid_password`.
- **Fixtures over xUnit `setUp/tearDown`**: pytest fixtures are explicit, composable, and scoping is clear (`function`, `class`, `module`, `session`).
- Prefer **pure functions** and **dependency injection** to minimize mocking.
- Keep one logical assertion per test; if multiple, make them about the same behavior.

**Handy built‑in fixtures**
- `tmp_path` / `tmp_path_factory`: isolated temporary paths (Pathlib)
- `monkeypatch`: patch environment variables, attributes, or `sys.path`
- `capsys` / `capfd`: capture stdout/stderr
- `caplog`: capture and assert on log records

**Examples**
```python
# tests/test_files.py
def test_writes_report(tmp_path):
    out = tmp_path / "report.txt"
    out.write_text("ok")
    assert out.read_text() == "ok"

# tests/test_env.py
def test_uses_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "fake-key")
    assert load_api_key() == "fake-key"
```

---

## 3) Parametrization

Use `@pytest.mark.parametrize` to cover many cases succinctly.

```python
import pytest
from yourpkg.core import add

@pytest.mark.parametrize("a,b,out", [(1,2,3),(0,0,0),(-1,1,0)])
def test_add(a, b, out):
    assert add(a, b) == out
```

---

## 4) Mocking you can trust

- Use the stdlib `unittest.mock` with **`autospec`** / **`spec_set=True`** to ensure mocks match real call signatures/attributes.
- **Patch where it’s used**, not where it’s defined (patch the import path the SUT references).
- Prefer fakes over mocks when behavior is simple.

```python
from unittest.mock import patch

def test_sends_email():
    with patch("yourpkg.mailer.smtp", autospec=True) as mock_smtp:
        send_welcome_email("alice@example.com")
        mock_smtp.SMTP.assert_called_once()
```

---

## 5) Async & concurrency

- Use **`pytest-asyncio`** for `async def` tests (configure loop scope if needed).
- Avoid real sleeps; await tasks and set timeouts.
- Ensure cleanup of tasks to avoid event‑loop leakage.
- Be careful when combining async tests with parallelization (xdist); isolate shared state.

```python
import pytest

async def test_async_flow():
    assert await do_async() == "ok"
```

---

## 6) Determinism: random, time, order

- Shuffle test order locally with a random-order plugin if you choose to add one back.
- Freeze time for clock‑sensitive logic with **Freezegun** or **pytest-freezer**.
- When asserting on logs, set levels explicitly: `caplog.set_level(\"INFO\")`.

---

## 7) Speed & reliability (flake‑resistant)

- **Parallelize** locally and in CI with **`pytest-xdist`**: `pytest -n auto`.
- Separate **fast smoke tests** from **slow** ones with markers; run `-m "not slow"` in tight loops.
- Avoid real network/disk where possible:
  - Use **`responses`** for `requests`
  - Use **`respx`** for `httpx`
- Keep fixtures small and scoped; prefer function scope by default.

---

## 8) Coverage you can act on

- Use **coverage.py** (via **`pytest-cov`**) with **branch coverage**.
- Enable **coverage contexts** to answer “_which test covered this line?_”.

**Coverage config (pyproject) and usage:**
```toml
[tool.coverage.run]
branch = true
dynamic_context = "test_function"

[tool.coverage.report]
show_missing = true
fail_under = 90
```
```bash
pytest --cov=yourpkg --cov-report=term-missing --cov-report=html --cov-context=test
# Open htmlcov/index.html to review per-test contexts
```

---

## 9) Property‑based testing (PBT)

Use **Hypothesis** to generate many inputs and shrink failures automatically.

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_round_trip(s):
    assert decode(encode(s)) == s
```

Great for parsers, arithmetic, serialization, and stateful workflows.

---

## 10) Frequently useful pytest flags

- `-q -ra` — quiet + extra summary of fails/skips
- `-k EXPRESSION` — filter by test name expression
- `-m MARKEXPR` — run by marker (e.g., `-m "smoke and not slow"`)
- `--maxfail=1` — fail fast
- `--pdb -x` — drop into debugger on first failure
- `--ff` — run failures first (requires `pytest`'s cache)

---

## 11) Example repository skeleton

See Section 1 for directory layout.

**`tests/test_core.py`**
```python
import pytest
from yourpkg.core import add

@pytest.mark.smoke
@pytest.mark.parametrize("a,b,out", [(1,2,3),(0,0,0),(-1,1,0)])
def test_add(a, b, out):
    assert add(a, b) == out
```

---

## 12) CI quickstart (GitHub Actions)

```yaml
name: tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: |
          pip install -e .
          pip install pytest pytest-cov pytest-asyncio pytest-xdist hypothesis
          pytest -n auto -q --cov=yourpkg --cov-report=term-missing --cov-context=test
```

---

## 13) Quick checklist

- [ ] `src/` layout with tests in `tests/`
- [ ] `pyproject.toml` has `--strict-markers` and `--strict-config`
- [ ] Slow tests are marked and isolated
- [ ] Parallel runs are clean (`pytest -n auto`)
- [ ] Coverage: branch + contexts, threshold set
- [ ] Deterministic RNG/time; flaky sources stubbed
- [ ] Async tests use `pytest-asyncio`
- [ ] Property‑based tests for critical invariants
- [ ] CI runs matrix across supported Python versions

---

## 14) Troubleshooting tips

- **Import errors disappear locally, fail in CI** → ensure `src/` layout and install the package in editable mode (`pip install -e .`) before running tests.
- **Mock doesn’t behave like real object** → use `autospec`/`spec_set` and patch the import location used by the SUT.
- **Intermittent failures** → seed randomness, freeze time, and run with `-n auto --dist loadfile` to surface shared‑state issues.
- **“Which test hit this line?”** → enable coverage contexts (`--cov-context=test`) and inspect `htmlcov` (toggle “Show contexts”).

---

Happy testing! 🧪
