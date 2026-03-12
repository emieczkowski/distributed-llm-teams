"""Pre-written test suite for Sales Data Analysis Pipeline (p=0.9, N=20).

Chain (tasks 1-2): get_records -> remove_invalid
Independent (tasks 3-20): compute_line_revenue, total_units, average_price,
    max_units_record, min_price_record, distinct_products, distinct_regions,
    distinct_months, filter_by_product, filter_by_region, filter_by_month,
    count_by_product, count_by_region, count_by_month, records_with_units_above,
    records_with_price_below, sort_by_units, sort_by_price
"""
import pytest

# SAMPLE_DATA used by independent tasks 3-20
SAMPLE = [
    {"product": "Alpha", "units": 10, "price": 5.0,  "region": "North", "month": "Jan"},
    {"product": "Beta",  "units":  5, "price": 12.0, "region": "South", "month": "Jan"},
    {"product": "Alpha", "units":  8, "price": 5.0,  "region": "East",  "month": "Feb"},
    {"product": "Gamma", "units":  3, "price": 20.0, "region": "West",  "month": "Feb"},
    {"product": "Beta",  "units": 12, "price": 12.0, "region": "North", "month": "Mar"},
]


# ── get_records ───────────────────────────────────────────────────────────────
def test_get_records_returns_12():
    from get_records import get_records
    assert len(get_records()) == 12

def test_get_records_has_one_zero_units():
    from get_records import get_records
    invalid = [r for r in get_records() if r["units"] == 0]
    assert len(invalid) == 1

def test_get_records_fields():
    from get_records import get_records
    for r in get_records():
        assert {"product", "units", "price", "region", "month"} <= r.keys()


# ── remove_invalid ────────────────────────────────────────────────────────────
def test_remove_invalid_returns_11():
    from remove_invalid import remove_invalid
    assert len(remove_invalid()) == 11

def test_remove_invalid_no_zero_units():
    from remove_invalid import remove_invalid
    assert all(r["units"] > 0 for r in remove_invalid())

def test_remove_invalid_subset_of_get_records():
    from get_records import get_records
    from remove_invalid import remove_invalid
    full = get_records()
    valid = remove_invalid()
    assert len(valid) < len(full)


# ── compute_line_revenue ──────────────────────────────────────────────────────
def test_compute_line_revenue_basic():
    from compute_line_revenue import compute_line_revenue
    assert compute_line_revenue({"product": "Alpha", "units": 10, "price": 5.0,
                                  "region": "North", "month": "Jan"}) == pytest.approx(50.0)

def test_compute_line_revenue_from_sample():
    from compute_line_revenue import compute_line_revenue
    assert compute_line_revenue(SAMPLE[1]) == pytest.approx(60.0)  # 5 * 12.0

def test_compute_line_revenue_all_sample():
    from compute_line_revenue import compute_line_revenue
    for r in SAMPLE:
        assert compute_line_revenue(r) == pytest.approx(r["units"] * r["price"])


# ── total_units ───────────────────────────────────────────────────────────────
def test_total_units_sample():
    from total_units import total_units
    assert total_units(SAMPLE) == 38  # 10+5+8+3+12

def test_total_units_empty():
    from total_units import total_units
    assert total_units([]) == 0

def test_total_units_single():
    from total_units import total_units
    assert total_units([SAMPLE[0]]) == 10


# ── average_price ─────────────────────────────────────────────────────────────
def test_average_price_sample():
    from average_price import average_price
    assert average_price(SAMPLE) == pytest.approx(10.8)  # (5+12+5+20+12)/5

def test_average_price_empty_raises():
    from average_price import average_price
    with pytest.raises((ValueError, ZeroDivisionError)):
        average_price([])

def test_average_price_single():
    from average_price import average_price
    assert average_price([SAMPLE[2]]) == pytest.approx(5.0)


# ── max_units_record ──────────────────────────────────────────────────────────
def test_max_units_record_returns_highest():
    from max_units_record import max_units_record
    result = max_units_record(SAMPLE)
    assert result["units"] == 12  # Beta Mar

def test_max_units_record_empty_raises():
    from max_units_record import max_units_record
    with pytest.raises((ValueError, IndexError)):
        max_units_record([])

def test_max_units_record_single():
    from max_units_record import max_units_record
    assert max_units_record([SAMPLE[0]]) == SAMPLE[0]


# ── min_price_record ──────────────────────────────────────────────────────────
def test_min_price_record_returns_lowest_price():
    from min_price_record import min_price_record
    result = min_price_record(SAMPLE)
    assert result["price"] == pytest.approx(5.0)

def test_min_price_record_empty_raises():
    from min_price_record import min_price_record
    with pytest.raises((ValueError, IndexError)):
        min_price_record([])

def test_min_price_record_single():
    from min_price_record import min_price_record
    assert min_price_record([SAMPLE[3]]) == SAMPLE[3]


# ── distinct_products ─────────────────────────────────────────────────────────
def test_distinct_products_sorted():
    from distinct_products import distinct_products
    assert distinct_products(SAMPLE) == ["Alpha", "Beta", "Gamma"]

def test_distinct_products_empty():
    from distinct_products import distinct_products
    assert distinct_products([]) == []


# ── distinct_regions ──────────────────────────────────────────────────────────
def test_distinct_regions_sorted():
    from distinct_regions import distinct_regions
    assert distinct_regions(SAMPLE) == ["East", "North", "South", "West"]

def test_distinct_regions_empty():
    from distinct_regions import distinct_regions
    assert distinct_regions([]) == []


# ── distinct_months ───────────────────────────────────────────────────────────
def test_distinct_months_first_appearance_order():
    from distinct_months import distinct_months
    assert distinct_months(SAMPLE) == ["Jan", "Feb", "Mar"]

def test_distinct_months_no_duplicates():
    from distinct_months import distinct_months
    result = distinct_months(SAMPLE)
    assert len(result) == len(set(result))


# ── filter_by_product ─────────────────────────────────────────────────────────
def test_filter_by_product_alpha():
    from filter_by_product import filter_by_product
    result = filter_by_product(SAMPLE, "Alpha")
    assert len(result) == 2
    assert all(r["product"] == "Alpha" for r in result)

def test_filter_by_product_missing():
    from filter_by_product import filter_by_product
    assert filter_by_product(SAMPLE, "Delta") == []


# ── filter_by_region ──────────────────────────────────────────────────────────
def test_filter_by_region_north():
    from filter_by_region import filter_by_region
    result = filter_by_region(SAMPLE, "North")
    assert len(result) == 2
    assert all(r["region"] == "North" for r in result)

def test_filter_by_region_missing():
    from filter_by_region import filter_by_region
    assert filter_by_region(SAMPLE, "Central") == []


# ── filter_by_month ───────────────────────────────────────────────────────────
def test_filter_by_month_jan():
    from filter_by_month import filter_by_month
    result = filter_by_month(SAMPLE, "Jan")
    assert len(result) == 2
    assert all(r["month"] == "Jan" for r in result)

def test_filter_by_month_missing():
    from filter_by_month import filter_by_month
    assert filter_by_month(SAMPLE, "Apr") == []


# ── count_by_product ──────────────────────────────────────────────────────────
def test_count_by_product_values():
    from count_by_product import count_by_product
    counts = count_by_product(SAMPLE)
    assert counts["Alpha"] == 2
    assert counts["Beta"] == 2
    assert counts["Gamma"] == 1

def test_count_by_product_keys():
    from count_by_product import count_by_product
    assert set(count_by_product(SAMPLE).keys()) == {"Alpha", "Beta", "Gamma"}

def test_count_by_product_total():
    from count_by_product import count_by_product
    assert sum(count_by_product(SAMPLE).values()) == len(SAMPLE)


# ── count_by_region ───────────────────────────────────────────────────────────
def test_count_by_region_north():
    from count_by_region import count_by_region
    counts = count_by_region(SAMPLE)
    assert counts["North"] == 2

def test_count_by_region_total():
    from count_by_region import count_by_region
    assert sum(count_by_region(SAMPLE).values()) == len(SAMPLE)


# ── count_by_month ────────────────────────────────────────────────────────────
def test_count_by_month_values():
    from count_by_month import count_by_month
    counts = count_by_month(SAMPLE)
    assert counts["Jan"] == 2
    assert counts["Feb"] == 2
    assert counts["Mar"] == 1

def test_count_by_month_total():
    from count_by_month import count_by_month
    assert sum(count_by_month(SAMPLE).values()) == len(SAMPLE)


# ── records_with_units_above ──────────────────────────────────────────────────
def test_records_with_units_above_5():
    from records_with_units_above import records_with_units_above
    result = records_with_units_above(SAMPLE, 5)
    assert len(result) == 3  # Alpha-Jan(10), Alpha-Feb(8), Beta-Mar(12)

def test_records_with_units_above_all_exceed_threshold():
    from records_with_units_above import records_with_units_above
    result = records_with_units_above(SAMPLE, 5)
    assert all(r["units"] > 5 for r in result)

def test_records_with_units_above_high_threshold():
    from records_with_units_above import records_with_units_above
    assert records_with_units_above(SAMPLE, 100) == []


# ── records_with_price_below ──────────────────────────────────────────────────
def test_records_with_price_below_12():
    from records_with_price_below import records_with_price_below
    result = records_with_price_below(SAMPLE, 12.0)
    assert len(result) == 2  # Alpha-Jan(5.0), Alpha-Feb(5.0)

def test_records_with_price_below_all_below_threshold():
    from records_with_price_below import records_with_price_below
    result = records_with_price_below(SAMPLE, 12.0)
    assert all(r["price"] < 12.0 for r in result)


# ── sort_by_units ─────────────────────────────────────────────────────────────
def test_sort_by_units_descending():
    from sort_by_units import sort_by_units
    result = sort_by_units(SAMPLE)
    units = [r["units"] for r in result]
    assert units == sorted(units, reverse=True)

def test_sort_by_units_first_element():
    from sort_by_units import sort_by_units
    result = sort_by_units(SAMPLE)
    assert result[0]["units"] == 12  # Beta Mar

def test_sort_by_units_does_not_mutate():
    from sort_by_units import sort_by_units
    original_first = SAMPLE[0]["units"]
    sort_by_units(SAMPLE)
    assert SAMPLE[0]["units"] == original_first


# ── sort_by_price ─────────────────────────────────────────────────────────────
def test_sort_by_price_ascending():
    from sort_by_price import sort_by_price
    result = sort_by_price(SAMPLE)
    prices = [r["price"] for r in result]
    assert prices == sorted(prices)

def test_sort_by_price_first_element():
    from sort_by_price import sort_by_price
    result = sort_by_price(SAMPLE)
    assert result[0]["price"] == pytest.approx(5.0)

def test_sort_by_price_does_not_mutate():
    from sort_by_price import sort_by_price
    original_first = SAMPLE[0]["price"]
    sort_by_price(SAMPLE)
    assert SAMPLE[0]["price"] == original_first
