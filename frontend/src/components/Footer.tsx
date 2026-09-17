import React from 'react';
import { ShieldCheck, Sparkles } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer
      style={{
        marginTop: 'auto',
        paddingTop: '36px',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        fontSize: '0.8rem',
        color: '#64748b',
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
          color: '#fbbf24',
          fontWeight: 700,
        }}
      >
        <Sparkles size={14} />
        <span>Raaso — Find your people. Find your rhythm.</span>
      </div>

      <div
        style={{
          maxWidth: '480px',
          margin: '0 auto',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: '8px',
          padding: '10px 14px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          textAlign: 'left',
        }}
      >
        <ShieldCheck size={24} color="#10b981" style={{ flexShrink: 0 }} />
        <span style={{ fontSize: '0.74rem', color: '#94a3b8' }}>
          <strong>Safety First:</strong> Raaso does not share private phone numbers or addresses.
          Always coordinate meeting points at the public festival grounds or main ticket entrance.
        </span>
      </div>

      <p style={{ fontSize: '0.72rem' }}>
        Built for Garba and Dandiya festival-goers across Gujarat, Maharashtra & beyond.
      </p>
    </footer>
  );
};

