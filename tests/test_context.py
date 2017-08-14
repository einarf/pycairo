import cairo
import pytest


@pytest.fixture
def context():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 42, 42)
    return cairo.Context(surface)


def test_cmp_hash(context):
    other = cairo.Context(context.get_target())
    assert context != other
    hash(context)


def test_get_antialias(context):
    assert context.get_antialias() == cairo.Antialias.DEFAULT
    assert isinstance(context.get_antialias(), cairo.Antialias)


def test_get_fill_rule(context):
    assert context.get_fill_rule() == cairo.FillRule.WINDING
    assert isinstance(context.get_fill_rule(), cairo.FillRule)


def test_get_line_cap(context):
    assert context.get_line_cap() == cairo.LineCap.BUTT
    assert isinstance(context.get_line_cap(), cairo.LineCap)


def test_get_line_join(context):
    assert context.get_line_join() == cairo.LineJoin.MITER
    assert isinstance(context.get_line_join(), cairo.LineJoin)


def test_get_operator(context):
    assert context.get_operator() == cairo.Operator.OVER
    assert isinstance(context.get_operator(), cairo.Operator)


def test_show_text_glyphs():
    surface = cairo.PDFSurface(None, 300, 300)
    context = cairo.Context(surface)
    context.scale(300, 300)
    context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_NORMAL)
    context.set_font_size(0.08)
    context.set_line_width(0.09)
    sf = context.get_scaled_font()
    glyphs, clusters, flags = sf.text_to_glyphs(0.5, 0.5, "foobar")
    context.show_text_glyphs("foobar", glyphs, clusters, flags)

    glyphs, clusters, flags = sf.text_to_glyphs(0.5, 0.5, "")
    context.show_text_glyphs("", glyphs, clusters, flags)

    with pytest.raises(TypeError):
        context.show_text_glyphs(object(), glyphs, clusters, flags)

    with pytest.raises(TypeError):
        context.show_text_glyphs("", [object()], clusters, flags)

    with pytest.raises(TypeError):
        context.show_text_glyphs("", object(), clusters, flags)

    with pytest.raises(TypeError):
        context.show_text_glyphs("", glyphs, [object()], flags)

    with pytest.raises(TypeError):
        context.show_text_glyphs("", glyphs, object(), flags)


def test_append_path(context):
    context.line_to(1, 2)
    p = context.copy_path()
    context.new_path()
    context.append_path(p)
    assert str(context.copy_path()) == str(p)


def test_arc(context):
    assert not list(context.copy_path())
    context.arc(0, 0, 0, 0, 0)
    assert list(context.copy_path())


def test_arc_negative(context):
    assert not list(context.copy_path())
    context.arc_negative(0, 0, 0, 0, 0)
    assert list(context.copy_path())


def test_clip_extents(context):
    assert context.clip_extents() == (0.0, 0.0, 42.0, 42.0)


def test_in_clip():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    context = cairo.Context(surface)
    assert context.in_clip(50, 50)
    context.clip()
    assert not context.in_clip(50, 50)
    context.reset_clip()
    assert context.in_clip(50, 50)

    with pytest.raises(TypeError):
        context.in_clip(None, None)


def test_device_to_user(context):
    assert context.device_to_user(0, 0) == (0, 0)
    with pytest.raises(TypeError):
        context.device_to_user(None, None)


def test_device_to_user_distance(context):
    assert context.device_to_user_distance(0, 0) == (0, 0)
    with pytest.raises(TypeError):
        context.device_to_user_distance(None, None)


def test_fill_extents(context):
    context.line_to(1, 1)
    context.line_to(1, 0)
    context.line_to(0, 0)
    context.line_to(0, 1)
    context.line_to(1, 1)
    assert context.fill_extents() == (0, 0, 1, 1)


def test_curve_to(context):
    with pytest.raises(TypeError):
        context.curve_to(1, 2, 3, 4, 5, object())


def test_set_get_dash(context):
    assert context.get_dash() == ((), 0)
    assert context.get_dash_count() == 0

    context.set_dash([0, 1, 2, 3], 10)
    assert context.get_dash() == ((0.0, 1.0, 2.0, 3.0), 4.0)
    assert context.get_dash_count() == 4


def test_glyph_extents(context):
    with pytest.raises(TypeError):
        context.glyph_extents(None)


def test_current_point(context):
    assert not context.has_current_point()
    assert context.get_current_point() == (0, 0)
    context.move_to(10, 10)
    assert context.has_current_point()
    assert context.get_current_point() == (10, 10)


def test_in_fill(context):
    assert not context.in_fill(0.1, 0.1)
    with pytest.raises(TypeError):
        context.in_fill(0.1, object())


def test_line_to(context):
    with pytest.raises(TypeError):
        context.line_to(0.1, object())


def test_mask(context):
    pattern = cairo.SolidPattern(0, 0, 0)
    context.mask(pattern)
    with pytest.raises(TypeError):
        context.mask(object())


def test_mask_surface(context):
    context.mask_surface(context.get_target(), 0, 0)
    with pytest.raises(TypeError):
        context.mask_surface(object(), 0, 0)


def test_paint_with_alpha(context):
    context.paint_with_alpha(0.5)
    with pytest.raises(TypeError):
        context.paint_with_alpha(object())


def test_path_extents(context):
    context.line_to(1, 1)
    context.line_to(1, 0)
    context.line_to(0, 0)
    context.line_to(0, 1)
    context.line_to(1, 1)
    assert context.path_extents() == (0.0, 0.0, 1.0, 1.0)


def test_push_pop_group(context):
    context.push_group()
    context.pop_group()

    context.push_group()
    context.pop_group_to_source()

    context.push_group_with_content(cairo.Content.COLOR)
    context.pop_group()

    with pytest.raises(cairo.Error):
        context.pop_group()


def test_rectangle(context):
    context.rectangle(1, 2, 4, 5)
    assert context.path_extents() == (1.0, 2.0, 5.0, 7.0)


def test_rel_curve_to(context):
    context.line_to(0, 0)
    context.rel_curve_to(0, 0, 0, 0, 0, 0)
    with pytest.raises(TypeError):
        context.rel_curve_to(object(), 0, 0, 0, 0, 0)


def test_rel_line_to(context):
    context.line_to(0, 0)
    context.rel_line_to(1, 1)
    with pytest.raises(TypeError):
        context.rel_line_to(object(), 0)


def test_rel_move_to(context):
    context.line_to(0, 0)
    context.rel_move_to(1, 1)
    with pytest.raises(TypeError):
        context.rel_move_to(object(), 0)


def test_save_restore(context):
    context.save()
    context.restore()


def test_scale(context):
    context.scale(2, 2)
    with pytest.raises(TypeError):
        context.scale(object(), 0)


def test_select_font_face(context):
    context.select_font_face("")
    with pytest.raises(TypeError):
        context.select_font_face(None)


def test_set_antialias(context):
    context.set_antialias(cairo.Antialias.SUBPIXEL)
    assert context.get_antialias() == cairo.Antialias.SUBPIXEL


def test_set_fill_rule(context):
    context.set_fill_rule(cairo.FillRule.EVEN_ODD)
    assert context.get_fill_rule() == cairo.FillRule.EVEN_ODD


def test_set_font_face(context):
    assert context.get_font_face()
    context.set_font_face(None)
    assert context.get_font_face()
    ff = context.get_font_face()
    context.set_font_face(ff)
    assert context.get_font_face() == ff


def test_set_font_matrix(context):
    m = cairo.Matrix()
    context.set_font_matrix(m)
    assert context.get_font_matrix() == m


def test_set_font_options(context):
    context.set_font_options(context.get_font_options())


def test_set_font_size(context):
    context.set_font_size(42)
    assert context.get_font_matrix() == cairo.Matrix(42, 0, 0, 42, 0, 0)
    with pytest.raises(TypeError):
        context.set_font_size(object())


def test_simple(context):
    context.clip_preserve()
    context.copy_page()
    context.copy_path_flat()
    context.fill()
    context.fill_preserve()
    context.font_extents()
    context.identity_matrix()
    context.new_sub_path()

    assert context.get_dash_count() == 0
    assert isinstance(context.get_font_matrix(), cairo.Matrix)

    assert context.get_group_target()
    context.get_line_width()

    assert isinstance(context.get_tolerance(), float)
    assert isinstance(context.get_miter_limit(), float)
    assert isinstance(context.get_matrix(), cairo.Matrix)
