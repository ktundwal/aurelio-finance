import { Fragment, useEffect, useState } from "react";
import { getTaxReturns, type TaxReturn } from "../api/taxReturns";
import { taxOutcome } from "./taxHistoryWords";
import { apiError, cardClass, money } from "./ui";

const COVERAGE: Record<TaxReturn["coverage"], string> = {
  filed_return: "Filed return",
  source_documents: "Source documents only",
  payment_only: "Payment record only",
};

const DETAIL_FIELDS: Array<[keyof TaxReturn, string]> = [
  ["wages", "Wages"],
  ["taxable_interest", "Taxable interest"],
  ["tax_exempt_interest", "Tax-exempt interest"],
  ["ordinary_dividends", "Ordinary dividends"],
  ["qualified_dividends", "Qualified dividends"],
  ["capital_gain", "Capital gain or loss"],
  ["business_income", "Business income or loss"],
  ["retirement_distributions", "Retirement distributions"],
  ["taxable_retirement_distributions", "Taxable retirement distributions"],
  ["unemployment_income", "Unemployment compensation"],
  ["other_income", "Other income"],
  ["total_income", "Total income"],
  ["adjustments", "Adjustments"],
  ["hsa_deduction", "HSA deduction"],
  ["moving_expenses", "Moving expenses"],
  ["ira_deduction", "IRA deduction"],
  ["adjusted_gross_income", "Adjusted gross income"],
  ["deductions", "Deductions"],
  ["exemptions", "Exemptions"],
  ["taxable_income", "Taxable income"],
  ["tax_before_credits", "Tax before credits"],
  ["credits", "Credits"],
  ["other_taxes", "Other taxes"],
  ["total_tax", "Total tax"],
  ["withholding", "Withholding"],
  ["estimated_payments", "Estimated payments"],
  ["other_payments", "Other payments and credits"],
  ["total_payments", "Total payments"],
  ["refund", "Refund"],
  ["amount_owed", "Amount owed"],
  ["penalty", "Penalty or interest"],
];

function amount(row: TaxReturn, key: keyof TaxReturn): string {
  const value = row[key];
  return typeof value === "number" ? money(row.currency).format(value) : "—";
}

export default function TaxHistory() {
  const [rows, setRows] = useState<TaxReturn[]>([]);
  const [open, setOpen] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTaxReturns()
      .then(setRows)
      .catch((err) => setError(apiError(err, "Could not load tax history.")))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-sm text-ink-soft">Loading tax history…</p>;
  if (error) return <p className="text-sm text-danger">{error}</p>;

  const filed = rows.filter((row) => row.coverage === "filed_return").length;
  const first = rows.length ? Math.min(...rows.map((row) => row.tax_year)) : null;
  const last = rows.length ? Math.max(...rows.map((row) => row.tax_year)) : null;

  return (
    <section className="space-y-5">
      <div>
        <h1 className="font-display text-2xl text-ink">Tax history</h1>
        <p className="mt-1 text-sm text-ink-soft">
          Annual return figures stay separate from recurring income and expenses. {rows.length} jurisdiction records
          {first == null ? "" : ` cover ${first}–${last}`}; {filed} come from filed returns.
        </p>
      </div>

      {rows.length === 0 ? (
        <div className={cardClass + " p-5 text-sm text-ink-soft"}>No tax returns recorded.</div>
      ) : (
        <div className={cardClass + " overflow-x-auto"}>
          <table className="w-full min-w-[960px] border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-rule text-ink-soft">
                <th className="px-4 py-3 font-medium">Year</th>
                <th className="px-4 py-3 font-medium">Jurisdiction</th>
                <th className="px-4 py-3 font-medium">Coverage</th>
                <th className="px-4 py-3 text-right font-medium">Wages</th>
                <th className="px-4 py-3 text-right font-medium">AGI</th>
                <th className="px-4 py-3 text-right font-medium">Taxable income</th>
                <th className="px-4 py-3 text-right font-medium">Total tax</th>
                <th className="px-4 py-3 text-right font-medium">Outcome</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <Fragment key={row.id}>
                  <tr key={row.id} className="border-b border-hair last:border-0">
                    <td className="px-4 py-3 font-semibold text-ink">
                      <button
                        type="button"
                        className="rounded-sm text-left underline decoration-hair underline-offset-4 hover:text-olive"
                        aria-expanded={open === row.id}
                        onClick={() => setOpen(open === row.id ? null : row.id)}
                      >
                        {row.tax_year}
                      </button>
                    </td>
                    <td className="px-4 py-3">{row.jurisdiction}</td>
                    <td className="px-4 py-3 text-ink-soft">{COVERAGE[row.coverage]}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{amount(row, "wages")}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{amount(row, "adjusted_gross_income")}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{amount(row, "taxable_income")}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{amount(row, "total_tax")}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{taxOutcome(row)}</td>
                  </tr>
                  {open === row.id && (
                    <tr key={`${row.id}-detail`} className="border-b border-rule bg-tint/40">
                      <td colSpan={8} className="px-4 py-5">
                        <div className="grid gap-x-8 gap-y-3 sm:grid-cols-2 lg:grid-cols-4">
                          {DETAIL_FIELDS.filter(([key]) => row[key] != null).map(([key, label]) => (
                            <div key={key}>
                              <div className="text-xs text-ink-soft">{label}</div>
                              <div className="tabular-nums text-ink">{amount(row, key)}</div>
                            </div>
                          ))}
                        </div>
                        <div className="mt-5 space-y-1 border-t border-hair pt-3 text-xs text-ink-soft">
                          {row.filing_status && <p>Filing status: {row.filing_status}</p>}
                          <p>Source: {row.source_path}</p>
                          {row.notes && <p>{row.notes}</p>}
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
