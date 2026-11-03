import WalletDemo from './nearby/WalletDemo';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode>{window.location.pathname === '/nearby' ? <WalletDemo /> : <App />}</React.StrictMode>);
