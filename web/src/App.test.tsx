import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import App from './App';
import { checkHealth, toMinor } from './api';

describe('foundation', () => {
  it('shows the synthetic notice before starting a session', () => {
    const html = renderToStaticMarkup(<App />);
    expect(html).toContain('Ipon Buffer');
    expect(html).toContain('Try the rider demo');
    expect(html).toContain('SYNTHETIC DEMO');
    expect(html).toContain('No signup or personal data');
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
