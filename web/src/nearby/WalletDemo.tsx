import { useEffect, useState } from 'react';
import Nearby from './Nearby';

let currentToken = '';
async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const response = await fetch('/api/v1'+path,{method,headers:{'Content-Type':'application/json','X-Demo-Session':currentToken},body:body === undefined ? undefined : JSON.stringify(body)});
  const result = await response.json(); if(!response.ok) throw new Error(result.error?.message ?? 'Request failed'); return result as T;
}
export default function WalletDemo() {
  const [ready,setReady]=useState(false); const [who,setWho]=useState('Mika'); const [error,setError]=useState('');
  async function select(name: string) {
    setReady(false);setError('');
    try { const key='ipon-nearby-demo-'+name; let token=sessionStorage.getItem(key);
      if(!token){const r=await request<{token:string}>('/sandbox/start','POST');token=r.token;sessionStorage.setItem(key,token);}
      currentToken=token; await request('/wallet');setWho(name);setReady(true);
    } catch(e){sessionStorage.removeItem('ipon-nearby-demo-'+name);setError(String(e));}
  }
  useEffect(()=>{void select('Mika');},[]);
  return <div><div className="wallet-demo-strip"><span>E-Wallet integration demo · Synthetic community</span><a href="/">Ipon Buffer savings</a><button disabled={!ready&&!error} onClick={()=>void select(who==='Mika'?'Sam':'Mika')}>Demo neighbor: {who} · switch to {who==='Mika'?'Sam':'Mika'}</button>{error&&<p role="alert">{error} <button onClick={()=>void select(who)}>Retry</button></p>}</div>{ready&&<Nearby key={who} host={{request,brand:'E-Wallet',openSavings:()=>{window.location.href='/';}}}/>}</div>;
}
