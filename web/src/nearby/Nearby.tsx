import { useEffect, useState } from 'react';
import { money, toMinor } from '../api';
import './nearby.css';

export type NearbyHost = {
  request: <T>(path: string, method?: string, body?: unknown) => Promise<T>;
  openSavings: () => void;
  savings?: { contribution: number; essentials: number; daily: number; asOf: string };
  brand?: string;
};
type Kind = 'helpful' | 'confirmed' | 'changed' | 'flagged';
type Report = { id: string; item: string; quantity: string; store: string; area: string;
  price_minor: number; observed_at: number; conditions: string; photo: string; mine: boolean;
  stale: boolean; review_pending: boolean; counts: Record<Kind, number>; my_reactions: Kind[] };
type Feed = { reports: Report[]; points: number; identity: string };

export default function Nearby({ host, embedded = false }: { host: NearbyHost; embedded?: boolean }) {
  const [feed, setFeed] = useState<Feed>({reports: [], points: 0, identity: ''});
  const [view, setView] = useState<'all' | 'confirmed' | 'mine'>('all');
  const [query, setQuery] = useState(''); const [area, setArea] = useState('Demo Central');
  const [busy, setBusy] = useState(false); const [message, setMessage] = useState('');
  const [error, setError] = useState(''); const [photo, setPhoto] = useState('');
  const [publishing, setPublishing] = useState(false); const [confirm, setConfirm] = useState<Report | null>(null);
  const refresh = async () => setFeed(await host.request<Feed>('/nearby'));
  useEffect(() => { void refresh().catch(e => setError(String(e))); }, [host.request]);
  async function act(work: () => Promise<void>) {
    setBusy(true); setError(''); setMessage('');
    try { await work(); await refresh(); } catch(e) { setError(e instanceof Error ? e.message : 'Please try again.'); }
    finally { setBusy(false); }
  }
  async function react(r: Report, kind: Kind) {
    await act(async () => { await host.request(`/nearby/${r.id}/react`, 'POST', {kind});
      setMessage(kind === 'confirmed' ? 'Thank you. Your observation helps neighbors plan. The reporter can earn up to 15 demo points per report.' : kind === 'helpful' ? 'Your thanks was recorded.' : 'Thank you for keeping local information useful.'); setConfirm(null); });
  }
  async function choosePhoto(file?: File) {
    if (!file) { setPhoto(''); return; }
    if (!['image/jpeg','image/png','image/webp'].includes(file.type) || file.size > 5000000) { setError('Choose a JPEG, PNG or WebP under 5 MB.'); return; }
    setBusy(true);
    try {
      const bitmap = await createImageBitmap(file); const canvas = document.createElement('canvas');
      const scale = Math.min(1, 900 / Math.max(bitmap.width, bitmap.height));
      canvas.width = Math.max(1,Math.round(bitmap.width*scale)); canvas.height = Math.max(1,Math.round(bitmap.height*scale));
      canvas.getContext('2d')!.drawImage(bitmap,0,0,canvas.width,canvas.height); bitmap.close();
      const encoded = canvas.toDataURL('image/jpeg',0.65);
      if(encoded.length > 450000) throw new Error('Photo is too detailed. Choose a smaller image.');
      setPhoto(encoded); setError('');
    } catch(e) { setError(e instanceof Error ? e.message : 'Could not read photo.'); }
    finally { setBusy(false); }
  }
  const filtered = feed.reports.filter(r => r.area === area && (view === 'all' || (view === 'mine' ? r.mine : r.counts.confirmed > 0)) && `${r.item} ${r.store} ${r.quantity}`.toLowerCase().includes(query.toLowerCase()));
  return <section className="nearby" aria-label="Ipon Nearby">
    <header className="nearby-masthead">{!embedded && <a className="nearby-wordmark" href="#" onClick={e=>e.preventDefault()}>ipon<span>nearby</span><i /></a>}<label className="nearby-search">Search your neighborhood<input aria-label="Search local prices" placeholder="Search rice, eggs, local stores…" value={query} onChange={e=>setQuery(e.target.value)} /></label><button className="nearby-avatar" aria-label="Show my contributions" onClick={()=>setView('mine')}>You</button></header>
    <div className="nearby-layout"><aside className="nearby-sidebar"><label>Your neighborhood<select value={area} onChange={e=>setArea(e.target.value)}><option>Demo Central</option><option>Demo Riverside</option></select></label><nav aria-label="Nearby navigation"><button aria-current={view === 'all' ? 'page' : undefined} onClick={()=>setView('all')}>⌂ <span>Neighborhood</span></button><button aria-current={view === 'confirmed' ? 'page' : undefined} onClick={()=>setView('confirmed')}>✓ <span>Confirmed prices</span></button><button aria-current={view === 'mine' ? 'page' : undefined} onClick={()=>setView('mine')}>♧ <span>My contributions</span></button><button onClick={host.openSavings}>◉ <span>Emergency savings</span></button></nav><button className="primary" onClick={()=>setPublishing(true)}>＋ Share a price</button><p className="fine">Small discoveries.<br/>A little more room to save.</p></aside><div className="nearby-center"><div className="nearby-feed-title"><div><p className="eyebrow">YOUR NEIGHBORHOOD</p><h1>{view === 'all' ? 'Around you' : view === 'mine' ? 'Your contributions' : 'Confirmed locally'}</h1></div><div>{view !== 'all' && <button onClick={()=>setView('all')}>← All finds</button>}<button disabled={busy} onClick={()=>void act(refresh)}>↻ Refresh</button></div></div><button className="nearby-composer" onClick={()=>setPublishing(true)}><span className="nearby-avatar">You</span><span>Found a good price? Tell your neighbors.</span><b>＋</b></button><div className="nearby-feed-tabs"><button aria-pressed={view==='all'} onClick={()=>setView('all')}>Latest finds</button><button aria-pressed={view==='confirmed'} onClick={()=>setView('confirmed')}>Community confirmed</button><button aria-pressed={view==='mine'} onClick={()=>setView('mine')}>Your posts</button></div>
    {error && <p role="alert" className="error-text">{error}</p>}{message && <p role="status" className="nearby-success">{message}</p>}
    {publishing && <form className="nearby-form" onSubmit={e=>{e.preventDefault();const form=e.currentTarget;const f=new FormData(form);void act(async()=>{await host.request('/nearby','POST',{item:f.get('item'),quantity:f.get('quantity'),store:f.get('store'),area,price_minor:toMinor(String(f.get('price'))),observed_at:Math.floor(new Date(String(f.get('observed'))).getTime()/1000),conditions:f.get('conditions'),photo});form.reset();setPhoto('');setPublishing(false);setMessage('Finding shared. Neighbors can thank you and independently confirm the price.');});}}>
      <button type="button" className="ipon-back" onClick={()=>{setPublishing(false);setPhoto('');}}>← Back to feed</button><h2>Found a useful price? Help a neighbor.</h2><p>Use fictional stores and synthetic examples in this demonstration.</p><div className="nearby-fields">
      <label>Exact item / brand<input name="item" required minLength={2} maxLength={100} /></label><label>Pack size / quantity<input name="quantity" placeholder="1 kg, 12 medium eggs…" required maxLength={60} /></label><label>Store and branch<input name="store" required minLength={2} maxLength={100} /></label><label>Price (PHP)<input name="price" type="number" min="0.01" step="0.01" required /></label><label>Observed at<input name="observed" type="datetime-local" required /></label><label>Conditions / promotion<input name="conditions" maxLength={200} placeholder="Regular price, member price, expiry…" /></label></div>
      <label>Optional shelf or product photo<input type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>void choosePhoto(e.target.files?.[0])} /></label><p className="fine">Use synthetic images. No faces, receipt identifiers or private details. Images are resized and re-encoded before upload.</p>{photo && <img className="nearby-photo" src={photo} alt="Your price report preview" />}<button className="primary" disabled={busy}>Publish finding</button><button type="button" onClick={()=>{setPublishing(false);setPhoto('');}}>Cancel</button>
    </form>}
    <div className="nearby-feed">{filtered.length === 0 && <div className="nearby-empty"><h2>Be the first helpful neighbor.</h2><p>No matching reports yet. Share a synthetic price observation to try the community flow.</p></div>}{filtered.map(r=><article className="nearby-report" key={r.id}>

      <div className="nearby-report-body"><div className="nearby-author"><span className="nearby-avatar">{r.mine ? 'You' : 'N'}</span><div><strong>{r.mine ? 'You shared a find' : 'A neighbor shared a find'}</strong><small>{r.area} · {new Date(r.observed_at*1000).toLocaleDateString()}</small></div><span className="nearby-tag">Price find</span></div><div className="nearby-price"><h2>{r.item}</h2><strong>{money(r.price_minor)}</strong></div><p>{r.quantity} · {r.store}</p><p className="fine">Observed {new Date(r.observed_at*1000).toLocaleString()} · {r.stale ? 'Older than 24 hours — recheck' : 'Recent observation'}</p>{r.conditions && <p>{r.conditions}</p>}
      {r.photo && <img className="nearby-photo" src={r.photo} alt={`Price observation for ${r.item}`} loading="lazy" />}<p className="nearby-proof">{r.counts.confirmed} same-price confirmations · {r.counts.changed} changed-price reports</p>{r.review_pending && <p>Hidden from others pending moderation review.</p>}
      <div className="nearby-actions"><button disabled={busy||r.mine||r.my_reactions.includes('helpful')} onClick={()=>void react(r,'helpful')}>♡ Helpful · {r.counts.helpful}</button><button disabled={busy||r.mine||r.stale||r.my_reactions.includes('confirmed')} onClick={()=>setConfirm(r)}>✓ Same price</button><button disabled={busy||r.mine||r.my_reactions.includes('changed')} onClick={()=>void react(r,'changed')}>Price changed</button><button disabled={busy||r.mine||r.my_reactions.includes('flagged')} onClick={()=>void react(r,'flagged')}>Flag</button>{r.mine && <button disabled={busy} onClick={()=>void act(async()=>{await host.request(`/nearby/${r.id}`,'DELETE');setMessage('Your report and its reactions were removed.');})}>Delete my report</button>}</div></div>
    </article>)}</div>
    </div><aside className="nearby-right"><section className="nearby-reputation"><p className="eyebrow">YOUR LOCAL IMPACT</p><strong>{feed.points}</strong><p>contribution points</p><small>Help neighbors find useful prices.<br/>Earn recognition for confirmed finds.</small></section>
    <div className="nearby-context">{host.savings ? <><p>Your suggested contribution <strong>{money(host.savings.contribution)}</strong></p><p>Based on {money(host.savings.essentials)} reserved essentials, including {money(host.savings.daily)} daily needs.</p><small>Savings scenario: {host.savings.asOf}. Local reports use their actual observation dates.</small></> : <p>Review your expenses to see your savings recommendation alongside local prices.</p>}<button onClick={host.openSavings}>Review savings plan →</button><p className="fine">A cheaper reported price is not money saved. Review actual expenses before changing your plan. No automatic transfers.</p></div>
    <p className="nearby-demo">Synthetic community demo · No verified residents or real store coverage · Points have no cash value</p>
<section className="nearby-guide"><h3>Better together</h3><p>Share the exact item, pack size and store. Confirm prices you’ve seen yourself.</p><p>♡ A thank-you makes someone’s day.</p></section></aside></div>
    <p className="fine">{feed.identity} · Likes express appreciation; confirmations record an observation, not guaranteed truth. Reporters receive 5 demo points per distinct confirming identity, capped at 15 per report. Synthetic identities can be recreated; this is not fraud-resistant.</p>
    <nav className="nearby-mobile-nav" aria-label="Mobile Nearby navigation"><button onClick={()=>{setView('all');window.scrollTo({top:0,behavior:'smooth'});}} aria-current={view==='all'?'page':undefined}>⌂<small>Home</small></button><button onClick={()=>setView('confirmed')}>✓<small>Confirmed</small></button><button onClick={()=>setPublishing(true)}>＋<small>Post</small></button><button onClick={host.openSavings}>◉<small>Savings</small></button><button onClick={()=>setView('mine')}>♧<small>You</small></button></nav>
    {confirm && <div className="dialog-backdrop"><section className="dialog" role="dialog" aria-modal="true" aria-label="Confirm observed price"><h2>Did you see this price yourself?</h2><p>{confirm.item} · {confirm.quantity} · {money(confirm.price_minor)} at {confirm.store}</p><p>Confirm only if you independently observed the same item, quantity, price and conditions. In this demo, role-play a second shopper.</p><button disabled={busy} onClick={()=>void react(confirm,'confirmed')}>I observed the same price</button><button onClick={()=>setConfirm(null)}>Cancel</button></section></div>}
  </section>;
}
