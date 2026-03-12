"""Pre-written test suite for Sales Data Analysis Pipeline (p=0.5, N=20).

Chain (tasks 1-10): get_records -> remove_invalid -> add_revenue ->
    total_revenue -> average_revenue -> above_average_records ->
    group_by_product -> group_revenue_totals -> rank_by_revenue -> revenue_summary
Independent (tasks 11-20): compute_line_revenue, total_units, average_price,
    max_units_record, filter_by_product, filter_by_region, filter_by_month,
    distinct_products, sort_by_units, sort_by_price

Key values (derived from the hard-coded SALES_RECORDS, 11 valid records):
  total_revenue  ≈ 1594.19
  average_revenue ≈ 144.93
  above_average: 5 records (Doohickey-Jan, Gadget-Feb, Doohickey-Feb,
                             Widget-Mar, Gadget-Mar)
  group revenue totals: Gadget≈449.82, Doohickey≈349.93, Widget≈149.85
  grand_total ≈ 949.60
"""
import pytest

# SAMPLE_DATA used by independent tasks 11-20
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


# ── add_revenue ───────────────────────────────────────────────────────────────
def test_add_revenue_returns_11():
    from add_revenue import add_revenue
    assert len(add_revenue()) == 11

def test_add_revenue_has_revenue_field():
    from add_revenue import add_revenue
    assert all("revenue" in r for r in add_revenue())

def test_add_revenue_correct_calculation():
    from add_revenue import add_revenue
    for r in add_revenue():
        assert r["revenue"] == pytest.approx(r["units"] * r["price"])

def test_add_revenue_does_not_mutate_upstream():
    from add_revenue import add_revenue
    from remove_invalid import remove_invalid
    before = [r.copy() for r in remove_invalid()]
    add_revenue()
    after = remove_invalid()
    for b, a in zip(before, after):
        assert "revenue" not in a or b.get("revenue") == a.get("revenue")


# ── total_revenue ─────────────────────────────────────────────────────────────
def test_total_revenue_value():
    from total_revenue import total_revenue
    assert total_revenue() == pytest.approx(1594.19, abs=0.01)

def test_total_revenue_positive():
    from total_revenue import total_revenue
    assert total_revenue() > 0


# ── average_revenue ───────────────────────────────────────────────────────────
def test_average_revenue_value():
    from average_revenue import average_revenue
    assert average_revenue() == pytest.approx(1594.19 / 11, abs=0.01)

def test_average_revenue_less_than_max():
    from average_revenue import average_revenue
    from add_revenue import add_revenue
    max_rev = max(r["revenue"] for r in add_revenue())
    assert average_revenue() < max_rev


# ── above_average_records ─────────────────────────────────────────────────────
def test_above_average_records_count():
    from above_average_records import above_average_records
    assert len(above_average_records()) == 5

def test_above_average_records_all_exceed_mean():
    from above_average_records import above_average_records
    from average_revenue import average_revenue
    threshold = average_revenue()
    assert all(r["revenue"] > threshold for r in above_average_records())

def test_above_average_records_has_revenue_field():
    from above_average_records import above_average_records
    assert all("revenue" in r for r in above_average_records())


# ── group_by_product ──────────────────────────────────────────────────────────
def test_group_by_product_keys():
    from group_by_product import group_by_product
    assert set(group_by_product().keys()) == {"Doohickey", "Gadget", "Widget"}

def test_group_by_product_counts():
    from group_by_product import group_by_product
    groups = group_by_product()
    assert len(groups["Doohickey"]) == 2
    assert len(groups["Gadget"]) == 2
    assert len(groups["Widget"]) == 1

def test_group_by_product_all_records_match_key():
    from group_by_product import group_by_product
    for product, records in group_by_product().items():
        assert all(r["product"] == product for r in records)


# ── group_revenue_totals ──────────────────────────────────────────────────────
def test_group_revenue_totals_keys():
    from group_revenue_totals import group_revenue_totals
    assert set(group_revenue_totals().keys()) == {"Doohickey", "Gadget", "Widget"}

def test_group_revenue_totals_gadget():
    from group_revenue_totals import group_revenue_totals
    assert group_revenue_totals()["Gadget"] == pytest.approx(449.82, abs=0.01)

def test_group_revenue_totals_doohickey():
    from group_revenue_totals import group_revenue_totals
    assert group_revenue_totals()["Doohickey"] == pytest.approx(349.93, abs=0.01)

def test_group_revenue_totals_widget():
    from group_revenue_totals import group_revenue_totals
    assert group_revenue_totals()["Widget"] == pytest.approx(149.85, abs=0.01)


# ── rank_by_revenue ───────────────────────────────────────────────────────────
def test_rank_by_revenue_length():
    from rank_by_revenue import rank_by_revenue
    assert len(rank_by_revenue()) == 3

def test_rank_by_revenue_top_is_gadget():
    from rank_by_revenue import rank_by_revenue
    top = rank_by_revenue()[0]
    assert top[0] == "Gadget"
    assert top[1] == pytest.approx(449.82, abs=0.01)

def test_rank_by_revenue_descending():
    from rank_by_revenue import rank_by_revenue
    revenues = [entry[1] for entry in rank_by_revenue()]
    assert revenues == sorted(revenues, reverse=True)


# ── revenue_summary ───────────────────────────────────────────────────────────
def test_revenue_summary_has_required_keys():
    from revenue_summary import revenue_summary
    summary = revenue_summary()
    assert "rankings" in summary
    assert "top_product" in summary
    assert "grand_total" in summary

def test_revenue_summary_top_product():
    from revenue_summary import revenue_summary
    assert revenue_summary()["top_product"] == "Gadget"

def test_revenue_summary_grand_total():
    from revenue_summary import revenue_summary
    assert revenue_summary()["grand_total"] == pytest.approx(949.60, abs=0.01)

def test_revenue_summary_rankings_length():
    from revenue_summary import revenue_summary
    assert len(revenue_summary()["rankings"]) == 3


# ── compute_line_revenue (task-11) ────────────────────────────────────────────
def test_compute_line_revenue_basic():
    from compute_line_revenue import compute_line_revenue
    assert compute_line_revenue(SAMPLE[0]) == pytest.approx(50.0)  # 10 * 5.0

def test_compute_line_revenue_all_sample():
    from compute_line_revenue import compute_line_revenue
    for r in SAMPLE:
        assert compute_line_revenue(r) == pytest.approx(r["units"] * r["price"])


# ── total_units (task-12) ─────────────────────────────────────────────────────
def test_total_units_sample():
    from total_units import total_units
    assert total_units(SAMPLE) == 38

def test_total_units_empty():
    from total_units import total_units
    assert total_units([]) == 0


# ── average_price (task-13) ───────────────────────────────────────────────────
def test_average_price_sample():
    from average_price import average_price
    assert average_price(SAMPLE) == pytest.approx(10.8)

def test_average_price_empty_raises():
    from average_price import average_price
    with pytest.raises((ValueError, ZeroDivisionError)):
        average_price([])


# ── max_units_record (task-14) ────────────────────────────────────────────────
def test_max_units_record_returns_highest():
    from max_units_record import max_units_record
    assert max_units_record(SAMPLE)["units"] == 12

def test_max_units_record_empty_raises():
    from max_units_record import max_units_record
    with pytest.raises((ValueError, IndexError)):
        max_units_record([])


# ── filter_by_product (task-15) ───────────────────────────────────────────────
def test_filter_by_product_alpha():
    from filter_by_product import filter_by_product
    result = filter_by_product(SAMPLE, "Alpha")
    assert len(result) == 2
    assert all(r["product"] == "Alpha" for r in result)

def test_filter_by_product_missing():
    from filter_by_product import filter_by_product
    assert filter_by_product(SAMPLE, "Delta") == []


# ── filter_by_region (task-16) ────────────────────────────────────────────────
def test_filter_by_region_north():
    from filter_by_region import filter_by_region
    result = filter_by_region(SAMPLE, "North")
    assert len(result) == 2
    assert all(r["region"] == "North" for r in result)

def test_filter_by_region_missing():
    from filter_by_region import filter_by_region
    assert filter_by_region(SAMPLE, "Central") == []


# ── filter_by_month (task-17) ─────────────────────────────────────────────────
def test_filter_by_month_jan():
    from filter_by_month import filter_by_month
    result = filter_by_month(SAMPLE, "Jan")
    assert len(result) == 2
    assert all(r["month"] == "Jan" for r in result)

def test_filter_by_month_missing():
    from filter_by_month import filter_by_month
    assert filter_by_month(SAMPLE, "Apr") == []


# ── distinct_products (task-18) ───────────────────────────────────────────────
def test_distinct_products_sorted():
    from distinct_products import distinct_products
    assert distinct_products(SAMPLE) == ["Alpha", "Beta", "Gamma"]

def test_distinct_products_empty():
    from distinct_products import distinct_products
    assert distinct_products([]) == []


# ── sort_by_units (task-19) ───────────────────────────────────────────────────
def test_sort_by_units_descending():
    from sort_by_units import sort_by_units
    result = sort_by_units(SAMPLE)
    units = [r["units"] for r in result]
    assert units == sorted(units, reverse=True)

def test_sort_by_units_does_not_mutate():
    from sort_by_units import sort_by_units
    original = SAMPLE[0]["units"]
    sort_by_units(SAMPLE)
    assert SAMPLE[0]["units"] == original


# ── sort_by_price (task-20) ───────────────────────────────────────────────────
def test_sort_by_price_ascending():
    from sort_by_price import sort_by_price
    result = sort_by_price(SAMPLE)
    prices = [r["price"] for r in result]
    assert prices == sorted(prices)

def test_sort_by_price_does_not_mutate():
    from sort_by_price import sort_by_price
    original = SAMPLE[0]["price"]
    sort_by_price(SAMPLE)
    assert SAMPLE[0]["price"] == original
