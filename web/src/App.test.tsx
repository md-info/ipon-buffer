import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import App, { ConsentBalances } from './App';
import { checkHealth, toMinor } from './api';

describe('foundation', () => {
  it('starts with one centered demo login action', () => {
    const html = renderToStaticMarkup(<App />);
    expect(html).toContain('ipon-login');
    expect(html).toContain('Log in to synthetic demo');
    expect(html.match(/<button/g)).toHaveLength(1);
    expect(html).not.toContain('landing-cards');
  });
  it('converts typed decimal amounts exactly into minor units', () => {
    expect(toMinor('0.29')).toBe(29);
    expect(toMinor('300')).toBe(30000);
    expect(toMinor('120.05')).toBe(12005);
    for (const value of ['-1', '1e3', '0.001', 'NaN', '1000001']) expect(() => toMinor(value)).toThrow();
  });
  it('accepts the health contract', async () => {
    const request = vi.fn().mockResolvedValue(new Response('{"status":"ok"}'));
    expect(await checkHealth(request)).toBe(true);
    expect(request.mock.calls[0][0]).toBe('/health');
  });
  it('does not show ready for an unhealthy server', async () => {
    await expect(checkHealth(vi.fn().mockResolvedValue(new Response('', {status: 503})))).rejects.toThrow();
    expect(await checkHealth(vi.fn().mockResolvedValue(new Response('{}')))).toBe(false);
  });
});

describe('consent balance disclosure', () => {
  it('shows starting balances as read-only synthetic money', () => {
    const html = renderToStaticMarkup(<ConsentBalances wallet={{ available_minor: 200000, buffer_minor: 50000 }} />);
    expect(html).toContain('Everyday wallet');
    expect(html).toContain('₱2,000.00');
    expect(html).toContain('Emergency buffer');
    expect(html).toContain('₱500.00');
    expect(html).toContain('Synthetic balances. No real money.');
    expect(html).not.toContain('<input');
  });
  it('shows updated balances when consent is reviewed later', () => {
    const html = renderToStaticMarkup(<ConsentBalances wallet={{ available_minor: 188000, buffer_minor: 62000 }} />);
    expect(html).toContain('₱1,880.00');
    expect(html).toContain('₱620.00');
    expect(html).not.toContain('₱2,000.00');
  });
});
