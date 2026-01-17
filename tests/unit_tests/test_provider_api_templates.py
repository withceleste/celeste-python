from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TemplateExpectations:
    usage_map_return: str
    parse_usage_return: str


TEMPLATE_REQUIRED_METHODS: set[str] = {
    "_make_request",
    "_make_stream_request",
    "map_usage_fields",
    "_parse_usage",
    "_parse_content",
    "_parse_finish_reason",
    "_build_metadata",
}


def _repo_root() -> Path:
    # This file lives at: celeste-python-private/tests/unit_tests/test_provider_api_templates.py
    return Path(__file__).resolve().parents[2]


def _template_client_path() -> Path:
    root = _repo_root()
    return (
        root
        / "templates"
        / "providers"
        / "{provider_slug}"
        / "src"
        / "celeste_{provider_slug}"
        / "{api_slug}"
        / "client.py.template"
    )


def _extract_template_expectations(template_text: str) -> TemplateExpectations:
    # Return annotations are stable and placeholder-free; we can regex them out of the template.
    def_ret_re = re.compile(
        r"^\s*(?:async\s+def|def)\s+(?P<name>[a-zA-Z0-9_]+)\s*\([^\)]*\)\s*(?:->\s*(?P<ret>[^:]+))?:",
        re.M,
    )

    returns: dict[str, str | None] = {}
    for m in def_ret_re.finditer(template_text):
        name = m.group("name")
        returns[name] = (m.group("ret") or "").strip() or None

    usage_map_return = returns.get("map_usage_fields")
    parse_usage_return = returns.get("_parse_usage")
    assert usage_map_return is not None
    assert parse_usage_return is not None

    # Also ensure the endpoint routing contract is present in the template.
    assert "async def _make_request" in template_text
    assert "endpoint: str | None = None" in template_text
    assert "def _make_stream_request" in template_text

    return TemplateExpectations(
        usage_map_return=usage_map_return,
        parse_usage_return=parse_usage_return,
    )


def _find_provider_module_dir(provider_pkg: Path) -> Path | None:
    src = provider_pkg / "src"
    if not src.exists():
        return None

    candidates = [
        p for p in src.iterdir() if p.is_dir() and p.name.startswith("celeste_")
    ]
    if not candidates:
        return None

    expected = f"celeste_{provider_pkg.name}"
    for c in candidates:
        if c.name == expected:
            return c

    return sorted(candidates)[0]


def _provider_api_client_files() -> list[Path]:
    root = _repo_root()
    providers_dir = root / "src" / "celeste" / "providers"

    # Wrapper providers that just re-export another provider's client
    # These don't need to match the template contract
    wrapper_providers = {"ollama"}

    out: list[Path] = []
    for provider_dir in sorted([p for p in providers_dir.iterdir() if p.is_dir()]):
        # Skip wrapper providers
        if provider_dir.name in wrapper_providers:
            continue
        # Each provider has API subdirs (e.g., openai/responses, openai/images)
        for api_dir in sorted([p for p in provider_dir.iterdir() if p.is_dir()]):
            client_path = api_dir / "client.py"
            if client_path.exists():
                out.append(client_path)

    # Sanity check: we currently expect ~20 provider API modules.
    assert len(out) >= 15
    return out


def _first_class(tree: ast.Module) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            return node
    msg = "No top-level class found"
    raise AssertionError(msg)


def _class_methods(
    cls: ast.ClassDef,
) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    methods: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods[node.name] = node
    return methods


def _kwonly_arg(
    fn: ast.FunctionDef | ast.AsyncFunctionDef, name: str
) -> tuple[ast.arg, ast.expr | None] | None:
    for arg, default in zip(fn.args.kwonlyargs, fn.args.kw_defaults, strict=True):
        if arg.arg == name:
            return arg, default
    return None


def _has_staticmethod_decorator(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for dec in fn.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "staticmethod":
            return True
    return False


def test_provider_template_contract_is_parseable() -> None:
    template_path = _template_client_path()
    text = template_path.read_text(encoding="utf-8")
    _extract_template_expectations(text)


def test_all_provider_api_mixins_match_template_contract() -> None:
    template_text = _template_client_path().read_text(encoding="utf-8")
    exp = _extract_template_expectations(template_text)

    for client_path in _provider_api_client_files():
        tree = ast.parse(client_path.read_text(encoding="utf-8"))
        cls = _first_class(tree)
        methods = _class_methods(cls)

        missing = sorted(TEMPLATE_REQUIRED_METHODS - set(methods.keys()))
        assert not missing, f"{client_path}: missing methods: {missing}"

        # Endpoint routing contract
        make_request = methods["_make_request"]
        make_stream = methods["_make_stream_request"]

        for fn_name, fn in (
            ("_make_request", make_request),
            ("_make_stream_request", make_stream),
        ):
            kw = _kwonly_arg(fn, "endpoint")
            assert kw is not None, f"{client_path}: {fn_name} missing kw-only endpoint"
            endpoint_arg, endpoint_default = kw

            assert endpoint_arg.annotation is not None, (
                f"{client_path}: {fn_name} endpoint missing annotation"
            )
            assert ast.unparse(endpoint_arg.annotation).strip() == "str | None", (
                f"{client_path}: {fn_name} endpoint annotation mismatch"
            )
            assert (
                isinstance(endpoint_default, ast.Constant)
                and endpoint_default.value is None
            ), f"{client_path}: {fn_name} endpoint default must be None"

        # Usage typing parity (matches template)
        map_usage_fields = methods["map_usage_fields"]
        assert _has_staticmethod_decorator(map_usage_fields), (
            f"{client_path}: map_usage_fields must be @staticmethod"
        )

        assert map_usage_fields.returns is not None, (
            f"{client_path}: map_usage_fields missing return annotation"
        )
        assert ast.unparse(map_usage_fields.returns).strip() == exp.usage_map_return, (
            f"{client_path}: map_usage_fields return annotation mismatch"
        )

        parse_usage = methods["_parse_usage"]
        assert parse_usage.returns is not None, (
            f"{client_path}: _parse_usage missing return annotation"
        )
        assert ast.unparse(parse_usage.returns).strip() == exp.parse_usage_return, (
            f"{client_path}: _parse_usage return annotation mismatch"
        )
