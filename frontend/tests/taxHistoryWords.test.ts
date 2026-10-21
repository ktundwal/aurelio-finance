import assert from "node:assert/strict";
import { test } from "node:test";
import { money } from "../src/components/money.ts";
import { taxOutcome } from "../src/components/taxHistoryWords.ts";

test("a partial or absent tax outcome remains unknown", () => {
  for (const [refund, amount_owed] of [[null, 0], [0, null], [null, null]]) {
    assert.equal(taxOutcome({ currency: "USD", refund, amount_owed }), "—");
  }
});

test("only two recorded zero amounts establish an even outcome", () => {
  assert.equal(taxOutcome({ currency: "USD", refund: 0, amount_owed: 0 }), "Even");
});

test("a recorded nonzero refund or balance is shown in its own currency", () => {
  assert.equal(
    taxOutcome({ currency: "USD", refund: 125, amount_owed: null }),
    `${money("USD").format(125)} refund`,
  );
  assert.equal(
    taxOutcome({ currency: "USD", refund: 0, amount_owed: 250 }),
    `${money("USD").format(250)} owed`,
  );
});
