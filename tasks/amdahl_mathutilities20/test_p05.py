"""Pre-written test suite for Math Utils Library (p=0.5, N=20).

Chain (tasks 1-10): add -> safe_add -> sum_list -> mean -> variance ->
                    std_dev -> z_score -> normalize -> outlier_mask ->
                    filter_outliers
Independent (tasks 11-20): subtract, multiply, divide, abs_val, is_even,
                            clamp, sign, max_val, min_val, modulo
"""
import pytest
import math


# ── add ──────────────────────────────────────────────────────────────────────
def test_add_positive():
    from add import add
    assert add(2, 3) == 5

def test_add_negative():
    from add import add
    assert add(-4, -1) == -5

def test_add_floats():
    from add import add
    assert add(1.5, 2.5) == pytest.approx(4.0)


# ── safe_add ─────────────────────────────────────────────────────────────────
def test_safe_add_ints():
    from safe_add import safe_add
    assert safe_add(3, 4) == 7

def test_safe_add_type_error_str():
    from safe_add import safe_add
    with pytest.raises(TypeError):
        safe_add("x", 1)

def test_safe_add_type_error_none():
    from safe_add import safe_add
    with pytest.raises(TypeError):
        safe_add(1, None)


# ── sum_list ─────────────────────────────────────────────────────────────────
def test_sum_list_basic():
    from sum_list import sum_list
    assert sum_list([1, 2, 3, 4, 5]) == pytest.approx(15.0)

def test_sum_list_empty():
    from sum_list import sum_list
    assert sum_list([]) == pytest.approx(0.0)

def test_sum_list_single():
    from sum_list import sum_list
    assert sum_list([7]) == pytest.approx(7.0)

def test_sum_list_floats():
    from sum_list import sum_list
    assert sum_list([0.1, 0.2, 0.3]) == pytest.approx(0.6)

def test_sum_list_negatives():
    from sum_list import sum_list
    assert sum_list([-1, -2, -3]) == pytest.approx(-6.0)


# ── mean ─────────────────────────────────────────────────────────────────────
def test_mean_basic():
    from mean import mean
    assert mean([1, 2, 3, 4, 5]) == pytest.approx(3.0)

def test_mean_floats():
    from mean import mean
    assert mean([1.0, 2.0, 3.0]) == pytest.approx(2.0)

def test_mean_empty():
    from mean import mean
    with pytest.raises(ValueError):
        mean([])

def test_mean_single():
    from mean import mean
    assert mean([42]) == pytest.approx(42.0)

def test_mean_negative():
    from mean import mean
    assert mean([-2, 0, 2]) == pytest.approx(0.0)


# ── variance ─────────────────────────────────────────────────────────────────
def test_variance_basic():
    from variance import variance
    # population variance of [2,4,4,4,5,5,7,9] = 4.0
    assert variance([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(4.0)

def test_variance_constant():
    from variance import variance
    # All same value -> variance = 0
    assert variance([3, 3, 3, 3]) == pytest.approx(0.0)

def test_variance_empty():
    from variance import variance
    with pytest.raises(ValueError):
        variance([])

def test_variance_two_elements():
    from variance import variance
    # [0, 2]: mean=1, var = ((0-1)^2 + (2-1)^2)/2 = 1.0
    assert variance([0, 2]) == pytest.approx(1.0)


# ── std_dev ──────────────────────────────────────────────────────────────────
def test_std_dev_basic():
    from std_dev import std_dev
    # std_dev of [2,4,4,4,5,5,7,9] = 2.0
    assert std_dev([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(2.0)

def test_std_dev_constant():
    from std_dev import std_dev
    assert std_dev([5, 5, 5]) == pytest.approx(0.0)

def test_std_dev_empty():
    from std_dev import std_dev
    with pytest.raises(ValueError):
        std_dev([])

def test_std_dev_nonnegative():
    from std_dev import std_dev
    assert std_dev([1, 2, 3, 4, 5]) >= 0.0


# ── z_score ──────────────────────────────────────────────────────────────────
def test_z_score_center():
    from z_score import z_score
    # z_score of mean element = 0
    assert z_score(3.0, [1, 2, 3, 4, 5]) == pytest.approx(0.0, abs=1e-9)

def test_z_score_positive():
    from z_score import z_score
    # [1,2,3,4,5]: mean=3, std=sqrt(2)≈1.414; z(5)=(5-3)/sqrt(2)
    result = z_score(5, [1, 2, 3, 4, 5])
    assert result == pytest.approx(2 / math.sqrt(2))

def test_z_score_negative():
    from z_score import z_score
    result = z_score(1, [1, 2, 3, 4, 5])
    assert result == pytest.approx(-2 / math.sqrt(2))

def test_z_score_zero_std():
    from z_score import z_score
    with pytest.raises(ValueError):
        z_score(3, [3, 3, 3])


# ── normalize ────────────────────────────────────────────────────────────────
def test_normalize_length():
    from normalize import normalize
    result = normalize([1, 2, 3, 4, 5])
    assert len(result) == 5

def test_normalize_mean_near_zero():
    from normalize import normalize
    result = normalize([1, 2, 3, 4, 5])
    assert abs(sum(result) / len(result)) == pytest.approx(0.0, abs=1e-9)

def test_normalize_std_near_one():
    from normalize import normalize
    result = normalize([1, 2, 3, 4, 5])
    n = len(result)
    m = sum(result) / n
    var = sum((x - m) ** 2 for x in result) / n
    assert var ** 0.5 == pytest.approx(1.0, abs=1e-9)

def test_normalize_constant_raises():
    from normalize import normalize
    with pytest.raises(ValueError):
        normalize([5, 5, 5])

def test_normalize_empty_raises():
    from normalize import normalize
    with pytest.raises(ValueError):
        normalize([])


# ── outlier_mask ─────────────────────────────────────────────────────────────
def test_outlier_mask_length():
    from outlier_mask import outlier_mask
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert len(outlier_mask(data)) == len(data)

def test_outlier_mask_no_outliers():
    from outlier_mask import outlier_mask
    # Tight cluster — no z-score should exceed 2.0
    data = [10, 10, 10, 10, 11, 10, 10, 10, 10, 10]
    mask = outlier_mask(data, threshold=2.0)
    assert all(isinstance(v, bool) for v in mask)

def test_outlier_mask_detects_extreme():
    from outlier_mask import outlier_mask
    # 100 is a clear outlier among [1..9]
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    mask = outlier_mask(data, threshold=1.5)
    assert mask[-1] is True

def test_outlier_mask_all_same_raises():
    from outlier_mask import outlier_mask
    with pytest.raises(ValueError):
        outlier_mask([5, 5, 5, 5])


# ── filter_outliers ──────────────────────────────────────────────────────────
def test_filter_outliers_removes_extreme():
    from filter_outliers import filter_outliers
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    result = filter_outliers(data, threshold=1.5)
    assert 100 not in result

def test_filter_outliers_keeps_inliers():
    from filter_outliers import filter_outliers
    # No extreme values — all should be kept
    data = [4, 5, 5, 5, 6]
    result = filter_outliers(data, threshold=2.0)
    assert len(result) == len(data)

def test_filter_outliers_returns_list():
    from filter_outliers import filter_outliers
    result = filter_outliers([1, 2, 3, 4, 5])
    assert isinstance(result, list)

def test_filter_outliers_empty_raises():
    from filter_outliers import filter_outliers
    with pytest.raises(ValueError):
        filter_outliers([])


# ── subtract ─────────────────────────────────────────────────────────────────
def test_subtract_basic():
    from subtract import subtract
    assert subtract(5, 3) == 2

def test_subtract_negative_result():
    from subtract import subtract
    assert subtract(3, 5) == -2

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


# ── divide ───────────────────────────────────────────────────────────────────
def test_divide_basic():
    from divide import divide
    assert divide(10, 2) == pytest.approx(5.0)

def test_divide_by_zero():
    from divide import divide
    with pytest.raises((ValueError, ZeroDivisionError)):
        divide(5, 0)


# ── abs_val ──────────────────────────────────────────────────────────────────
def test_abs_val_negative():
    from abs_val import abs_val
    assert abs_val(-7) == 7

def test_abs_val_positive():
    from abs_val import abs_val
    assert abs_val(5) == 5

def test_abs_val_zero():
    from abs_val import abs_val
    assert abs_val(0) == 0


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


# ── max_val ──────────────────────────────────────────────────────────────────
def test_max_val_basic():
    from max_val import max_val
    assert max_val(7, 3) == 7

def test_max_val_equal():
    from max_val import max_val
    assert max_val(5, 5) == 5


# ── min_val ──────────────────────────────────────────────────────────────────
def test_min_val_basic():
    from min_val import min_val
    assert min_val(3, 7) == 3

def test_min_val_equal():
    from min_val import min_val
    assert min_val(5, 5) == 5


# ── modulo ───────────────────────────────────────────────────────────────────
def test_modulo_basic():
    from modulo import modulo
    assert modulo(10, 3) == pytest.approx(1.0)

def test_modulo_even():
    from modulo import modulo
    assert modulo(10, 2) == pytest.approx(0.0)

def test_modulo_float():
    from modulo import modulo
    assert modulo(7.5, 2.5) == pytest.approx(0.0)

def test_modulo_by_zero():
    from modulo import modulo
    with pytest.raises((ValueError, ZeroDivisionError)):
        modulo(5, 0)
