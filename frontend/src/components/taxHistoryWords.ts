import type { TaxReturn } from "../api/taxReturns";
import { money } from "./money.ts";

export function taxOutcome(
  row: Pick<TaxReturn, "currency" | "refund" | "amount_owed">,
): string {
  if (row.refund != null && row.refund !== 0) {
    return `${money(row.currency).format(row.refund)} refund`;
  }
  if (row.amount_owed != null && row.amount_owed !== 0) {
    return `${money(row.currency).format(row.amount_owed)} owed`;
  }
  if (row.refund === 0 && row.amount_owed === 0) return "Even";
  return "—";
}
