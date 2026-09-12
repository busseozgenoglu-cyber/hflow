"""Focused numeric-guard coverage for VideoImportConfig."""

from dataclasses import replace

import pytest

from hflow.importers.video import VideoImportConfig


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("duration_s", True, "duration_s must be an int or float, got bool"),
        ("duration_s", float("nan"), "duration_s must be finite, got nan"),
        ("source_start_s", "0", "source_start_s must be an int or float, got str"),
        ("image_hz", float("inf"), "image_hz must be finite, got inf"),
        ("image_width", True, "image_width must be an int, got bool"),
        ("image_width", -2, "image_width must be > 0, got -2"),
        ("image_width", 3, "image_width must be even, got 3"),
        ("image_height", 3, "image_height must be even, got 3"),
        ("start_time_ns", True, "start_time_ns must be an int, got bool"),
        ("start_time_ns", -1, "start_time_ns must be in [0, 18446744073709551615], got -1"),
        (
            "start_time_ns",
            1 << 64,
            "start_time_ns must be in [0, 18446744073709551615], got 18446744073709551616",
        ),
    ],
)
def test_numeric_field_guards(field: str, value: object, message: str) -> None:
    with pytest.raises(ValueError, match=rf"^{message.replace('[', r'\[').replace(']', r'\]')}$"):
        replace(VideoImportConfig(duration_s=1), **{field: value})


def test_valid_numeric_configuration_is_unchanged() -> None:
    config = VideoImportConfig(
        duration_s=1,
        source_start_s=0,
        image_hz=30,
        image_width=640,
        image_height=360,
        start_time_ns=(1 << 64) - 1_000_000_000,
    )

    assert config.frame_count == 30
