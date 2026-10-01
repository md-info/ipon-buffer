export async function checkHealth(fetcher: typeof fetch = fetch): Promise<boolean> {
  const response = await fetcher('/health', { signal: AbortSignal.timeout(5000) });
  if (!response.ok) throw new Error('Service unavailable');
  const body: unknown = await response.json();
  return typeof body === 'object' && body !== null && 'status' in body && body.status === 'ok';
}

let token = '';
export function setSession(value: string) { token = value; }
export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); }
}

export async function api<T>(path: string, method = 'GET', body?: unknown, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    method, headers: { 'Content-Type': 'application/json', 'X-Demo-Session': token },
    body: body === undefined ? undefined : JSON.stringify(body), signal: signal ?? AbortSignal.timeout(55000),
  });
  const value = await response.json();
  if (!response.ok) throw new ApiError(value.error?.message ?? 'Request failed. Please try again.', response.status);
  return value as T;
}

export function toMinor(value: string): number {
  if (!/^\d+(\.\d{1,2})?$/.test(value)) throw new Error('Use a positive amount with up to two decimal places.');
  const [whole, decimal = ''] = value.split('.');
  const amount = Number(whole) * 100 + Number(decimal.padEnd(2, '0'));
  if (!Number.isSafeInteger(amount) || amount < 0 || amount > 100000000) throw new Error('Amount is out of range.');
  return amount;
}
export const money = (amount: number) => new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(amount / 100);
