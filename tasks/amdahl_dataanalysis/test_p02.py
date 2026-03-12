"""Pre-written test suite for Sales Data Analysis Pipeline (p=0.2, N=20).

Chain (tasks 1-16): get_records -> remove_invalid -> add_revenue ->
    total_revenue -> average_revenue -> above_average_records ->
    group_by_product -> group_revenue_totals -> rank_by_revenue ->
    revenue_summary -> top_product_name -> top_product_records ->
    top_product_monthly_revenue -> best_month_for_top_product ->
    is_top_product_growing -> analysis_summary
Independent (tasks 17-20): compute_line_revenue, filter_by_region,
    distinct_products, sort_by_price

Key values (derived from the hard-coded SALES_RECORDS, 11 valid records):
  total_revenue  ≈ 1594.19
  average_revenue ≈ 144.93
  above_average: 5 records (Doohickey-Jan, Gadget-Feb, Doohickey-Feb,
                             Widget-Mar, Gadget-Mar)
  top product: "Gadget"
  Gadget records (from add_revenue): Jan(124.95), Feb(299.88), Mar(149.94)
  best month for Gadget: "Feb" (revenue 299.88)
  is_growing: True (Feb > Jan)
  grand_total ≈ 949.60
"""
import pytest

# SAMPLE_DATA used by independent tasks 17-20
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
    assert len([r for r in get_records() if r["units"] == 0]) == 1

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

def test_add_revenue_correct_calculation():
    from add_revenue import add_revenue
    for r in add_revenue():
        assert r["revenue"] == pytest.approx(r["units"] * r["price"])


# ── total_revenue ─────────────────────────────────────────────────────────────
def test_total_revenue_value():
    from total_revenue import total_revenue
    assert total_revenue() == pytest.approx(1594.19, abs=0.01)


# ── average_revenue ───────────────────────────────────────────────────────────
def test_average_revenue_value():
    from average_revenue import average_revenue
    assert average_revenue() == pytest.approx(1594.19 / 11, abs=0.01)


# ── above_average_records ─────────────────────────────────────────────────────
def test_above_average_records_count():
    from above_average_records import above_average_records
    assert len(above_average_records()) == 5

def test_above_average_records_all_exceed_mean():
    from above_average_records import above_average_records
    from average_revenue import average_revenue
    threshold = average_revenue()
    assert all(r["revenue"] > threshold for r in above_average_records())


# ── group_by_product ──────────────────────────────────────────────────────────
def test_group_by_product_keys():
    from group_by_product import group_by_product
    assert set(group_by_product().keys()) == {"Doohickey", "Gadget", "Widget"}

def test_group_by_product_counts():
    from group_by_product import group_by_product
    groups = group_by_product()
    assert len(groups["Gadget"]) == 2
    assert len(groups["Doohickey"]) == 2
    assert len(groups["Widget"]) == 1


# ── group_revenue_totals ──────────────────────────────────────────────────────
def test_group_revenue_totals_gadget():
    from group_revenue_totals import group_revenue_totals
    assert group_revenue_totals()["Gadget"] == pytest.approx(449.82, abs=0.01)

def test_group_revenue_totals_doohickey():
    from group_revenue_totals import group_revenue_totals
    assert group_revenue_totals()["Doohickey"] == pytest.approx(349.93, abs=0.01)


# ── rank_by_revenue ───────────────────────────────────────────────────────────
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
def test_revenue_summary_top_product():
    from revenue_summary import revenue_summary
    assert revenue_summary()["top_product"] == "Gadget"

def test_revenue_summary_grand_total():
    from revenue_summary import revenue_summary
    assert revenue_summary()["grand_total"] == pytest.approx(949.60, abs=0.01)

def test_revenue_summary_has_required_keys():
    from revenue_summary import revenue_summary
    summary = revenue_summary()
    assert {"rankings", "top_product", "grand_total"} <= summary.keys()


# ── top_product_name ──────────────────────────────────────────────────────────
def test_top_product_name_is_gadget():
    from top_product_name import top_product_name
    assert top_product_name() == "Gadget"

def test_top_product_name_returns_string():
    from top_product_name import top_product_name
    assert isinstance(top_product_name(), str)


# ── top_product_records ───────────────────────────────────────────────────────
def test_top_product_records_count():
    from top_product_records import top_product_records
    # 3 Gadget records in SALES_RECORDS (Jan, Feb, Mar) — all valid (units > 0)
    assert len(top_product_records()) == 3

def test_top_product_records_all_gadget():
    from top_product_records import top_product_records
    assert all(r["product"] == "Gadget" for r in top_product_records())

def test_top_product_records_has_revenue():
    from top_product_records import top_product_records
    assert all("revenue" in r for r in top_product_records())


# ── top_product_monthly_revenue ───────────────────────────────────────────────
def test_top_product_monthly_revenue_keys():
    from top_product_monthly_revenue import top_product_monthly_revenue
    assert set(top_product_monthly_revenue().keys()) == {"Jan", "Feb", "Mar"}

def test_top_product_monthly_revenue_feb():
    from top_product_monthly_revenue import top_product_monthly_revenue
    # Gadget Feb: 12 * 24.99 = 299.88
    assert top_product_monthly_revenue()["Feb"] == pytest.approx(299.88, abs=0.01)

def test_top_product_monthly_revenue_jan():
    from top_product_monthly_revenue import top_product_monthly_revenue
    # Gadget Jan: 5 * 24.99 = 124.95
    assert top_product_monthly_revenue()["Jan"] == pytest.approx(124.95, abs=0.01)

def test_top_product_monthly_revenue_mar():
    from top_product_monthly_revenue import top_product_monthly_revenue
    # Gadget Mar: 6 * 24.99 = 149.94
    assert top_product_monthly_revenue()["Mar"] == pytest.approx(149.94, abs=0.01)


# ── best_month_for_top_product ────────────────────────────────────────────────
def test_best_month_for_top_product_is_feb():
    from best_month_for_top_product import best_month_for_top_product
    # Feb has highest Gadget revenue (299.88)
    assert best_month_for_top_product() == "Feb"

def test_best_month_for_top_product_returns_string():
    from best_month_for_top_product import best_month_for_top_product
    assert isinstance(best_month_for_top_product(), str)


# ── is_top_product_growing ────────────────────────────────────────────────────
def test_is_top_product_growing_true():
    from is_top_product_growing import is_top_product_growing
    # Best month Feb (299.88) > first month Jan (124.95)
    assert is_top_product_growing() is True

def test_is_top_product_growing_returns_bool():
    from is_top_product_growing import is_top_product_growing
    assert isinstance(is_top_product_growing(), bool)


# ── analysis_summary ──────────────────────────────────────────────────────────
def test_analysis_summary_has_required_keys():
    from analysis_summary import analysis_summary
    summary = analysis_summary()
    assert {"top_product", "best_month", "is_growing", "grand_total"} <= summary.keys()

def test_analysis_summary_top_product():
    from analysis_summary import analysis_summary
    assert analysis_summary()["top_product"] == "Gadget"

def test_analysis_summary_best_month():
    from analysis_summary import analysis_summary
    assert analysis_summary()["best_month"] == "Feb"

def test_analysis_summary_is_growing():
    from analysis_summary import analysis_summary
    assert analysis_summary()["is_growing"] is True

def test_analysis_summary_grand_total():
    from analysis_summary import analysis_summary
    assert analysis_summary()["grand_total"] == pytest.approx(949.60, abs=0.01)


# ── compute_line_revenue (task-17) ────────────────────────────────────────────
def test_compute_line_revenue_basic():
    from compute_line_revenue import compute_line_revenue
    assert compute_line_revenue(SAMPLE[0]) == pytest.approx(50.0)  # 10 * 5.0

def test_compute_line_revenue_all_sample():
    from compute_line_revenue import compute_line_revenue
    for r in SAMPLE:
        assert compute_line_revenue(r) == pytest.approx(r["units"] * r["price"])


# ── filter_by_region (task-18) ────────────────────────────────────────────────
def test_filter_by_region_north():
    from filter_by_region import filter_by_region
    result = filter_by_region(SAMPLE, "North")
    assert len(result) == 2
    assert all(r["region"] == "North" for r in result)

def test_filter_by_region_missing():
    from filter_by_region import filter_by_region
    assert filter_by_region(SAMPLE, "Central") == []


# ── distinct_products (task-19) ───────────────────────────────────────────────
def test_distinct_products_sorted():
    from distinct_products import distinct_products
    assert distinct_products(SAMPLE) == ["Alpha", "Beta", "Gamma"]

def test_distinct_products_empty():
    from distinct_products import distinct_products
    assert distinct_products([]) == []


# ── sort_by_price (task-20) ───────────────────────────────────────────────────
def test_sort_by_price_ascending():
    from sort_by_price import sort_by_price
    result = sort_by_price(SAMPLE)
    prices = [r["price"] for r in result]
    assert prices == sorted(prices)

def test_sort_by_price_first_element():
    from sort_by_price import sort_by_price
    assert sort_by_price(SAMPLE)[0]["price"] == pytest.approx(5.0)

def test_sort_by_price_does_not_mutate():
    from sort_by_price import sort_by_price
    original = SAMPLE[0]["price"]
    sort_by_price(SAMPLE)
    assert SAMPLE[0]["price"] == original
