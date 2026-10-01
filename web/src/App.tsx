import { useEffect, useRef, useState } from 'react';
import { api, ApiError, money, setSession, toMinor } from './api';
import type { Bill, Draft, Plan, Summary, Wallet } from './types';
import c from './i18n/product.en.json';

type Tab = 'overview' | 'plan' | 'emergency' | 'privacy';
const allScopes = ['transactions:read', 'balance:read', 'buffer:transfer', 'ai:parse'];
const initialChoices = [false, false, false, false];

export default function App() {
  const [phase, setPhase] = useState<'start' | 'consent' | 'app'>('start');
  const [tab, setTab] = useState<Tab>('overview');
  const [data, setData] = useState<Summary | null>(null);
  const [wallet, setWallet] = useState<Wallet>({ available_minor: 200000, buffer_minor: 50000 });
  const [plan, setPlan] = useState<Plan | null>(null);
  const [choices, setChoices] = useState(initialChoices);
  const [days, setDays] = useState(90);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [modelMode, setModelMode] = useState('disabled');
  const [text, setText] = useState('');
  const [draft, setDraft] = useState<Draft | null>(null);
  const [amount, setAmount] = useState('600');
  const [refill, setRefill] = useState<{ weekly_minor: number; estimated_weeks: number } | null>(null);
  const [withdrawalMade, setWithdrawalMade] = useState(false);
  const [confirmAction, setConfirmAction] = useState<'delete' | 'reset' | null>(null);
  const [audit, setAudit] = useState<{ verified: boolean; entries: { action: string; ts: number }[] } | null>(null);
  const controller = useRef<AbortController | null>(null);
  const retry = useRef<Record<string, string>>({});
  const pendingDeposit = useRef<{ id: string; amount_minor: number } | null>(null);
  useEffect(() => { window.scrollTo({ top: 0, behavior: 'instant' }); }, [tab, phase]);

  const accept = (value: Summary) => { setData(value); setPlan(value.plan); setWallet(value); setModelMode(value.assistant_mode); };
  const perform = async (operation: () => Promise<void>) => {
    setBusy(true); setError(''); setNotice('');
    try { await operation(); } catch (e) { setError(e instanceof Error ? e.message : 'Request failed'); }
    finally { setBusy(false); }
  };
  const refresh = async () => { setWallet(await api<Wallet>('/wallet')); if (choices[0] && choices[1]) accept(await api<Summary>('/summary')); };
  const start = () => perform(async () => {
    const response = await api<{ token: string; assistant_mode: string }>('/sandbox/start', 'POST');
    setSession(response.token); setModelMode(response.assistant_mode); setPhase('consent');
  });
  const grant = () => perform(async () => {
    await api('/consents', 'POST', { scopes: allScopes.filter((_, i) => choices[i]), days });
    accept(await api<Summary>('/summary')); setPhase('app'); setTab('plan');
  });
  const save = () => perform(async () => {
    if (!plan) return;
    if (![...document.querySelectorAll('input')].every(input => input.reportValidity())) return;
    accept(await api<Summary>('/plan', 'PUT', { ...plan, confirmed: true }));
    setDraft(null); setNotice(c.planSaved); setTab('overview');
  });
  const move = (operation: 'transfer' | 'withdraw' | 'pay-emergency') => perform(async () => {
    let value = operation === 'transfer' ? 0 : toMinor(amount);
    let recommendation_id: string | undefined;
    if (operation === 'transfer') {
      const rec = pendingDeposit.current ?? await api<{ id: string; amount_minor: number }>('/recommendation', 'POST');
      pendingDeposit.current = rec;
      value = rec.amount_minor; recommendation_id = rec.id;
    }
    const fingerprint = `${operation}:${value}:${recommendation_id ?? ''}`;
    const key = retry.current[fingerprint] ?? crypto.randomUUID();
    retry.current[fingerprint] = key;
    const result = await api<Wallet & { refill?: { weekly_minor: number; estimated_weeks: number } | null }>(
      operation === 'pay-emergency' ? '/sandbox/pay-emergency' : `/buffer/${operation}`, 'POST',
      { amount_minor: value, idempotency_key: key, recommendation_id: recommendation_id ?? null, confirmed: true }).catch(error => {
        if (error instanceof ApiError && error.status < 500) {
          delete retry.current[fingerprint];
          if (operation === 'transfer') pendingDeposit.current = null;
        }
        throw error;
      });
    delete retry.current[fingerprint];
    if (operation === 'transfer') pendingDeposit.current = null;
    setWallet(result);
    if (operation === 'withdraw') { setWithdrawalMade(true); setRefill(result.refill ?? null); }
    setNotice(operation === 'transfer' ? c.depositDone : operation === 'withdraw' ? c.withdrawn : c.paymentDone);
    await refresh();
  });
  const parse = () => perform(async () => {
    const requestController = new AbortController();
    controller.current = requestController;
    const response = await api<Draft>('/assistant/parse', 'POST', { text }, requestController.signal);
    if (!requestController.signal.aborted) setDraft(response);
    if (controller.current === requestController) controller.current = null;
  });
  const discard = () => perform(async () => {
    controller.current?.abort(); controller.current = null; setDraft(null);
    await api('/assistant/draft', 'DELETE');
  });
  const applyDraft = () => perform(async () => {
    if (!plan || !draft) return;
    const bills: Bill[] = draft.proposal.candidates.map(item => {
      if (!item.amount || !item.due_date || item.recurrence === 'unknown' || item.included_in_daily === null) throw new Error(c.reviewNote);
      return { id: crypto.randomUUID(), label: item.label, amount_minor: toMinor(item.amount),
        due_date: item.due_date, recurrence: item.recurrence, included_in_daily: item.included_in_daily, paid: false };
    });
    if (!bills.length && !draft.proposal.expected_income_date) throw new Error(c.reviewNote);
    const next = { ...plan, confirmed: true, obligations: [...plan.obligations, ...bills],
      next_expected_income: draft.proposal.expected_income_date ?? plan.next_expected_income };
    accept(await api<Summary>('/assistant/apply', 'POST', { draft_id: draft.draft_id, plan: next }));
    setDraft(null); setText(''); setNotice(c.planSaved); setTab('overview');
  });
  const editBill = (index: number, values: Partial<Bill>) => setPlan(old => old && ({ ...old, obligations: old.obligations.map((bill, i) => i === index ? { ...bill, ...values } : bill) }));
  const updateCandidate = (index: number, field: string, value: unknown) => setDraft(old => old && ({ ...old, proposal: { ...old.proposal, candidates: old.proposal.candidates.map((item, i) => i === index ? { ...item, [field]: value } : item) } }));
  const revoke = () => perform(async () => {
    await api('/consents', 'DELETE'); setChoices(initialChoices); setDraft(null); setData(null); setPlan(null); setRefill(null); setNotice(c.revoked);
  });
  const destructive = () => perform(async () => {
    if (confirmAction === 'delete') { await api('/privacy/data', 'DELETE'); setSession(''); setPhase('start'); }
    else { await api('/sandbox/reset', 'POST'); setPhase('consent'); }
    setChoices(initialChoices); setData(null); setPlan(null); setDraft(null); setAudit(null); setText(''); setRefill(null); setWithdrawalMade(false); setConfirmAction(null); retry.current = {};
    pendingDeposit.current = null;
    setWallet({ available_minor: 200000, buffer_minor: 50000 });
  });

  return <div className="app-shell">
    <header className="topbar"><a className="wordmark" href="#" onClick={e => e.preventDefault()}><span className="logo">i</span>{c.brand}</a><span className="demo-badge">{c.notice}</span></header>
    {phase === 'start' ? <main className="landing"><p className="eyebrow">{c.eyebrow}</p><h1>{c.hero}</h1><p className="lead">{c.intro}</p><button className="primary" onClick={start} disabled={busy}>{busy ? c.busy : c.start} <span aria-hidden="true">↗</span></button><p className="muted">{c.startNote}</p><div className="landing-cards"><article><span className="step">01</span><h2>{c.reserve}</h2><p>{c.overviewIntro}</p></article><article><span className="step">02</span><h2>{c.suggestion}</h2><p>{c.suggestionNote}</p></article><article><span className="step">03</span><h2>{c.emergency}</h2><p>{c.emergencyIntro}</p></article></div><p className="scope">{c.scope}</p></main>
    : phase === 'consent' ? <main className="consent"><p className="eyebrow">{c.notice}</p><h1>{c.consentTitle}</h1><p className="lead">{c.consentIntro}</p>
      {[['transactions', 'transactionsNote'], ['balances', 'balancesNote'], ['transfers', 'transfersNote'], ['ai', 'aiNote']].map(([title, description], i) => <label className="consent-option" key={title}><input type="checkbox" checked={choices[i]} onChange={e => setChoices(old => old.map((v, j) => j === i ? e.target.checked : v))} /><span><strong>{c[title as keyof typeof c]}</strong><small>{c[description as keyof typeof c]}</small></span></label>)}
      <label className="field">{c.expiry}<select value={days} onChange={e => setDays(Number(e.target.value))}>{[30, 90, 180].map(day => <option key={day} value={day}>{day} {c.days}</option>)}</select></label>
      <button className="primary" disabled={busy || !choices[0] || !choices[1]} onClick={grant}>{busy ? c.busy : c.continue}</button></main>
    : <div className="workspace"><aside><nav aria-label="Main navigation">{(['overview', 'plan', 'emergency', 'privacy'] as Tab[]).map((item, i) => <button key={item} aria-current={tab === item ? 'page' : undefined} onClick={() => { setTab(item); setError(''); setNotice(''); }}><span className="nav-number">0{i + 1}</span>{c[item]}</button>)}</nav><div className="sidebar-note"><span className="status-dot" />{c.notice}<p>{c.scope}</p></div><button className="text-button" onClick={() => setConfirmAction('reset')}>{c.reset}</button></aside>
      <main className="dashboard">
        <div className="page-heading"><div><p className="eyebrow">{c.brand} / {c[tab]}</p><h1>{tab === 'overview' ? c.greeting : tab === 'plan' ? c.planTitle : tab === 'emergency' ? c.emergencyTitle : c.privacyTitle}</h1></div><span className="date-chip">28 SEP 2026</span></div>
        {tab === 'overview' && (data ? <>
          <p className="lead compact">{c.overviewIntro}</p>
          <div className="overview-grid"><section className="buffer-card"><p>{c.buffer}</p><div className="big-money">{money(wallet.buffer_minor)}</div><p>{data.buffer_days?.toFixed(1) ?? '—'} {c.cover}</p><div className="buffer-track"><span style={{ width: `${Math.min(100, data.stage ? wallet.buffer_minor / data.stage.target_minor * 100 : 0)}%` }} /></div><div className="split"><span>{c.goal}</span><strong>{data.stage?.days ?? '—'} {c.days}</strong></div><div className="stage-ladder">{[7, 14, 30, 60, 90].map(day => <span className={(data.buffer_days ?? 0) >= day ? 'reached' : ''} key={day}>{day}d</span>)}</div><p className="fine">{c.etaUnavailable}</p></section>
          <div className="stack"><section className="card stat"><p>{c.wallet}</p><strong>{money(wallet.available_minor)}</strong></section><section className="card stat"><p>{c.reserve}</p><strong>{money(data.reserve_minor)}</strong><small>{c.through} {data.protected_through}</small></section></div></div>
          <section className="saving-card"><div><p className="eyebrow">{c.suggestion}</p><strong>{money(data.amount_minor)}</strong><p>{data.amount_minor ? c.suggestionNote : c.noSurplus}</p></div><button className="primary" onClick={() => move('transfer')} disabled={busy || !data.amount_minor || !choices[2]}>{busy ? c.busy : c.confirmDeposit}</button></section>
          <div className="two-col"><section className="card"><h2>{c.why}</h2>{data.reasons.map(reason => <p key={reason}>{reason}</p>)}<details><summary>{c.review}</summary>{data.guardrails.map(check => <p className="fine" key={check.name}>{check.passed ? '✓' : '×'} {check.detail}</p>)}</details></section><section className="card"><h2>{c.room}</h2><strong className="medium-money">{data.room_per_day_minor === null ? c.unavailable : money(data.room_per_day_minor)}</strong><p className="fine">{c.roomNote}</p></section></div>
          <section className="card scenarios"><h2>{c.scenarios}</h2><p className="fine">{c.scenariosNote}</p><div className="scenario-row">{data.coverage.scenarios.map(s => <div key={s.amount_minor}><strong>{money(s.amount_minor)}</strong><span>{s.covered ? c.covered : c.notCovered}</span></div>)}</div></section>
        </> : <section className="card"><p>{c.consentRequired}</p><button onClick={() => setPhase('consent')}>{c.editConsent}</button></section>)}

        {tab === 'plan' && (plan ? <><p className="lead compact">{c.planIntro}</p><section className="assistant-card"><div><span className="ai-tag">AI</span><h2>{c.assistantTitle}</h2><p>{c.assistantIntro}</p></div><p className="fine">{modelMode === 'disabled' ? c.aiOff : c.aiOn}</p>{!choices[3] && <p className="fine">{c.aiConsentNeeded}</p>}
          <label className="field"><span className="sr-only">{c.assistantTitle}</span><textarea value={text} maxLength={2000} onChange={e => setText(e.target.value)} placeholder={c.assistantPlaceholder} /></label><div className="actions"><button className="primary" disabled={busy || !choices[3] || !text.trim()} onClick={parse}>{busy ? c.busy : c.parse}</button>{busy && <button onClick={discard}>{c.cancel}</button>}</div>
          {draft && <div className="draft"><h3>{c.review}</h3><p>{c.reviewNote}</p><p>{draft.proposal.clarification}</p>{draft.proposal.candidates.map((item, index) => <div className="bill" key={index}><p className="fine">{c.source}: “{item.source_excerpt}”</p><div className="form-grid"><label className="field">{c.label}<input value={item.label} onChange={e => updateCandidate(index, 'label', e.target.value)} /></label><label className="field">{c.amount}<input inputMode="decimal" value={item.amount ?? ''} onChange={e => updateCandidate(index, 'amount', e.target.value)} /></label><label className="field">{c.due}<input type="date" value={item.due_date ?? ''} onChange={e => updateCandidate(index, 'due_date', e.target.value)} /></label><label className="field">{c.recurrence}<select value={item.recurrence} onChange={e => updateCandidate(index, 'recurrence', e.target.value)}><option value="unknown">{c.select}</option><option value="one_off">{c.once}</option><option value="monthly">{c.monthly}</option></select></label><label className="field">{c.included}<select value={item.included_in_daily === null ? '' : String(item.included_in_daily)} onChange={e => updateCandidate(index, 'included_in_daily', e.target.value === '' ? null : e.target.value === 'true')}><option value="">{c.select}</option><option value="true">{c.yes}</option><option value="false">{c.no}</option></select></label></div></div>)}{draft.proposal.expected_income_date && <label className="field">{c.incomeEstimate}<input type="date" value={draft.proposal.expected_income_date} onChange={e => setDraft({ ...draft, proposal: { ...draft.proposal, expected_income_date: e.target.value } })} /></label>}<div className="actions"><button className="primary" disabled={busy || draft.proposal.status === 'unsupported' || draft.proposal.candidates.some(item => !item.amount || !item.due_date || item.recurrence === 'unknown' || item.included_in_daily === null) || (!draft.proposal.candidates.length && !draft.proposal.expected_income_date)} onClick={applyDraft}>{c.applyDraft}</button><button disabled={busy} onClick={discard}>{c.discard}</button></div></div>}
        </section><section className="card"><div className="form-grid"><label className="field">{c.daily}<MoneyInput key={`daily-${plan.version}`} value={plan.routine_daily_minor} onValue={value => setPlan({ ...plan, routine_daily_minor: value })} /></label><label className="field">{c.nextIncome}<input type="date" value={plan.next_expected_income} onChange={e => setPlan({ ...plan, next_expected_income: e.target.value })} /></label></div><div className="split"><h2>{c.bills}</h2><button onClick={() => setPlan({ ...plan, obligations: [...plan.obligations, { id: crypto.randomUUID(), label: '', amount_minor: 0, due_date: '2026-09-29', recurrence: 'one_off', included_in_daily: false, paid: false }] })}>{c.addBill}</button></div>
          {plan.obligations.map((bill, index) => <div className="bill" key={bill.id}><div className="form-grid"><label className="field">{c.label}<input value={bill.label} onChange={e => editBill(index, { label: e.target.value })} /></label><label className="field">{c.amount}<MoneyInput key={`${bill.id}-${plan.version}`} value={bill.amount_minor} onValue={value => editBill(index, { amount_minor: value })} /></label><label className="field">{c.due}<input type="date" value={bill.due_date} onChange={e => editBill(index, { due_date: e.target.value })} /></label><label className="field">{c.recurrence}<select value={bill.recurrence} onChange={e => editBill(index, { recurrence: e.target.value as Bill['recurrence'] })}><option value="one_off">{c.once}</option><option value="monthly">{c.monthly}</option></select></label></div><div className="bill-options"><label><input type="checkbox" checked={bill.included_in_daily} onChange={e => editBill(index, { included_in_daily: e.target.checked })} /> {c.included}</label><label><input type="checkbox" checked={bill.paid} onChange={e => editBill(index, { paid: e.target.checked })} /> {c.paid}</label><button className="text-button" onClick={() => setPlan({ ...plan, obligations: plan.obligations.filter((_, i) => i !== index) })}>{c.remove}</button></div></div>)}
          <button className="primary" disabled={busy} onClick={save}>{busy ? c.busy : c.confirmPlan}</button></section></> : <section className="card"><p>{c.consentRequired}</p><button onClick={() => setPhase('consent')}>{c.editConsent}</button></section>)}

        {tab === 'emergency' && <><p className="lead compact">{c.emergencyIntro}</p><div className="two-col"><section className="buffer-card"><p>{c.buffer}</p><div className="big-money">{money(wallet.buffer_minor)}</div><p>{c.wallet}: {money(wallet.available_minor)}</p></section><section className="card"><label className="field">{c.amount}<input inputMode="decimal" value={amount} onChange={e => setAmount(e.target.value)} /></label><button className="primary" disabled={busy} onClick={() => move('withdraw')}>{c.withdraw}</button><p className="fine">{c.paymentNote}</p><button disabled={busy} onClick={() => move('pay-emergency')}>{c.pay}</button></section></div>{withdrawalMade && <section className="card"><h2>{c.refill}</h2>{refill ? <p><strong>{money(refill.weekly_minor)}</strong> {c.perWeek} · {refill.estimated_weeks} {c.weeks}</p> : <p>{c.refillPaused}</p>}<p className="fine">{c.refillNote}</p></section>}</>}

        {tab === 'privacy' && <><p className="lead compact">{c.privacyIntro}</p><section className="card"><h2>{c.consentTitle}</h2><div className="actions"><button onClick={() => setPhase('consent')}>{c.editConsent}</button><button disabled={busy} onClick={revoke}>{c.revoke}</button></div></section><section className="card"><h2>{c.audit}</h2><p className="fine">{c.auditNote}</p><button disabled={busy} onClick={() => perform(async () => setAudit(await api('/audit')))}>{c.audit}</button>{audit && <><p className={audit.verified ? 'success-text' : 'error-text'}>{audit.verified ? c.verified : c.auditFailed}</p><ul className="audit-list">{audit.entries.slice(-12).reverse().map((entry, i) => <li key={i}>{entry.action}</li>)}</ul></>}</section><section className="card"><h2>{c.delete}</h2><p>{c.deleteNote}</p><button className="danger" onClick={() => setConfirmAction('delete')}>{c.delete}</button></section></>}
        <footer>{c.footer}</footer>
      </main></div>}
    {error && <div className="toast error" role="alert">{error}<button aria-label="Dismiss error" onClick={() => setError('')}>×</button></div>}
    {notice && <div className="toast success" role="status">{notice}<button aria-label="Dismiss notification" onClick={() => setNotice('')}>×</button></div>}
    {confirmAction && <div className="dialog-backdrop"><section className="dialog" role="dialog" aria-modal="true" aria-labelledby="confirm-title"><h2 id="confirm-title">{confirmAction === 'delete' ? c.confirmDelete : c.confirmReset}</h2><p>{confirmAction === 'delete' ? c.deleteNote : c.scope}</p><div className="actions"><button className="primary" disabled={busy} onClick={destructive}>{confirmAction === 'delete' ? c.delete : c.reset}</button><button onClick={() => setConfirmAction(null)}>{c.cancel}</button></div></section></div>}
  </div>;
}

function MoneyInput({ value, onValue }: { value: number; onValue: (value: number) => void }) {
  const [text, setText] = useState((value / 100).toString());
  return <input inputMode="decimal" value={text} onChange={event => {
    setText(event.target.value);
    try { const parsed = toMinor(event.target.value); event.target.setCustomValidity(''); onValue(parsed); }
    catch { event.target.setCustomValidity('Enter an amount with up to two decimal places.'); }
  }} onBlur={event => event.target.reportValidity()} />;
}
