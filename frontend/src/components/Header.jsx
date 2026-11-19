import React from 'react';
import { Lock } from 'lucide-react';

const GELogo = ({ height = 40 }) => (
  <svg viewBox="0 0 400 100" height={height} xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(50, 50)">
      <circle cx="0" cy="0" r="42" fill="none" stroke="white" strokeWidth="3"/>
      <circle cx="0" cy="0" r="36" fill="none" stroke="white" strokeWidth="1.5"/>
      <text x="0" y="14" textAnchor="middle" fontFamily="Georgia, serif" fontWeight="bold" fontSize="46" fill="white" letterSpacing="-2">GE</text>
    </g>
    <text x="115" y="58" fontFamily="'Inter', sans-serif" fontWeight="700" fontSize="30" fill="white" letterSpacing="3">GE APPLIANCES</text>
  </svg>
);

export default function Header({ activeTab, setActiveTab, onLogout }) {
  return (
    <header className="header">
      <div className="header-left">
        <GELogo height={36} />
        <div style={{ width: '1px', height: '32px', backgroundColor: 'var(--color-border)', margin: '0 8px' }}></div>
        <div className="header-title-container">
          <h1 className="header-title">AI Parts Recommendation</h1>
          <span className="header-subtitle">Intelligent Service Diagnostics Prototype</span>
        </div>
      </div>
      
      <div className="nav-tabs" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button 
          className={`nav-tab ${activeTab === 'recommendation' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendation')}
        >
          AI Recommendation
        </button>
        <button 
          className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Operations Dashboard
        </button>
        {onLogout && (
          <button 
            className="nav-tab"
            onClick={onLogout}
            title="Lock Portal / Sign Out"
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '6px', 
              color: 'var(--color-text-muted)',
              padding: '8px 12px'
            }}
          >
            <Lock size={15} />
            <span>Lock</span>
          </button>
        )}
      </div>
    </header>
  );
}
