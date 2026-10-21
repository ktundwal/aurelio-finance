import { api } from "./client";
import type { Schemas } from "./types";

export type TaxReturn = Schemas["TaxReturnRead"];

export async function getTaxReturns(): Promise<TaxReturn[]> {
  return (await api.get<TaxReturn[]>("/api/tax-returns")).data;
}
