import React from 'react';
import { Brain, AlertTriangle, Lightbulb, Compass, GitMerge, CheckCircle } from 'lucide-react';

export default function AdaptationHUD({ lastEvaluation, activeMisconception, adaptationCount }) {
  if (!lastEvaluation && !activeMisconception) {
    return (
      <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Brain size={18} color="#2563EB" />
          <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A' }}>Teacher's Pedagogical Reasoning</h4>
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Active diagnostic observation: Continuously modeling student comprehension, cognitive load, and prerequisite mastery.
        </p>
      </div>
    );
  }

  const isMisconception = lastEvaluation?.misconception || activeMisconception;

  return (
    <div 
      className="glass-panel" 
      style={{ 
        padding: '18px', 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '12px',
        border: isMisconception ? '1px solid #FDE68A' : '1px solid var(--border-subtle)',
        boxShadow: isMisconception ? 'var(--shadow-amber-glow)' : 'var(--shadow-sm)'
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Brain size={20} color={isMisconception ? '#D97706' : '#059669'} />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A' }}>
            {isMisconception ? "Pedagogical Adaptation Triggered" : "Cognitive Reasoning State"}
          </h4>
        </div>
        <span className={isMisconception ? "badge badge-amber" : "badge badge-emerald"}>
          {isMisconception ? "Misconception Detected" : "Concept Mastered"}
        </span>
      </div>

      {/* Misconception Alert if active */}
      {isMisconception && (
        <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '8px', padding: '10px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#B45309', fontWeight: 700, fontSize: '0.88rem' }}>
            <AlertTriangle size={16} />
            <span>Detected Misconception: {lastEvaluation?.misconception || activeMisconception}</span>
          </div>
          {lastEvaluation?.knowledge_gap && (
            <p style={{ fontSize: '0.78rem', color: '#92400E', marginTop: '4px' }}>
              <strong>Knowledge Gap:</strong> {lastEvaluation.knowledge_gap}
            </p>
          )}
        </div>
      )}

      {/* Internal Monologue / Thought */}
      {lastEvaluation?.teacher_thought && (
        <div style={{ fontSize: '0.82rem', color: '#1E293B', background: '#F8FAFC', padding: '10px 14px', borderRadius: '8px', border: '1px solid #E2E8F0', borderLeft: '3px solid #2563EB' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#1D4ED8', fontWeight: 600, marginBottom: '2px' }}>
            <Lightbulb size={14} />
            <span>Teacher's Internal Reflection:</span>
          </div>
          <span style={{ fontStyle: 'italic' }}>"{lastEvaluation.teacher_thought}"</span>
        </div>
      )}

      {/* Strategy and Bloom Details */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', paddingTop: '4px' }}>
        <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', padding: '8px 10px', borderRadius: '8px' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Action</span>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0F172A' }}>
            {lastEvaluation?.recommended_action || 'continue'}
          </div>
        </div>
        <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', padding: '8px 10px', borderRadius: '8px' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Bloom Level</span>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0284C7' }}>
            {lastEvaluation?.bloom_level || 'Understanding'}
          </div>
        </div>
        <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', padding: '8px 10px', borderRadius: '8px' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Adaptations</span>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#D97706' }}>
            {adaptationCount} Interventions
          </div>
        </div>
      </div>
    </div>
  );
}
