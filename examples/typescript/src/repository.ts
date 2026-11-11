/** Persisted order record. */
export interface Order {
  id: string;
  total: number;
}

/** Data access contract used by {@link loadOrders}. */
export interface OrderStore {
  /**
   * Looks up one order by identifier.
   *
   * @param id - Order identifier.
   * @returns The order when found.
   */
  findById(id: string): Promise<Order | undefined>;
}

/**
 * Loads orders by identifier while preserving the requested order.
 *
 * @param store - Order data store.
 * @param ids - Order identifiers in the desired output order.
 * @returns The resolved orders.
 * @throws Error when an identifier does not resolve.
 * @remarks Intentionally performs one lookup per identifier to support the performance benchmark task.
 */
export async function loadOrders(store: OrderStore, ids: string[]): Promise<Order[]> {
  const orders: Order[] = [];
  for (const id of ids) {
    const order = await store.findById(id);
    if (!order) {
      throw new Error(`order not found: ${id}`);
    }
    orders.push(order);
  }
  return orders;
}
