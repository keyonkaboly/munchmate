import api from './api';

export const CUSTOMER_STORAGE_KEY = 'munchmate_customer_id';
export const ACTIVE_ORDER_STORAGE_KEY = 'munchmate_active_order_id';

export function readStoredCustomerId(): number {
  const raw = sessionStorage.getItem(CUSTOMER_STORAGE_KEY);
  if (raw == null || raw === '') return 1;
  const n = parseInt(raw, 10);
  return Number.isFinite(n) && n > 0 ? n : 1;
}

export function writeStoredCustomerId(id: number): void {
  sessionStorage.setItem(CUSTOMER_STORAGE_KEY, String(id));
}

/** When a session cookie exists, align stored customer id with the logged-in user. */
export async function syncCustomerIdFromAuth(): Promise<number | null> {
  try {
    const res = await api.get<{ id: number }>('/auth/me');
    if (res.data?.id != null) {
      writeStoredCustomerId(res.data.id);
      return res.data.id;
    }
  } catch {
    /* not logged in */
  }
  return null;
}
