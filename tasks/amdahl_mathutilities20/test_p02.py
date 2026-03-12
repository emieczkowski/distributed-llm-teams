"""Pre-written test suite for Robust Statistics Library (p=0.2, N=20).

Chain (tasks 1-16): add -> safe_add -> sum_list -> mean -> variance ->
                    std_dev -> z_score -> normalize -> outlier_mask ->
                    filter_outliers -> trimmed_mean -> trimmed_variance ->
                    trimmed_std -> trimmed_z_score -> trimmed_normalize ->
                    normality_score
Independent (tasks 17-20): abs_val, is_even, sign, clamp
"""
import pytest
import math


# ── add ──────────────────────────────────────────────────────────────────────
def test_add_positive():
    from add import add
    assert add(2, 3) == 5

def test_add_floats():
    from add import add
    assert add(1.5, 2.5) == pytest.approx(4.0)

def test_add_negative():
    from add import add
    assert add(-4, -1) == -5


# ── safe_add ─────────────────────────────────────────────────────────────────
def test_safe_add_ints():
    from safe_add import safe_add
    assert safe_add(3, 4) == 7

def test_safe_add_type_error():
    from safe_add import safe_add
    with pytest.raises(TypeError):
        safe_add("x", 1)

def test_safe_add_none_error():
    from safe_add import safe_add
    with pytest.raises(TypeError):
        safe_add(None, 1)


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


# ── mean ─────────────────────────────────────────────────────────────────────
def test_mean_basic():
    from mean import mean
    assert mean([1, 2, 3, 4, 5]) == pytest.approx(3.0)

def test_mean_empty():
    from mean import mean
    with pytest.raises(ValueError):
        mean([])

def test_mean_single():
    from mean import mean
    assert mean([42]) == pytest.approx(42.0)


# ── variance ─────────────────────────────────────────────────────────────────
def test_variance_basic():
    from variance import variance
    # population variance of [2,4,4,4,5,5,7,9] = 4.0
    assert variance([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(4.0)

def test_variance_constant():
    from variance import variance
    assert variance([3, 3, 3]) == pytest.approx(0.0)

def test_variance_empty():
    from variance import variance
    with pytest.raises(ValueError):
        variance([])


# ── std_dev ──────────────────────────────────────────────────────────────────
def test_std_dev_basic():
    from std_dev import std_dev
    assert std_dev([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(2.0)

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
    assert z_score(3.0, [1, 2, 3, 4, 5]) == pytest.approx(0.0, abs=1e-9)

def test_z_score_known():
    from z_score import z_score
    # [1,2,3,4,5]: mean=3, pop_std=sqrt(2); z(5) = 2/sqrt(2)
    assert z_score(5, [1, 2, 3, 4, 5]) == pytest.approx(2 / math.sqrt(2))

def test_z_score_zero_std_raises():
    from z_score import z_score
    with pytest.raises(ValueError):
        z_score(3, [3, 3, 3])


# ── normalize ────────────────────────────────────────────────────────────────
def test_normalize_length():
    from normalize import normalize
    assert len(normalize([1, 2, 3, 4, 5])) == 5

def test_normalize_mean_zero():
    from normalize import normalize
    result = normalize([1, 2, 3, 4, 5])
    assert abs(sum(result) / len(result)) == pytest.approx(0.0, abs=1e-9)

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

def test_outlier_mask_detects_extreme():
    from outlier_mask import outlier_mask
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    assert outlier_mask(data, threshold=1.5)[-1] is True

def test_outlier_mask_returns_bools():
    from outlier_mask import outlier_mask
    data = [1, 2, 3, 4, 5]
    mask = outlier_mask(data)
    assert all(isinstance(v, bool) for v in mask)


# ── filter_outliers ──────────────────────────────────────────────────────────
def test_filter_outliers_removes_extreme():
    from filter_outliers import filter_outliers
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    assert 100 not in filter_outliers(data, threshold=1.5)

def test_filter_outliers_returns_list():
    from filter_outliers import filter_outliers
    assert isinstance(filter_outliers([1, 2, 3, 4, 5]), list)

def test_filter_outliers_empty_raises():
    from filter_outliers import filter_outliers
    with pytest.raises(ValueError):
        filter_outliers([])


# ── trimmed_mean ─────────────────────────────────────────────────────────────
def test_trimmed_mean_no_outliers():
    from trimmed_mean import trimmed_mean
    # tight cluster — trimmed_mean ≈ regular mean
    data = [4, 5, 5, 5, 5, 5, 6]
    result = trimmed_mean(data, threshold=2.0)
    assert result == pytest.approx(5.0, abs=0.5)

def test_trimmed_mean_removes_extreme():
    from trimmed_mean import trimmed_mean
    # 100 is an outlier; trimmed mean should be much less than regular mean
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
    regular_mean = sum(data) / len(data)
    t_mean = trimmed_mean(data, threshold=1.5)
    assert t_mean < regular_mean

def test_trimmed_mean_returns_float():
    from trimmed_mean import trimmed_mean
    result = trimmed_mean([1, 2, 3, 4, 5])
    assert isinstance(result, (int, float))


# ── trimmed_variance ─────────────────────────────────────────────────────────
def test_trimmed_variance_nonnegative():
    from trimmed_variance import trimmed_variance
    result = trimmed_variance([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert result >= 0.0

def test_trimmed_variance_constant_after_trim():
    from trimmed_variance import trimmed_variance
    # If all non-outlier values are identical, variance = 0
    # [5, 5, 5, 5, 100]: after removing 100, all 5s remain
    data = [5, 5, 5, 5, 100]
    result = trimmed_variance(data, threshold=1.5)
    assert result == pytest.approx(0.0, abs=1e-9)

def test_trimmed_variance_empty_raises():
    from trimmed_variance import trimmed_variance
    with pytest.raises(ValueError):
        trimmed_variance([])


# ── trimmed_std ──────────────────────────────────────────────────────────────
def test_trimmed_std_nonnegative():
    from trimmed_std import trimmed_std
    assert trimmed_std([1, 2, 3, 4, 5]) >= 0.0

def test_trimmed_std_sqrt_of_variance():
    from trimmed_std import trimmed_std
    from trimmed_variance import trimmed_variance
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert trimmed_std(data) == pytest.approx(trimmed_variance(data) ** 0.5)

def test_trimmed_std_empty_raises():
    from trimmed_std import trimmed_std
    with pytest.raises(ValueError):
        trimmed_std([])


# ── trimmed_z_score ──────────────────────────────────────────────────────────
def test_trimmed_z_score_returns_float():
    from trimmed_z_score import trimmed_z_score
    # Use data where no outliers are trimmed
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = trimmed_z_score(5, data)
    assert isinstance(result, (int, float))

def test_trimmed_z_score_zero_std_raises():
    from trimmed_z_score import trimmed_z_score
    # After trimming, if all remaining values are identical -> std=0
    data = [5, 5, 5, 5, 100]
    with pytest.raises(ValueError):
        trimmed_z_score(5, data, threshold=1.5)

def test_trimmed_z_score_mean_element():
    from trimmed_z_score import trimmed_z_score
    # For symmetric data with no outliers, trimmed_z_score of the mean ≈ 0
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    from trimmed_mean import trimmed_mean
    mu = trimmed_mean(data)
    result = trimmed_z_score(mu, data)
    assert result == pytest.approx(0.0, abs=1e-9)


# ── trimmed_normalize ────────────────────────────────────────────────────────
def test_trimmed_normalize_length():
    from trimmed_normalize import trimmed_normalize
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert len(trimmed_normalize(data)) == len(data)

def test_trimmed_normalize_returns_list():
    from trimmed_normalize import trimmed_normalize
    result = trimmed_normalize([1, 2, 3, 4, 5])
    assert isinstance(result, list)

def test_trimmed_normalize_empty_raises():
    from trimmed_normalize import trimmed_normalize
    with pytest.raises(ValueError):
        trimmed_normalize([])


# ── normality_score ──────────────────────────────────────────────────────────
def test_normality_score_nonnegative():
    from normality_score import normality_score
    data = list(range(1, 21))
    assert normality_score(data) >= 0.0

def test_normality_score_returns_float():
    from normality_score import normality_score
    result = normality_score([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert isinstance(result, (int, float))

def test_normality_score_empty_raises():
    from normality_score import normality_score
    with pytest.raises(ValueError):
        normality_score([])

def test_normality_score_near_normal_lower_than_extreme():
    from normality_score import normality_score
    # A roughly symmetric distribution should score lower than a highly skewed one
    symmetric = [1, 2, 3, 3, 3, 4, 4, 4, 5, 6]
    skewed = [1, 1, 1, 1, 1, 1, 1, 1, 1, 100]
    assert normality_score(symmetric) <= normality_score(skewed)


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
