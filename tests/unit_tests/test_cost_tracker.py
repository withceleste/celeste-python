"""Tests for the CostTracker class."""

import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from celeste.pricing import Cost, CostBreakdown, CostTracker


class TestCostBreakdown:
    """Tests for the CostBreakdown dataclass."""

    def test_default_values(self) -> None:
        """Test that CostBreakdown has correct default values."""
        breakdown = CostBreakdown()
        assert breakdown.input == 0.0
        assert breakdown.output == 0.0
        assert breakdown.cache_creation == 0.0
        assert breakdown.cache_read == 0.0
        assert breakdown.reasoning == 0.0
        assert breakdown.image == 0.0
        assert breakdown.audio == 0.0
        assert breakdown.video == 0.0

    def test_total_property(self) -> None:
        """Test that total computes correctly."""
        breakdown = CostBreakdown(
            input=0.001,
            output=0.002,
            cache_read=0.0005,
        )
        assert breakdown.total == pytest.approx(0.0035)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        breakdown = CostBreakdown(input=0.001, output=0.002)
        result = breakdown.to_dict()

        assert result["input"] == 0.001
        assert result["output"] == 0.002
        assert result["total"] == pytest.approx(0.003)
        assert "cache_creation" in result
        assert "reasoning" in result


class TestCostTracker:
    """Tests for the CostTracker class."""

    def test_initial_state(self) -> None:
        """Test that CostTracker starts empty."""
        tracker = CostTracker()
        assert tracker.total == 0.0
        assert tracker.count == 0

    def test_add_cost(self) -> None:
        """Test adding a cost to the tracker."""
        tracker = CostTracker()
        cost = Cost(input_cost=0.001, output_cost=0.002)
        tracker.add(cost)

        assert tracker.count == 1
        assert tracker.total == pytest.approx(0.003)

    def test_add_none_cost(self) -> None:
        """Test that adding None is ignored."""
        tracker = CostTracker()
        tracker.add(None)
        assert tracker.count == 0

    def test_add_multiple_costs(self) -> None:
        """Test adding multiple costs."""
        tracker = CostTracker()
        tracker.add(Cost(input_cost=0.001))
        tracker.add(Cost(input_cost=0.002))
        tracker.add(Cost(output_cost=0.003))

        assert tracker.count == 3
        assert tracker.total == pytest.approx(0.006)

    def test_breakdown(self) -> None:
        """Test that breakdown aggregates correctly."""
        tracker = CostTracker()
        tracker.add(Cost(input_cost=0.001, output_cost=0.002))
        tracker.add(Cost(input_cost=0.003, image_cost=0.01))

        breakdown = tracker.breakdown
        assert breakdown.input == pytest.approx(0.004)
        assert breakdown.output == pytest.approx(0.002)
        assert breakdown.image == pytest.approx(0.01)

    def test_reset(self) -> None:
        """Test that reset clears all costs."""
        tracker = CostTracker()
        tracker.add(Cost(input_cost=0.001))
        tracker.add(Cost(output_cost=0.002))
        assert tracker.count == 2

        tracker.reset()
        assert tracker.count == 0
        assert tracker.total == 0.0

    def test_get_costs(self) -> None:
        """Test that get_costs returns a copy."""
        tracker = CostTracker()
        cost1 = Cost(input_cost=0.001)
        cost2 = Cost(output_cost=0.002)
        tracker.add(cost1)
        tracker.add(cost2)

        costs = tracker.get_costs()
        assert len(costs) == 2
        assert costs[0] == cost1
        assert costs[1] == cost2

        # Verify it's a copy
        costs.append(Cost())
        assert tracker.count == 2

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        tracker = CostTracker()
        tracker.add(Cost(input_cost=0.001, output_cost=0.002))

        result = tracker.to_dict()
        assert result["total"] == pytest.approx(0.003)
        assert result["count"] == 1
        assert result["currency"] == "USD"
        assert "breakdown" in result

    def test_thread_safety(self) -> None:
        """Test that CostTracker is thread-safe."""
        tracker = CostTracker()
        num_threads = 10
        adds_per_thread = 100

        def add_costs() -> None:
            for _ in range(adds_per_thread):
                tracker.add(Cost(input_cost=0.001))

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(add_costs) for _ in range(num_threads)]
            for future in futures:
                future.result()

        expected_count = num_threads * adds_per_thread
        assert tracker.count == expected_count
        assert tracker.total == pytest.approx(expected_count * 0.001)

    def test_concurrent_read_write(self) -> None:
        """Test concurrent reading and writing."""
        tracker = CostTracker()
        num_iterations = 100
        errors: list[Exception] = []

        def writer() -> None:
            for _ in range(num_iterations):
                try:
                    tracker.add(Cost(input_cost=0.001))
                except Exception as e:
                    errors.append(e)

        def reader() -> None:
            for _ in range(num_iterations):
                try:
                    _ = tracker.total
                    _ = tracker.breakdown
                    _ = tracker.count
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=writer) for _ in range(5)] + [
            threading.Thread(target=reader) for _ in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestCostTrackerIntegration:
    """Integration tests for CostTracker with Cost objects."""

    def test_all_cost_types(self) -> None:
        """Test tracking all types of costs."""
        tracker = CostTracker()

        tracker.add(
            Cost(
                input_cost=0.001,
                output_cost=0.002,
                cache_creation_cost=0.0003,
                cache_read_cost=0.0001,
                reasoning_cost=0.003,
                image_cost=0.04,
                audio_cost=0.05,
                video_cost=0.06,
            )
        )

        breakdown = tracker.breakdown
        assert breakdown.input == pytest.approx(0.001)
        assert breakdown.output == pytest.approx(0.002)
        assert breakdown.cache_creation == pytest.approx(0.0003)
        assert breakdown.cache_read == pytest.approx(0.0001)
        assert breakdown.reasoning == pytest.approx(0.003)
        assert breakdown.image == pytest.approx(0.04)
        assert breakdown.audio == pytest.approx(0.05)
        assert breakdown.video == pytest.approx(0.06)

    def test_mixed_cost_types(self) -> None:
        """Test tracking mixed cost types."""
        tracker = CostTracker()

        # Text generation
        tracker.add(Cost(input_cost=0.001, output_cost=0.002))
        # Image generation
        tracker.add(Cost(image_cost=0.04))
        # Audio generation
        tracker.add(Cost(audio_cost=0.05))

        assert tracker.count == 3
        breakdown = tracker.breakdown
        assert breakdown.input == pytest.approx(0.001)
        assert breakdown.output == pytest.approx(0.002)
        assert breakdown.image == pytest.approx(0.04)
        assert breakdown.audio == pytest.approx(0.05)
