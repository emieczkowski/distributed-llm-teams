"""Pre-written test suite for Math Utils Library (p=0.9, N=20).

Functions: add, safe_add, subtract, multiply, divide, abs_val, is_even,
           clamp, sign, max_val, min_val, square, cube, reciprocal,
           is_positive, is_negative, is_zero, negate, double, half
"""
import pytest


# ── add ──────────────────────────────────────────────────────────────────────
def test_add_positive():
    from add import add
    assert add(2, 3) == 5

def test_add_negative():
    from add import add
    assert add(-4, -1) == -5

def test_add_zero():
    from add import add
    assert add(0, 7) == 7

def test_add_floats():
    from add import add
    assert add(1.5, 2.5) == pytest.approx(4.0)

def test_add_mixed():
    from add import add
    assert add(-3, 3) == 0


# ── safe_add ─────────────────────────────────────────────────────────────────
def test_safe_add_ints():
    from safe_add import safe_add
    assert safe_add(2, 3) == 5

def test_safe_add_floats():
    from safe_add import safe_add
    assert safe_add(1.5, 2.5) == pytest.approx(4.0)

def test_safe_add_mixed_numeric():
    from safe_add import safe_add
    assert safe_add(2, 0.5) == pytest.approx(2.5)

def test_safe_add_type_error_str():
    from safe_add import safe_add
    with pytest.raises(TypeError):
        safe_add("a", 1)

def test_safe_add_type_error_none():
    from safe_add import safe_add
    with pytest.raises(TypeError):
        safe_add(1, None)

def test_safe_add_type_error_list():
    from safe_add import safe_add
    with pytest.raises(TypeError):
        safe_add([1], 2)


# ── subtract ─────────────────────────────────────────────────────────────────
def test_subtract_basic():
    from subtract import subtract
    assert subtract(5, 3) == 2

def test_subtract_negative_result():
    from subtract import subtract
    assert subtract(3, 5) == -2

def test_subtract_zero():
    from subtract import subtract
    assert subtract(7, 0) == 7

def test_subtract_floats():
    from subtract import subtract
    assert subtract(3.5, 1.5) == pytest.approx(2.0)


# ── multiply ─────────────────────────────────────────────────────────────────
def test_multiply_positive():
    from multiply import multiply
    assert multiply(3, 4) == 12

def test_multiply_negative():
    from multiply import multiply
    assert multiply(-2, 5) == -10

def test_multiply_zero():
    from multiply import multiply
    assert multiply(0, 100) == 0

def test_multiply_floats():
    from multiply import multiply
    assert multiply(2.5, 4.0) == pytest.approx(10.0)

def test_multiply_both_negative():
    from multiply import multiply
    assert multiply(-3, -4) == 12


# ── divide ───────────────────────────────────────────────────────────────────
def test_divide_basic():
    from divide import divide
    assert divide(10, 2) == pytest.approx(5.0)

def test_divide_floats():
    from divide import divide
    assert divide(7.5, 2.5) == pytest.approx(3.0)

def test_divide_negative():
    from divide import divide
    assert divide(-10, 2) == pytest.approx(-5.0)

def test_divide_fraction():
    from divide import divide
    assert divide(1, 3) == pytest.approx(1/3)

def test_divide_by_zero():
    from divide import divide
    with pytest.raises((ValueError, ZeroDivisionError)):
        divide(5, 0)


# ── abs_val ──────────────────────────────────────────────────────────────────
def test_abs_val_positive():
    from abs_val import abs_val
    assert abs_val(5) == 5

def test_abs_val_negative():
    from abs_val import abs_val
    assert abs_val(-7) == 7

def test_abs_val_zero():
    from abs_val import abs_val
    assert abs_val(0) == 0

def test_abs_val_float():
    from abs_val import abs_val
    assert abs_val(-3.14) == pytest.approx(3.14)


# ── is_even ──────────────────────────────────────────────────────────────────
def test_is_even_true():
    from is_even import is_even
    assert is_even(4) is True

def test_is_even_false():
    from is_even import is_even
    assert is_even(7) is False

def test_is_even_zero():
    from is_even import is_even
    assert is_even(0) is True

def test_is_even_negative_even():
    from is_even import is_even
    assert is_even(-2) is True

def test_is_even_negative_odd():
    from is_even import is_even
    assert is_even(-3) is False


# ── clamp ────────────────────────────────────────────────────────────────────
def test_clamp_below():
    from clamp import clamp
    assert clamp(-5, 0, 10) == 0

def test_clamp_above():
    from clamp import clamp
    assert clamp(15, 0, 10) == 10

def test_clamp_within():
    from clamp import clamp
    assert clamp(5, 0, 10) == 5

def test_clamp_at_lo():
    from clamp import clamp
    assert clamp(0, 0, 10) == 0

def test_clamp_at_hi():
    from clamp import clamp
    assert clamp(10, 0, 10) == 10

def test_clamp_float():
    from clamp import clamp
    assert clamp(10.5, 0.0, 10.0) == pytest.approx(10.0)


# ── sign ─────────────────────────────────────────────────────────────────────
def test_sign_positive():
    from sign import sign
    assert sign(5) == 1

def test_sign_negative():
    from sign import sign
    assert sign(-3) == -1

def test_sign_zero():
    from sign import sign
    assert sign(0) == 0

def test_sign_float_positive():
    from sign import sign
    assert sign(0.001) == 1

def test_sign_float_negative():
    from sign import sign
    assert sign(-0.001) == -1


# ── max_val ──────────────────────────────────────────────────────────────────
def test_max_val_first_larger():
    from max_val import max_val
    assert max_val(7, 3) == 7

def test_max_val_second_larger():
    from max_val import max_val
    assert max_val(3, 7) == 7

def test_max_val_equal():
    from max_val import max_val
    assert max_val(5, 5) == 5

def test_max_val_negative():
    from max_val import max_val
    assert max_val(-2, -8) == -2


# ── min_val ──────────────────────────────────────────────────────────────────
def test_min_val_first_smaller():
    from min_val import min_val
    assert min_val(3, 7) == 3

def test_min_val_second_smaller():
    from min_val import min_val
    assert min_val(7, 3) == 3

def test_min_val_equal():
    from min_val import min_val
    assert min_val(5, 5) == 5

def test_min_val_negative():
    from min_val import min_val
    assert min_val(-2, -8) == -8


# ── square ───────────────────────────────────────────────────────────────────
def test_square_positive():
    from square import square
    assert square(4) == 16

def test_square_negative():
    from square import square
    assert square(-3) == 9

def test_square_zero():
    from square import square
    assert square(0) == 0

def test_square_float():
    from square import square
    assert square(2.5) == pytest.approx(6.25)


# ── cube ─────────────────────────────────────────────────────────────────────
def test_cube_positive():
    from cube import cube
    assert cube(3) == 27

def test_cube_negative():
    from cube import cube
    assert cube(-2) == -8

def test_cube_zero():
    from cube import cube
    assert cube(0) == 0

def test_cube_float():
    from cube import cube
    assert cube(2.0) == pytest.approx(8.0)


# ── reciprocal ───────────────────────────────────────────────────────────────
def test_reciprocal_basic():
    from reciprocal import reciprocal
    assert reciprocal(4) == pytest.approx(0.25)

def test_reciprocal_negative():
    from reciprocal import reciprocal
    assert reciprocal(-2) == pytest.approx(-0.5)

def test_reciprocal_one():
    from reciprocal import reciprocal
    assert reciprocal(1) == pytest.approx(1.0)

def test_reciprocal_zero():
    from reciprocal import reciprocal
    with pytest.raises((ValueError, ZeroDivisionError)):
        reciprocal(0)


# ── is_positive ──────────────────────────────────────────────────────────────
def test_is_positive_true():
    from is_positive import is_positive
    assert is_positive(5) is True

def test_is_positive_false_negative():
    from is_positive import is_positive
    assert is_positive(-3) is False

def test_is_positive_zero():
    from is_positive import is_positive
    assert is_positive(0) is False

def test_is_positive_float():
    from is_positive import is_positive
    assert is_positive(0.001) is True


# ── is_negative ──────────────────────────────────────────────────────────────
def test_is_negative_true():
    from is_negative import is_negative
    assert is_negative(-5) is True

def test_is_negative_false_positive():
    from is_negative import is_negative
    assert is_negative(3) is False

def test_is_negative_zero():
    from is_negative import is_negative
    assert is_negative(0) is False

def test_is_negative_float():
    from is_negative import is_negative
    assert is_negative(-0.001) is True


# ── is_zero ──────────────────────────────────────────────────────────────────
def test_is_zero_true():
    from is_zero import is_zero
    assert is_zero(0) is True

def test_is_zero_false_positive():
    from is_zero import is_zero
    assert is_zero(1) is False

def test_is_zero_false_negative():
    from is_zero import is_zero
    assert is_zero(-1) is False

def test_is_zero_float():
    from is_zero import is_zero
    assert is_zero(0.0) is True


# ── negate ───────────────────────────────────────────────────────────────────
def test_negate_positive():
    from negate import negate
    assert negate(5) == -5

def test_negate_negative():
    from negate import negate
    assert negate(-3) == 3

def test_negate_zero():
    from negate import negate
    assert negate(0) == 0

def test_negate_float():
    from negate import negate
    assert negate(2.5) == pytest.approx(-2.5)


# ── double ───────────────────────────────────────────────────────────────────
def test_double_positive():
    from double import double
    assert double(5) == 10

def test_double_negative():
    from double import double
    assert double(-3) == -6

def test_double_zero():
    from double import double
    assert double(0) == 0

def test_double_float():
    from double import double
    assert double(2.5) == pytest.approx(5.0)


# ── half ─────────────────────────────────────────────────────────────────────
def test_half_even():
    from half import half
    assert half(10) == pytest.approx(5.0)

def test_half_odd():
    from half import half
    assert half(7) == pytest.approx(3.5)

def test_half_negative():
    from half import half
    assert half(-4) == pytest.approx(-2.0)

def test_half_zero():
    from half import half
    assert half(0) == pytest.approx(0.0)
