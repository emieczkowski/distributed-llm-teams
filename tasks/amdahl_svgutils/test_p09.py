"""Pre-written test suite for SVG Utils Library (all p-values, N=20)."""
import pytest


# ── fmt_num ──────────────────────────────────────────────────────────────────
def test_fmt_num_whole_float():
    from fmt_num import fmt_num
    assert fmt_num(5.0) == "5"

def test_fmt_num_whole_int():
    from fmt_num import fmt_num
    assert fmt_num(100) == "100"

def test_fmt_num_zero():
    from fmt_num import fmt_num
    assert fmt_num(0) == "0"

def test_fmt_num_decimal():
    from fmt_num import fmt_num
    assert fmt_num(3.14) == "3.14"

def test_fmt_num_single_decimal():
    from fmt_num import fmt_num
    assert fmt_num(3.1) == "3.1"

def test_fmt_num_negative_whole():
    from fmt_num import fmt_num
    assert fmt_num(-5.0) == "-5"

def test_fmt_num_negative_decimal():
    from fmt_num import fmt_num
    assert fmt_num(-3.14) == "-3.14"

def test_fmt_num_strips_trailing_zeros():
    from fmt_num import fmt_num
    assert fmt_num(1.50) == "1.5"


# ── fmt_coord ─────────────────────────────────────────────────────────────────
def test_fmt_coord_integers():
    from fmt_coord import fmt_coord
    assert fmt_coord(10, 20) == "10,20"

def test_fmt_coord_floats():
    from fmt_coord import fmt_coord
    assert fmt_coord(1.5, 2.5) == "1.5,2.5"

def test_fmt_coord_zero():
    from fmt_coord import fmt_coord
    assert fmt_coord(0, 0) == "0,0"

def test_fmt_coord_mixed():
    from fmt_coord import fmt_coord
    assert fmt_coord(10.0, 20) == "10,20"

def test_fmt_coord_negative():
    from fmt_coord import fmt_coord
    assert fmt_coord(-5, 10) == "-5,10"


# ── fmt_points ───────────────────────────────────────────────────────────────
def test_fmt_points_single():
    from fmt_points import fmt_points
    assert fmt_points([(0, 0)]) == "0,0"

def test_fmt_points_two():
    from fmt_points import fmt_points
    assert fmt_points([(0, 0), (10, 10)]) == "0,0 10,10"

def test_fmt_points_three():
    from fmt_points import fmt_points
    assert fmt_points([(0, 0), (10, 0), (5, 10)]) == "0,0 10,0 5,10"

def test_fmt_points_floats():
    from fmt_points import fmt_points
    assert fmt_points([(1.5, 2.5)]) == "1.5,2.5"

def test_fmt_points_space_separated():
    from fmt_points import fmt_points
    result = fmt_points([(0, 0), (10, 10), (20, 0)])
    assert result == "0,0 10,10 20,0"


# ── make_polyline ────────────────────────────────────────────────────────────
def test_make_polyline_tag():
    from make_polyline import make_polyline
    result = make_polyline([(0, 0), (10, 10)])
    assert result.startswith("<polyline")
    assert result.endswith("/>")

def test_make_polyline_points():
    from make_polyline import make_polyline
    result = make_polyline([(0, 0), (10, 10)])
    assert 'points="0,0 10,10"' in result

def test_make_polyline_default_stroke():
    from make_polyline import make_polyline
    result = make_polyline([(0, 0), (10, 10)])
    assert 'stroke="black"' in result

def test_make_polyline_default_stroke_width():
    from make_polyline import make_polyline
    result = make_polyline([(0, 0), (10, 10)])
    assert 'stroke-width="1"' in result

def test_make_polyline_fill_none():
    from make_polyline import make_polyline
    result = make_polyline([(0, 0), (10, 10)])
    assert 'fill="none"' in result

def test_make_polyline_custom_stroke():
    from make_polyline import make_polyline
    result = make_polyline([(0, 0), (10, 10)], stroke="red", stroke_width=2)
    assert 'stroke="red"' in result
    assert 'stroke-width="2"' in result

def test_make_polyline_three_points():
    from make_polyline import make_polyline
    result = make_polyline([(0, 0), (10, 0), (10, 10)])
    assert 'points="0,0 10,0 10,10"' in result


# ── make_polygon ─────────────────────────────────────────────────────────────
def test_make_polygon_tag():
    from make_polygon import make_polygon
    result = make_polygon([(0, 0), (10, 0), (5, 10)])
    assert result.startswith("<polygon")

def test_make_polygon_points():
    from make_polygon import make_polygon
    result = make_polygon([(0, 0), (10, 0), (5, 10)])
    assert 'points="0,0 10,0 5,10"' in result

def test_make_polygon_default_fill():
    from make_polygon import make_polygon
    result = make_polygon([(0, 0), (10, 0), (5, 10)])
    assert 'fill="none"' in result

def test_make_polygon_default_stroke():
    from make_polygon import make_polygon
    result = make_polygon([(0, 0), (10, 0), (5, 10)])
    assert 'stroke="black"' in result

def test_make_polygon_custom_fill():
    from make_polygon import make_polygon
    result = make_polygon([(0, 0), (10, 0), (5, 10)], fill="blue")
    assert 'fill="blue"' in result

def test_make_polygon_custom_stroke():
    from make_polygon import make_polygon
    result = make_polygon([(0, 0), (10, 0), (5, 10)], stroke="red")
    assert 'stroke="red"' in result


# ── make_triangle ────────────────────────────────────────────────────────────
def test_make_triangle_is_polygon():
    from make_triangle import make_triangle
    result = make_triangle(0, 0, 10, 0, 5, 10)
    assert result.startswith("<polygon")

def test_make_triangle_points():
    from make_triangle import make_triangle
    result = make_triangle(0, 0, 10, 0, 5, 10)
    assert 'points="0,0 10,0 5,10"' in result

def test_make_triangle_default_fill():
    from make_triangle import make_triangle
    result = make_triangle(0, 0, 10, 0, 5, 10)
    assert 'fill="none"' in result

def test_make_triangle_custom_fill():
    from make_triangle import make_triangle
    result = make_triangle(0, 0, 10, 0, 5, 10, fill="red")
    assert 'fill="red"' in result

def test_make_triangle_custom_stroke():
    from make_triangle import make_triangle
    result = make_triangle(0, 0, 10, 0, 5, 10, stroke="blue")
    assert 'stroke="blue"' in result


# ── make_rect ────────────────────────────────────────────────────────────────
def test_make_rect_tag():
    from make_rect import make_rect
    result = make_rect(0, 0, 100, 50)
    assert result.startswith("<rect")

def test_make_rect_position():
    from make_rect import make_rect
    result = make_rect(10, 20, 100, 50)
    assert 'x="10"' in result
    assert 'y="20"' in result

def test_make_rect_size():
    from make_rect import make_rect
    result = make_rect(0, 0, 100, 50)
    assert 'width="100"' in result
    assert 'height="50"' in result

def test_make_rect_default_fill():
    from make_rect import make_rect
    result = make_rect(0, 0, 100, 50)
    assert 'fill="none"' in result

def test_make_rect_custom_fill():
    from make_rect import make_rect
    result = make_rect(0, 0, 100, 50, fill="blue")
    assert 'fill="blue"' in result

def test_make_rect_float_coords():
    from make_rect import make_rect
    result = make_rect(10.5, 20, 100, 50)
    assert 'x="10.5"' in result
    assert 'y="20"' in result


# ── make_circle ──────────────────────────────────────────────────────────────
def test_make_circle_tag():
    from make_circle import make_circle
    result = make_circle(50, 50, 30)
    assert result.startswith("<circle")

def test_make_circle_center():
    from make_circle import make_circle
    result = make_circle(50, 50, 30)
    assert 'cx="50"' in result
    assert 'cy="50"' in result

def test_make_circle_radius():
    from make_circle import make_circle
    result = make_circle(50, 50, 30)
    assert 'r="30"' in result

def test_make_circle_default_fill():
    from make_circle import make_circle
    result = make_circle(50, 50, 30)
    assert 'fill="none"' in result

def test_make_circle_custom_fill():
    from make_circle import make_circle
    result = make_circle(50, 50, 30, fill="red")
    assert 'fill="red"' in result

def test_make_circle_float_radius():
    from make_circle import make_circle
    result = make_circle(0, 0, 2.5)
    assert 'r="2.5"' in result


# ── make_text ────────────────────────────────────────────────────────────────
def test_make_text_tag():
    from make_text import make_text
    result = make_text(10, 20, "Hello")
    assert result.startswith("<text")
    assert result.endswith("</text>")

def test_make_text_position():
    from make_text import make_text
    result = make_text(10, 20, "Hello")
    assert 'x="10"' in result
    assert 'y="20"' in result

def test_make_text_content():
    from make_text import make_text
    result = make_text(10, 20, "Hello")
    assert ">Hello<" in result

def test_make_text_default_font_size():
    from make_text import make_text
    result = make_text(10, 20, "Hello")
    assert 'font-size="12"' in result

def test_make_text_custom_font_size():
    from make_text import make_text
    result = make_text(10, 20, "Hello", font_size=16)
    assert 'font-size="16"' in result

def test_make_text_default_fill():
    from make_text import make_text
    result = make_text(10, 20, "Hello")
    assert 'fill="black"' in result

def test_make_text_custom_fill():
    from make_text import make_text
    result = make_text(10, 20, "Hello", fill="red")
    assert 'fill="red"' in result


# ── make_group ───────────────────────────────────────────────────────────────
def test_make_group_empty():
    from make_group import make_group
    result = make_group([])
    assert result == "<g></g>"

def test_make_group_single_child():
    from make_group import make_group
    result = make_group(["<circle/>"])
    assert result == "<g><circle/></g>"

def test_make_group_multiple_children():
    from make_group import make_group
    result = make_group(["<circle/>", "<rect/>"])
    assert result == "<g><circle/><rect/></g>"

def test_make_group_with_transform():
    from make_group import make_group
    result = make_group(["<circle/>"], transform="translate(10,20)")
    assert 'transform="translate(10,20)"' in result
    assert result.startswith("<g")

def test_make_group_no_transform_attr_when_empty():
    from make_group import make_group
    result = make_group([])
    assert "transform" not in result


# ── make_labeled_group ───────────────────────────────────────────────────────
def test_make_labeled_group_contains_children():
    from make_labeled_group import make_labeled_group
    result = make_labeled_group(["<circle/>"], "label", 0, 10)
    assert "<circle/>" in result

def test_make_labeled_group_contains_label():
    from make_labeled_group import make_labeled_group
    result = make_labeled_group([], "My Label", 5, 15)
    assert "My Label" in result

def test_make_labeled_group_has_text_element():
    from make_labeled_group import make_labeled_group
    result = make_labeled_group([], "test", 0, 20)
    assert "<text" in result

def test_make_labeled_group_wrapped_in_g():
    from make_labeled_group import make_labeled_group
    result = make_labeled_group(["<circle/>"], "label", 0, 10)
    assert result.startswith("<g")
    assert result.endswith("</g>")


# ── make_grid ────────────────────────────────────────────────────────────────
def test_make_grid_contains_items():
    from make_grid import make_grid
    result = make_grid(["<a/>", "<b/>"], cols=2, cell_w=50, cell_h=50)
    assert "<a/>" in result
    assert "<b/>" in result

def test_make_grid_wrapped_in_g():
    from make_grid import make_grid
    result = make_grid(["<circle/>"], cols=1, cell_w=50, cell_h=50)
    assert result.startswith("<g")

def test_make_grid_uses_translate():
    from make_grid import make_grid
    result = make_grid(["<a/>", "<b/>", "<c/>"], cols=2, cell_w=50, cell_h=50)
    assert "translate" in result

def test_make_grid_three_items():
    from make_grid import make_grid
    result = make_grid(["<a/>", "<b/>", "<c/>"], cols=2, cell_w=50, cell_h=50)
    assert "<a/>" in result
    assert "<b/>" in result
    assert "<c/>" in result


# ── make_bar_chart ───────────────────────────────────────────────────────────
def test_make_bar_chart_three_bars():
    from make_bar_chart import make_bar_chart
    result = make_bar_chart([10, 20, 30], 0, 0, 90, 100)
    assert result.count("<rect") == 3

def test_make_bar_chart_single_bar():
    from make_bar_chart import make_bar_chart
    result = make_bar_chart([50], 0, 0, 100, 100)
    assert "<rect" in result

def test_make_bar_chart_wrapped():
    from make_bar_chart import make_bar_chart
    result = make_bar_chart([10, 20], 0, 0, 100, 100)
    assert result.startswith("<g")

def test_make_bar_chart_has_fill():
    from make_bar_chart import make_bar_chart
    result = make_bar_chart([10, 20, 30], 0, 0, 90, 100)
    assert "fill=" in result


# ── make_title ───────────────────────────────────────────────────────────────
def test_make_title_content():
    from make_title import make_title
    result = make_title("My Chart", 100, 20)
    assert "My Chart" in result

def test_make_title_is_text():
    from make_title import make_title
    result = make_title("My Chart", 100, 20)
    assert result.startswith("<text")

def test_make_title_font_size():
    from make_title import make_title
    result = make_title("My Chart", 100, 20, font_size=18)
    assert 'font-size="18"' in result

def test_make_title_bold():
    from make_title import make_title
    result = make_title("My Chart", 100, 20)
    assert 'font-weight="bold"' in result


# ── make_legend ──────────────────────────────────────────────────────────────
def test_make_legend_basic():
    from make_legend import make_legend
    result = make_legend([("Series A", "red")], 10, 10)
    assert "Series A" in result

def test_make_legend_wrapped_in_g():
    from make_legend import make_legend
    result = make_legend([("A", "red")], 0, 0)
    assert result.startswith("<g")

def test_make_legend_color_swatch():
    from make_legend import make_legend
    result = make_legend([("Label", "green")], 0, 0)
    assert "green" in result
    assert "<rect" in result

def test_make_legend_multiple_items():
    from make_legend import make_legend
    result = make_legend([("A", "red"), ("B", "blue")], 0, 0)
    assert "A" in result
    assert "B" in result
    assert result.count("<rect") == 2


# ── make_svg ─────────────────────────────────────────────────────────────────
def test_make_svg_tag():
    from make_svg import make_svg
    result = make_svg(200, 100, [])
    assert result.startswith("<svg")
    assert result.endswith("</svg>")

def test_make_svg_dimensions():
    from make_svg import make_svg
    result = make_svg(200, 100, [])
    assert 'width="200"' in result
    assert 'height="100"' in result

def test_make_svg_xmlns():
    from make_svg import make_svg
    result = make_svg(200, 100, [])
    assert "xmlns=" in result

def test_make_svg_children():
    from make_svg import make_svg
    result = make_svg(200, 100, ["<circle/>"])
    assert "<circle/>" in result

def test_make_svg_title():
    from make_svg import make_svg
    result = make_svg(200, 100, [], title="My SVG")
    assert "<title>My SVG</title>" in result

def test_make_svg_no_title_tag_when_empty():
    from make_svg import make_svg
    result = make_svg(200, 100, [], title="")
    assert "<title>" not in result


# ── make_line ────────────────────────────────────────────────────────────────
def test_make_line_tag():
    from make_line import make_line
    result = make_line(0, 0, 100, 100)
    assert result.startswith("<line")

def test_make_line_coords():
    from make_line import make_line
    result = make_line(0, 0, 100, 100)
    assert 'x1="0"' in result
    assert 'y1="0"' in result
    assert 'x2="100"' in result
    assert 'y2="100"' in result

def test_make_line_default_stroke():
    from make_line import make_line
    result = make_line(0, 0, 100, 100)
    assert 'stroke="black"' in result

def test_make_line_custom_stroke():
    from make_line import make_line
    result = make_line(0, 0, 100, 100, stroke="red")
    assert 'stroke="red"' in result

def test_make_line_stroke_width():
    from make_line import make_line
    result = make_line(0, 0, 100, 100, stroke_width=3)
    assert 'stroke-width="3"' in result


# ── make_ellipse ─────────────────────────────────────────────────────────────
def test_make_ellipse_tag():
    from make_ellipse import make_ellipse
    result = make_ellipse(50, 50, 30, 20)
    assert result.startswith("<ellipse")

def test_make_ellipse_center():
    from make_ellipse import make_ellipse
    result = make_ellipse(50, 50, 30, 20)
    assert 'cx="50"' in result
    assert 'cy="50"' in result

def test_make_ellipse_radii():
    from make_ellipse import make_ellipse
    result = make_ellipse(50, 50, 30, 20)
    assert 'rx="30"' in result
    assert 'ry="20"' in result

def test_make_ellipse_default_fill():
    from make_ellipse import make_ellipse
    result = make_ellipse(50, 50, 30, 20)
    assert 'fill="none"' in result

def test_make_ellipse_custom_fill():
    from make_ellipse import make_ellipse
    result = make_ellipse(50, 50, 30, 20, fill="yellow")
    assert 'fill="yellow"' in result


# ── make_path ────────────────────────────────────────────────────────────────
def test_make_path_tag():
    from make_path import make_path
    result = make_path("M 0,0 L 10,10 Z")
    assert result.startswith("<path")

def test_make_path_d_attr():
    from make_path import make_path
    result = make_path("M 0,0 L 10,10 Z")
    assert 'd="M 0,0 L 10,10 Z"' in result

def test_make_path_default_fill():
    from make_path import make_path
    result = make_path("M 0,0 L 10,10")
    assert 'fill="none"' in result

def test_make_path_custom_fill():
    from make_path import make_path
    result = make_path("M 0,0 L 10,10 Z", fill="red")
    assert 'fill="red"' in result

def test_make_path_custom_stroke():
    from make_path import make_path
    result = make_path("M 0,0 L 10,10", stroke="blue")
    assert 'stroke="blue"' in result


# ── make_comment ─────────────────────────────────────────────────────────────
def test_make_comment_basic():
    from make_comment import make_comment
    result = make_comment("hello world")
    assert result == "<!-- hello world -->"

def test_make_comment_starts_ends():
    from make_comment import make_comment
    result = make_comment("test")
    assert result.startswith("<!--")
    assert result.endswith("-->")

def test_make_comment_empty():
    from make_comment import make_comment
    result = make_comment("")
    assert result.startswith("<!--")
    assert result.endswith("-->")

def test_make_comment_preserves_text():
    from make_comment import make_comment
    result = make_comment("generated by agent")
    assert "generated by agent" in result
