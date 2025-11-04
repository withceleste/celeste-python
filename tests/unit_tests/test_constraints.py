"""Tests for constraint validation models."""

import pytest

from celeste.constraints import Bool, Choice, Float, Int, Pattern, Range, Str


class TestChoice:
    """Test Choice constraint validation."""

    @pytest.mark.smoke
    def test_validates_value_in_options(self) -> None:
        """Test that valid choice passes validation."""
        constraint = Choice[str](options=["a", "b", "c"])

        result = constraint("b")

        assert result == "b"

    def test_rejects_value_not_in_options(self) -> None:
        """Test that invalid choice raises ValueError."""
        constraint = Choice[str](options=["a", "b", "c"])

        with pytest.raises(
            ValueError, match=r"Must be one of \['a', 'b', 'c'\], got 'd'"
        ):
            constraint("d")

    def test_works_with_numeric_types(self) -> None:
        """Test Choice works with int/float options."""
        constraint = Choice[int](options=[1, 2, 3])

        result = constraint(2)

        assert result == 2

    def test_rejects_empty_options_list(self) -> None:
        """Test Choice construction fails with empty options."""
        with pytest.raises(ValueError):
            Choice[str](options=[])


class TestRange:
    """Test Range constraint validation."""

    @pytest.mark.smoke
    def test_validates_value_within_range(self) -> None:
        """Test that value within bounds passes validation."""
        constraint = Range(min=0.0, max=1.0)

        result = constraint(0.5)

        assert result == 0.5

    def test_validates_boundary_values(self) -> None:
        """Test that min/max boundary values are inclusive."""
        constraint = Range(min=0, max=10)

        assert constraint(0) == 0
        assert constraint(10) == 10

    def test_rejects_value_below_min(self) -> None:
        """Test that value below min raises ValueError."""
        constraint = Range(min=0, max=10)

        with pytest.raises(ValueError, match=r"Must be between 0 and 10, got -1"):
            constraint(-1)

    def test_rejects_value_above_max(self) -> None:
        """Test that value above max raises ValueError."""
        constraint = Range(min=0, max=10)

        with pytest.raises(ValueError, match=r"Must be between 0 and 10, got 11"):
            constraint(11)

    def test_rejects_non_numeric_value(self) -> None:
        """Test that non-numeric value raises TypeError."""
        constraint = Range(min=0, max=10)

        with pytest.raises(TypeError, match=r"Must be numeric, got str"):
            constraint("5")  # type: ignore[arg-type]

    def test_accepts_both_int_and_float(self) -> None:
        """Test Range accepts both int and float values."""
        constraint = Range(min=0.0, max=10.0)

        assert constraint(5) == 5  # int
        assert constraint(5.5) == 5.5  # float

    def test_validates_value_with_step(self) -> None:
        """Test that value at valid step increment passes."""
        constraint = Range(min=0, max=10, step=2)

        assert constraint(0) == 0  # min
        assert constraint(2) == 2
        assert constraint(4) == 4
        assert constraint(10) == 10  # max

    def test_rejects_value_not_on_step(self) -> None:
        """Test that value not on step increment raises ValueError."""
        constraint = Range(min=0, max=10, step=2)

        with pytest.raises(
            ValueError,
            match=r"Value must match step 2(\.0)?. Nearest valid: 2(\.0)? or 4(\.0)?, got 3",
        ):
            constraint(3)

    def test_validates_float_step(self) -> None:
        """Test step validation with float increments."""
        constraint = Range(min=0.0, max=1.0, step=0.25)

        assert constraint(0.0) == 0.0
        assert constraint(0.25) == 0.25
        assert constraint(0.5) == 0.5
        assert constraint(0.75) == 0.75
        assert constraint(1.0) == 1.0

    def test_step_validation_with_non_zero_min(self) -> None:
        """Test step validation calculates offset from min correctly."""
        constraint = Range(min=5, max=15, step=3)

        assert constraint(5) == 5  # min
        assert constraint(8) == 8  # min + 3
        assert constraint(11) == 11  # min + 6
        assert constraint(14) == 14  # min + 9

        with pytest.raises(
            ValueError,
            match=r"Value must match step 3(\.0)?. Nearest valid: 5(\.0)? or 8(\.0)?, got 7",
        ):
            constraint(7)

    def test_step_validation_handles_float_precision(self) -> None:
        """Test step validation handles floating-point precision issues."""
        constraint = Range(min=0.0, max=2.0, step=0.1)

        # These should all pass despite potential float precision issues
        assert constraint(0.0) == 0.0
        assert constraint(0.1) == 0.1
        assert constraint(0.7) == 0.7
        assert constraint(1.0) == 1.0
        assert constraint(2.0) == 2.0

    def test_validates_value_near_step_within_epsilon(self) -> None:
        """Range validates values within epsilon tolerance of valid step."""
        constraint = Range(min=0.0, max=10.0, step=0.1)

        # Test values that might have floating-point precision issues
        # 0.1 + 0.1 + 0.1 might be 0.30000000000000004 due to float representation
        result = constraint(0.1 + 0.1 + 0.1)  # Should be ~0.3
        assert result == pytest.approx(0.3)

        # Test another precision edge case
        result2 = constraint(0.7)  # Should pass within epsilon
        assert result2 == pytest.approx(0.7)


class TestPattern:
    """Test Pattern constraint validation."""

    @pytest.mark.smoke
    def test_validates_matching_pattern(self) -> None:
        """Test that string matching pattern passes validation."""
        constraint = Pattern(pattern=r"^\d{3}-\d{4}$")

        result = constraint("123-4567")

        assert result == "123-4567"

    def test_rejects_non_matching_pattern(self) -> None:
        """Test that non-matching pattern raises ValueError."""
        constraint = Pattern(pattern=r"^\d{3}-\d{4}$")

        with pytest.raises(ValueError, match=r"Must match pattern"):
            constraint("abc-defg")

    def test_rejects_non_string_value(self) -> None:
        """Test that non-string value raises TypeError."""
        constraint = Pattern(pattern=r"^\d+$")

        with pytest.raises(TypeError, match=r"Must be string, got int"):
            constraint(123)  # type: ignore[arg-type]

    def test_validates_complex_regex_patterns(self) -> None:
        """Test Pattern works with complex regex."""
        # Email-like pattern
        constraint = Pattern(pattern=r"^[a-z]+@[a-z]+\.[a-z]+$")

        result = constraint("user@domain.com")

        assert result == "user@domain.com"


class TestStr:
    """Test Str constraint validation."""

    @pytest.mark.smoke
    def test_validates_string_without_length_constraints(self) -> None:
        """Test that any string passes when no length constraints set."""
        constraint = Str()

        result = constraint("any string")

        assert result == "any string"

    def test_validates_string_within_length_bounds(self) -> None:
        """Test string within min/max length passes."""
        constraint = Str(min_length=2, max_length=10)

        result = constraint("valid")

        assert result == "valid"

    def test_rejects_string_below_min_length(self) -> None:
        """Test string shorter than min_length raises ValueError."""
        constraint = Str(min_length=5)

        with pytest.raises(ValueError, match=r"String too short \(min 5\), got 3"):
            constraint("abc")

    def test_rejects_string_above_max_length(self) -> None:
        """Test string longer than max_length raises ValueError."""
        constraint = Str(max_length=5)

        with pytest.raises(ValueError, match=r"String too long \(max 5\), got 10"):
            constraint("too long!!")

    def test_rejects_non_string_value(self) -> None:
        """Test non-string value raises TypeError."""
        constraint = Str()

        with pytest.raises(TypeError, match=r"Must be string, got int"):
            constraint(123)  # type: ignore[arg-type]

    def test_validates_boundary_lengths(self) -> None:
        """Test exact min/max length strings are valid."""
        constraint = Str(min_length=3, max_length=5)

        assert constraint("abc") == "abc"  # min
        assert constraint("abcde") == "abcde"  # max


class TestInt:
    """Test Int constraint validation."""

    @pytest.mark.smoke
    def test_validates_integer_value(self) -> None:
        """Test that integer passes validation."""
        constraint = Int()

        result = constraint(42)

        assert result == 42

    def test_rejects_float_value(self) -> None:
        """Test that float raises TypeError."""
        constraint = Int()

        with pytest.raises(TypeError, match=r"Must be int, got float"):
            constraint(42.0)  # type: ignore[arg-type]

    def test_rejects_boolean_value(self) -> None:
        """Test that bool raises TypeError despite isinstance(True, int)."""
        constraint = Int()

        with pytest.raises(TypeError, match=r"Must be int, got bool"):
            constraint(True)

    def test_rejects_string_value(self) -> None:
        """Test that string raises TypeError."""
        constraint = Int()

        with pytest.raises(TypeError, match=r"Must be int, got str"):
            constraint("42")  # type: ignore[arg-type]


class TestFloat:
    """Test Float constraint validation."""

    @pytest.mark.smoke
    def test_validates_float_value(self) -> None:
        """Test that float passes validation."""
        constraint = Float()

        result = constraint(3.14)

        assert result == 3.14

    def test_accepts_and_converts_int_to_float(self) -> None:
        """Test that int is accepted and converted to float."""
        constraint = Float()

        result = constraint(42)

        assert result == 42.0
        assert isinstance(result, float)

    def test_rejects_boolean_value(self) -> None:
        """Test that bool raises TypeError despite isinstance(True, int)."""
        constraint = Float()

        with pytest.raises(TypeError, match=r"Must be float or int, got bool"):
            constraint(True)

    def test_rejects_string_value(self) -> None:
        """Test that string raises TypeError."""
        constraint = Float()

        with pytest.raises(TypeError, match=r"Must be float or int, got str"):
            constraint("3.14")  # type: ignore[arg-type]


class TestBool:
    """Test Bool constraint validation."""

    @pytest.mark.smoke
    def test_validates_boolean_value(self) -> None:
        """Test that bool passes validation."""
        constraint = Bool()

        assert constraint(True) is True
        assert constraint(False) is False

    def test_rejects_int_value(self) -> None:
        """Test that int raises TypeError (no implicit 0/1 conversion)."""
        constraint = Bool()

        with pytest.raises(TypeError, match=r"Must be bool, got int"):
            constraint(1)  # type: ignore[arg-type]

    def test_rejects_string_value(self) -> None:
        """Test that string raises TypeError."""
        constraint = Bool()

        with pytest.raises(TypeError, match=r"Must be bool, got str"):
            constraint("true")  # type: ignore[arg-type]
