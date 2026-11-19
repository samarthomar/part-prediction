import React, { useState } from 'react';
import { Lock, KeyRound, Eye, EyeOff, ShieldCheck, ArrowRight } from 'lucide-react';

const GELogo = ({ height = 48 }) => (
  <svg viewBox="0 0 400 100" height={height} xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(50, 50)">
      <circle cx="0" cy="0" r="42" fill="none" stroke="white" strokeWidth="3"/>
      <circle cx="0" cy="0" r="36" fill="none" stroke="white" strokeWidth="1.5"/>
      <text x="0" y="14" textAnchor="middle" fontFamily="Georgia, serif" fontWeight="bold" fontSize="46" fill="white" letterSpacing="-2">GE</text>
    </g>
    <text x="115" y="58" fontFamily="'Inter', sans-serif" fontWeight="700" fontSize="30" fill="white" letterSpacing="3">GE APPLIANCES</text>
  </svg>
);

export default function LoginScreen({ onLogin }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Read password from Vercel environment variable, fallback to default 'ge2026'
  const expectedPassword = import.meta.env.VITE_APP_PASSWORD || import.meta.env.VITE_PASSWORD || 'ge2026';

  const handleSubmit = (e) => {
    e.preventDefault();
    if (password.trim() === expectedPassword.trim()) {
      localStorage.setItem('ge_auth_unlocked', 'true');
      onLogin();
    } else {
      setError(true);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'var(--color-bg-main)',
      backgroundImage: 'radial-gradient(circle at 50% 30%, rgba(0, 86, 179, 0.15) 0%, rgba(11, 17, 32, 0.95) 70%)',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '440px',
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        borderRadius: '16px',
        padding: '40px 32px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 30px rgba(0, 86, 179, 0.2)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Accent top bar */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: 'linear-gradient(90deg, var(--color-ge-primary-blue), var(--color-ge-orange))'
        }} />

        {/* Header / Logo */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ display: 'inline-block', marginBottom: '16px' }}>
            <GELogo height={42} />
          </div>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: 'rgba(0, 86, 179, 0.15)',
            border: '1px solid rgba(74, 144, 217, 0.3)',
            borderRadius: '20px',
            padding: '4px 12px',
            fontSize: '0.75rem',
            color: 'var(--color-ge-light-blue)',
            fontWeight: 600,
            marginBottom: '12px'
          }}>
            <ShieldCheck size={14} />
            RESTRICTED ACCESS PORTAL
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: '8px' }}>
            AI Parts Recommendation
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
            Please enter your authorized security key to access the predictive service intelligence portal.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              fontSize: '0.8rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              color: 'var(--color-text-secondary)',
              marginBottom: '8px'
            }}>
              Access Key
            </label>
            <div style={{ position: 'relative' }}>
              <div style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--color-text-muted)'
              }}>
                <KeyRound size={18} />
              </div>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (error) setError(false);
                }}
                placeholder="Enter password..."
                autoFocus
                style={{
                  width: '100%',
                  padding: '12px 40px 12px 40px',
                  backgroundColor: 'rgba(255, 255, 255, 0.04)',
                  border: error ? '1px solid var(--color-error)' : '1px solid var(--color-border)',
                  borderRadius: '8px',
                  color: 'var(--color-text-primary)',
                  fontSize: '0.95rem',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  boxShadow: error ? '0 0 10px rgba(239, 68, 68, 0.2)' : 'none'
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'var(--color-text-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {error && (
              <p style={{
                fontSize: '0.8rem',
                color: 'var(--color-error)',
                marginTop: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                Incorrect password. Please verify and try again.
              </p>
            )}
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{
              width: '100%',
              padding: '12px 16px',
              fontSize: '0.95rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              borderRadius: '8px'
            }}
          >
            <span>Unlock Portal</span>
            <ArrowRight size={18} />
          </button>
        </form>

        {/* Footer info */}
        <div style={{
          marginTop: '28px',
          paddingTop: '20px',
          borderTop: '1px solid var(--color-border)',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--color-text-muted)'
        }}>
          <span>Protected demo environment &bull; Configured via Vercel (<code>VITE_APP_PASSWORD</code>)</span>
        </div>
      </div>
    </div>
  );
}
