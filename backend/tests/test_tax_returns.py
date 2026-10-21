"""Historical returns remain annual facts with explicit source coverage."""

from __future__ import annotations

import pytest

from tests.test_chat import _events, _fake_stream


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


def test_chat_from_empty_tax_history_resolves_and_remembers_the_page(client, monkeypatch):
    seen = _fake_stream(monkeypatch)
    events = _events(client.post("/api/chat", json={
        "content": "What tax records do I have?",
        "page": {"kind": "records", "section": "taxes"},
    }))

    assert events[-1]["kind"] == "done"
    question = seen[0]["messages"][-1]["content"]
    assert question.startswith("<screen>\nRecords → Taxes\n")
    assert "annual tax records" in question
    assert "recurring cash flow" in question
    stored = client.get(
        f"/api/chat/conversations/{events[0]['conversation_id']}"
    ).json()["messages"]
    assert stored[0]["blocks"][0] == {"kind": "page", "label": "Records → Taxes"}


@pytest.mark.parametrize("coverage", ["filed_return", "source_documents", "payment_only"])
def test_chat_receives_tax_details_and_provenance_without_inventing_totals(
    client, monkeypatch, coverage
):
    amounts = {
        "wages": ("wages", 100_000),
        "taxable_interest": ("taxable interest", 101),
        "tax_exempt_interest": ("tax-exempt interest", 102),
        "ordinary_dividends": ("ordinary dividends", 103),
        "qualified_dividends": ("qualified dividends", 104),
        "capital_gain": ("capital gain or loss", -105),
        "business_income": ("business income or loss", -106),
        "retirement_distributions": ("retirement distributions", 50_000),
        "taxable_retirement_distributions": ("taxable retirement distributions", 40_000),
        "unemployment_income": ("unemployment compensation", 107),
        "other_income": ("other income", 108),
        "total_income": ("total income", 109),
        "adjustments": ("adjustments", 110),
        "hsa_deduction": ("HSA deduction", 111),
        "moving_expenses": ("moving expenses", 112),
        "ira_deduction": ("IRA deduction", 113),
        "adjusted_gross_income": ("AGI", 114),
        "deductions": ("deductions", 115),
        "exemptions": ("exemptions", 116),
        "taxable_income": ("taxable income", 117),
        "tax_before_credits": ("tax before credits", 118),
        "credits": ("credits", 119),
        "other_taxes": ("other taxes", 120),
        "withholding": ("withholding", 121),
        "estimated_payments": ("estimated payments", 122),
        "other_payments": ("other payments and credits", 123),
        "total_payments": ("payments", 124),
        "refund": ("refund", 0),
        "amount_owed": ("owed", 125),
        "penalty": ("penalty or interest", 126),
    }
    payload = {
        **_return(2006),
        **{key: value for key, (_, value) in amounts.items()},
        "coverage": coverage,
        "notes": "Only the surviving pages were recoverable; total tax is unknown.",
    }
    response = client.post("/api/tax-returns", json=payload)
    assert response.status_code == 201, response.text
    seen = _fake_stream(monkeypatch)

    _events(client.post("/api/chat", json={
        "content": "Explain the recorded tax evidence.",
        "page": {"kind": "records", "section": "taxes"},
    }))

    picture = seen[0]["messages"][0]["content"]
    history = picture.split("## Tax history", 1)[1].split("\n## ", 1)[0]
    assert f"2006 Federal [{coverage}]" in history
    assert "filing status: Married filing jointly" in history
    for label, value in amounts.values():
        assert f"{label} {value:.2f} USD" in history
    assert "total tax 0.00" not in history
    assert payload["source_path"] in history
    assert payload["notes"] in history
