export interface LineItem {
  unitPrice: number;
  quantity: number;
  taxable: boolean;
}

const TAX_RATE = 0.2;

export function lineTotal(item: LineItem): number {
  const subtotal = item.unitPrice * item.quantity;
  if (item.taxable) {
    return subtotal + subtotal * TAX_RATE;
  }
  return subtotal;
}

// Intentionally duplicated for the refactor benchmark task.
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
