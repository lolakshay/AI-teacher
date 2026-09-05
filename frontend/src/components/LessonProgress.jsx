import React from 'react';
import { CheckCircle, Circle, Clock, Award, Compass } from 'lucide-react';

export default function LessonProgress({ lessonPlan, currentStepIndex, totalSteps, onTriggerAssessment, status, currentConcept }) {
  if (!lessonPlan) return null;

  const concepts = lessonPlan.ordered_concepts || [];
  const currentStepNum = Math.min(totalSteps, currentStepIndex + 1);
  const progressPercent = totalSteps > 0 ? Math.min(100, Math.round((currentStepNum / totalSteps) * 100)) : 0;

  return (
    <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      
      {/* Title and Step Number */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0F172A' }}>Curriculum Progression</h4>
          <span style={{ fontSize: '0.74rem', color: '#2563EB', fontWeight: 600 }}>
            Step {currentStepNum} of {totalSteps}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.74rem', color: 'var(--text-muted)' }}>
          <Clock size={12} />
          <span>{lessonPlan.estimated_duration}m</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ width: '100%', height: '6px', background: '#E2E8F0', borderRadius: '3px', overflow: 'hidden' }}>
        <div 
          style={{
            width: `${progressPercent}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #2563EB, #0284C7)',
            transition: 'width 0.3s ease'
          }} 
        />
      </div>

      {/* Concepts List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '170px', overflowY: 'auto' }}>
        {concepts.map((concept, idx) => {
          const isDone = idx < Math.floor(currentStepIndex / 1.5);
          const isCurrent = idx === Math.min(concepts.length - 1, Math.floor(currentStepIndex / 1.5));

          return (
            <div 
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.78rem',
                color: isCurrent ? '#0F172A' : isDone ? '#475569' : 'var(--text-muted)'
              }}
            >
              {isDone ? (
                <CheckCircle size={13} color="#059669" />
              ) : isCurrent ? (
                <Circle size={13} color="#2563EB" fill="#2563EB" />
              ) : (
                <Circle size={13} color="#CBD5E1" />
              )}
              <span style={{ fontWeight: isCurrent ? 700 : 400 }}>{concept}</span>
            </div>
          );
        })}
      </div>

      {/* Final Assessment Trigger */}
      <div style={{ paddingTop: '8px', borderTop: '1px solid var(--border-subtle)' }}>
        <button 
          id="btn-trigger-assessment"
          className="btn btn-secondary"
          onClick={onTriggerAssessment}
          style={{ width: '100%', padding: '8px 12px', fontSize: '0.82rem' }}
        >
          <Award size={14} color="#F59E0B" />
          <span>Take Final Assessment</span>
        </button>
      </div>
    </div>
  );
}
