import pytest

from celeste.constraints import Range
from celeste.core import Parameter, Provider
from celeste.exceptions import ConstraintViolationError
from celeste.models import Model
from celeste.parameters import FieldMapper


class TemperatureMapper(FieldMapper[str]):
    name = Parameter.TEMPERATURE
    field = "temperature"


def _model(constraint: Range | None = None) -> Model:
    constraints = {Parameter.TEMPERATURE: constraint} if constraint else {}
    return Model(
        id="test-model",
        provider=Provider.OPENAI,
        display_name="Test Model",
        parameter_constraints=constraints,
    )


@pytest.mark.parametrize(
    ("value", "constraint", "expected"),
    [
        (None, Range(min=0, max=1), {}),
        (2.0, None, {"temperature": 2.0}),
        (0.7, Range(min=0, max=1), {"temperature": 0.7}),
    ],
)
def test_field_mapper_maps_and_validates(
    value: float | None, constraint: Range | None, expected: dict[str, float]
) -> None:
    assert TemperatureMapper().map({}, value, _model(constraint)) == expected


def test_field_mapper_rejects_constraint_violation() -> None:
    with pytest.raises(ConstraintViolationError):
        TemperatureMapper().map({}, 2.0, _model(Range(min=0, max=1)))


def test_parameter_mapper_default_output_is_identity() -> None:
    content = "content"
    assert TemperatureMapper().parse_output(content, 0.7) is content
