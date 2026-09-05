import React from 'react';
import { 
  Play, 
  RotateCcw, 
  ArrowRight, 
  MessageSquareQuote, 
  CheckCircle2,
  Sparkles,
  HelpCircle,
  BookOpen
} from 'lucide-react';

export default function TeacherDialogue({ 
  step, 
  onAdvance, 
  onReplaySpeech, 
  isSpeaking, 
  canAdvance,
  onRequestSimplify,
  onRequestExample,
  onOpenSource
}) {
  if (!step) {
    return (
      <div className="glass-panel" style={{ padding: '20px' }}>
        <p style={{ color: 'var(--text-muted)' }}>Preparing lesson materials...</p>
      </div>
    );
  }

  const { step_type, objective, explanation, language, source_references } = step;

  const getStepBadge = () => {
    switch (step_type) {
      case 'introduction':
        return { label: 'Lesson Introduction', cls: 'badge-indigo' };
      case 'demonstration':
        return { label: 'Visual Demonstration', cls: 'badge-cyan' };
      case 're_explanation':
        return { label: 'Adaptive Re-Explanation', cls: 'badge-amber' };
      case 'question':
        return { label: 'Formative Concept Check', cls: 'badge-emerald' };
      case 'summary':
        return { label: 'Concept Synthesis', cls: 'badge-indigo' };
      default:
        return { label: step_type, cls: 'badge-indigo' };
    }
  };

  const badge = getStepBadge();

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px', position: 'relative' }}>
      
      {/* Step Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className={`badge ${badge.cls}`}>{badge.label}</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Language: {language}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Source Citation Button */}
          {source_references && source_references.length > 0 && (
            <button 
              type="button"
              onClick={onOpenSource}
              className="btn btn-secondary"
              style={{ padding: '5px 10px', fontSize: '0.78rem' }}
              title="View Prescribed Textbook / Material Citation"
            >
              <BookOpen size={13} color="#818CF8" />
              <span>View Source</span>
            </button>
          )}

          {/* Replay */}
          <button 
            onClick={onReplaySpeech}
            className="btn btn-secondary"
            style={{ padding: '5px 10px', fontSize: '0.78rem' }}
            title="Replay Spoken Voice"
          >
            <RotateCcw size={13} />
            <span>{isSpeaking ? 'Replaying...' : 'Hear Teacher'}</span>
          </button>
        </div>
      </div>

      {/* Pedagogical Objective */}
      <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <CheckCircle2 size={14} color="#2563EB" />
        <span><strong>Objective:</strong> {objective}</span>
      </div>

      {/* Spoken Dialogue Transcript */}
      <div style={{
        background: '#F8FAFC',
        border: '1px solid #E2E8F0',
        borderLeft: step_type === 're_explanation' ? '4px solid #D97706' : '4px solid #2563EB',
        borderRadius: '0 10px 10px 0',
        padding: '14px 18px',
        fontSize: '0.98rem',
        lineHeight: '1.65',
        color: '#0F172A',
        position: 'relative'
      }}>
        <div style={{ position: 'absolute', right: '12px', top: '10px', opacity: 0.2, color: '#64748B' }}>
          <MessageSquareQuote size={32} />
        </div>
        {explanation}
      </div>

      {/* In-Lesson Assistance Controls & Advance */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px', flexWrap: 'wrap', gap: '8px' }}>
        {/* Assistance Buttons */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            type="button"
            className="btn btn-secondary"
            onClick={onRequestSimplify}
            style={{ padding: '6px 12px', fontSize: '0.78rem' }}
            title="Request AI Teacher to break this down more simply"
          >
            <Sparkles size={13} color="#2563EB" />
            <span>Explain more simply</span>
          </button>
          
          <button 
            type="button"
            className="btn btn-secondary"
            onClick={onRequestExample}
            style={{ padding: '6px 12px', fontSize: '0.78rem' }}
            title="Request a concrete real-world example"
          >
            <HelpCircle size={13} color="#0284C7" />
            <span>Show me an example</span>
          </button>
        </div>

        {/* Advance step if not an interactive question */}
        {canAdvance && (
          <button 
            id="btn-advance-step"
            onClick={onAdvance}
            className="btn btn-primary"
            style={{ padding: '8px 18px' }}
          >
            <span>Proceed to Next Step</span>
            <ArrowRight size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
