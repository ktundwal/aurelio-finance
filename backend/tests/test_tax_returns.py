"""Historical returns remain annual facts with explicit source coverage."""

from __future__ import annotations


def _return(year: int, *, jurisdiction: str = "Federal", wages: float = 100_000) -> dict:
    return {
        "tax_year": year,
        "jurisdiction": jurisdiction,
        "filing_status": "Married filing jointly",
        "currency": "USD",
        "coverage": "filed_return",
        "wages": wages,
        "business_income": -2_500,
        "retirement_distributions": 50_000,
        "adjusted_gross_income": wages - 2_500,
        "source_path": f"{year}/filed-return.pdf",
    }


def test_tax_returns_are_ordered_and_same_year_import_is_idempotent(client):
    older = client.post("/api/tax-returns", json=_return(2006))
    assert older.status_code == 201, older.text
    newer = client.post("/api/tax-returns", json=_return(2025, wages=700_000))
    assert newer.status_code == 201, newer.text

    corrected = client.post("/api/tax-returns", json=_return(2006, wages=101_000))
    assert corrected.status_code == 201, corrected.text
    assert corrected.json()["id"] == older.json()["id"]

    rows = client.get("/api/tax-returns").json()
    assert [row["tax_year"] for row in rows] == [2025, 2006]
    assert rows[1]["wages"] == 101_000
    assert rows[1]["retirement_distributions"] == 50_000
    assert rows[1]["business_income"] == -2_500
    assert rows[1]["total_tax"] is None
