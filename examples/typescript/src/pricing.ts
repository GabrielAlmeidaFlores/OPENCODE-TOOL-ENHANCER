/** One priced line in an order. */
export interface LineItem {
  unitPrice: number;
  quantity: number;
  taxable: boolean;
}

const TAX_RATE = 0.2;

/**
 * Calculates the total for one line item.
 *
 * @param item - Line item with unit price, quantity, and taxability.
 * @returns The line total including tax when applicable.
 */
export function lineTotal(item: LineItem): number {
  const subtotal = item.unitPrice * item.quantity;
  if (item.taxable) {
    return subtotal + subtotal * TAX_RATE;
  }
  return subtotal;
}

/**
 * Calculates the total for an order.
 *
 * @param items - Line items in the order.
 * @returns The sum of all line totals.
 * @remarks Intentionally duplicates the branch in {@link lineTotal} to support the refactor benchmark task.
 */
export function orderTotal(items: LineItem[]): number {
  let total = 0;
  for (const item of items) {
    const subtotal = item.unitPrice * item.quantity;
    if (item.taxable) {
      total += subtotal + subtotal * TAX_RATE;
    } else {
      total += subtotal;
    }
  }
  return total;
}
