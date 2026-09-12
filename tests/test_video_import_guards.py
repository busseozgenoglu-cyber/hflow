"""Video import configuration reports precise numeric-field failures."""

import re
from dataclasses import replace

import pytest

from hflow.importers.video import VideoImportConfig


_MAXIMUM_TIMESTAMP_NS = (1 << 64) - 1


@pytest.mark.parametrize(
    ("changes", "expected_message"),
    [
        ({"duration_s": True}, "duration_s must be an int or float, got bool"),
        ({"duration_s": "1"}, "duration_s must be an int or float, got str"),
        ({"duration_s": float("nan")}, "duration_s must be finite, got nan"),
        ({"source_start_s": float("inf")}, "source_start_s must be finite, got inf"),
        ({"image_hz": float("-inf")}, "image_hz must be finite, got -inf"),
        ({"image_width": True}, "image_width must be an int, got bool"),
        ({"image_width": 0}, "image_width must be > 0, got 0"),
        ({"image_width": -2}, "image_width must be > 0, got -2"),
        ({"image_width": 3}, "image_width must be even, got 3"),
        ({"image_height": False}, "image_height must be an int, got bool"),
        ({"image_height": 5}, "image_height must be even, got 5"),
        ({"start_time_ns": True}, "start_time_ns must be an int, got bool"),
        (
            {"start_time_ns": -1},
            f"start_time_ns must be in [0, {_MAXIMUM_TIMESTAMP_NS}], got -1",
        ),
        (
            {"start_time_ns": _MAXIMUM_TIMESTAMP_NS + 1},
            "start_time_ns must be in "
            f"[0, {_MAXIMUM_TIMESTAMP_NS}], got {_MAXIMUM_TIMESTAMP_NS + 1}",
        ),
    ],
)
def test_numeric_configuration_guards_name_the_field_and_bad_value(
    changes: dict[str, object], expected_message: str
) -> None:
    with pytest.raises(ValueError, match=rf"^{re.escape(expected_message)}$"):
        replace(VideoImportConfig(duration_s=1), **changes)


def test_valid_even_dimensions_and_timestamp_bounds_are_unchanged() -> None:
    config = VideoImportConfig(
        duration_s=1,
        image_width=2,
        image_height=4,
        start_time_ns=_MAXIMUM_TIMESTAMP_NS - 1_000_000_000,
    )

    assert config.image_width == 2
    assert config.image_height == 4
    assert config.start_time_ns == _MAXIMUM_TIMESTAMP_NS - 1_000_000_000
