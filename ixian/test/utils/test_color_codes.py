import pytest

from ixian.utils import color_codes


@pytest.fixture(params=list(color_codes.COLOR_REFERENCE.items()))
def color(request):
    yield request.param


@pytest.fixture(
    params=[
        color_codes.red,
        color_codes.green,
        color_codes.yellow,
        color_codes.gray,
        color_codes.bold_white,
    ]
)
def color_method(request):
    yield request.param


class TestColorCodes:
    """Test that all color codes render"""

    def test_colors(self, snapshot, color):
        """Test that all colors may be printed"""
        name, color = color
        snapshot.assert_match(color_codes.format("testing", color), name)

    def test_color_methods(self, snapshot, color_method):
        snapshot.assert_match(color_method("testing"))
