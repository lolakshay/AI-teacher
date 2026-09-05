import React from 'react';
import { Sparkles, Lightbulb, Compass, AlertCircle } from 'lucide-react';

export default function AdaptationNotice({ misconception, teacherThought, onDismiss }) {
  if (!misconception) return null;

  return (
    <div style={{
      background: '#FFFBEB',
      border: '1px solid #FDE68A',
      borderRadius: '12px',
      padding: '14px 18px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      animation: 'speakingPulse 0.5s ease',
      boxShadow: 'var(--shadow-sm)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#92400E', fontWeight: 700, fontSize: '0.92rem' }}>
          <Lightbulb size={18} color="#D97706" />
          <span>Let's look at this another way</span>
        </div>
        <span className="badge badge-amber" style={{ fontSize: '0.72rem' }}>
          Adaptive Explanation
        </span>
      </div>

      <p style={{ fontSize: '0.88rem', color: '#78350F', lineHeight: 1.5 }}>
        Your AI Teacher noticed an intuitive misconception and adapted the visual presentation using a water-pipe analogy to make the inverse relationship clear.
      </p>

      <div style={{ fontSize: '0.82rem', color: '#92400E', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <Compass size={14} color="#D97706" />
        <span><strong style={{ color: '#78350F' }}>Concept to revisit:</strong> Inverse relationship between Resistance and Current</span>
      </div>
    </div>
  );
}
