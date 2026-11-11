import { test } from "node:test";
import assert from "node:assert/strict";

import { validateCreateUser } from "./validation.js";
import { lineTotal, orderTotal } from "./pricing.js";
import { loadOrders, type OrderStore } from "./repository.js";
import { resolveUserFile, BASE_DIR } from "./files.js";

test("validates a valid user", () => {
  assert.deepEqual(validateCreateUser({ email: "a@b.co", name: "Ada", age: 30 }), {
    ok: true,
    errors: [],
  });
});

test("rejects a missing email", () => {
  const result = validateCreateUser({ name: "Ada" });
  assert.equal(result.ok, false);
  assert.match(result.errors.join(","), /email/);
});

test("prices taxable and non-taxable items", () => {
  assert.equal(lineTotal({ unitPrice: 10, quantity: 2, taxable: false }), 20);
  assert.equal(lineTotal({ unitPrice: 10, quantity: 2, taxable: true }), 24);
});

test("totals an order", () => {
  assert.equal(
    orderTotal([
      { unitPrice: 10, quantity: 1, taxable: false },
      { unitPrice: 5, quantity: 2, taxable: true },
    ]),
    22,
  );
});

test("loads orders in order", async () => {
  const store: OrderStore = {
    async findById(id) {
      return { id, total: 1 };
    },
  };
  const orders = await loadOrders(store, ["a", "b"]);
  assert.deepEqual(orders.map((o) => o.id), ["a", "b"]);
});

test("resolves a normal file name", () => {
  assert.equal(resolveUserFile("avatar.png"), `${BASE_DIR}/avatar.png`);
});
