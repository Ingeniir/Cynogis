import pytest

from cynogis.core.atlas import MARGIN, layout_boxes, page_size


def test_formats():
    assert page_size("A4", "landscape") == (297.0, 210.0)
    assert page_size("A3", "portrait") == (297.0, 420.0)
    with pytest.raises(ValueError):
        page_size("A5", "landscape")


@pytest.mark.parametrize("size", ["A4", "A3"])
@pytest.mark.parametrize("orientation", ["landscape", "portrait"])
@pytest.mark.parametrize("legend", [True, False])
@pytest.mark.parametrize("overview", [True, False])
def test_zones_dans_la_page_sans_chevauchement(size, orientation, legend, overview):
    width, height = page_size(size, orientation)
    boxes = layout_boxes(size, orientation, legend, overview)
    assert ("legend" in boxes) == legend and ("overview" in boxes) == overview
    for box in boxes.values():
        assert box.x >= MARGIN and box.y >= MARGIN and box.width > 0 and box.height > 0
        assert box.x + box.width <= width - MARGIN + 1e-9
        assert box.y + box.height <= height - MARGIN + 1e-9
    items = list(boxes.values())
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            overlap_x = a.x < b.x + b.width and b.x < a.x + a.width
            overlap_y = a.y < b.y + b.height and b.y < a.y + a.height
            assert not (overlap_x and overlap_y)
