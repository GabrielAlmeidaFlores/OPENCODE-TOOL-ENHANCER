export interface Order {
  id: string;
  total: number;
}

export interface OrderStore {
  findById(id: string): Promise<Order | undefined>;
}

// Intentionally N+1 for the performance benchmark task.
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
