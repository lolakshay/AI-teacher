import React, { useState } from 'react';
import { Award, ArrowRight, ArrowLeft, CheckCircle2, HelpCircle, Send, Sparkles } from 'lucide-react';

export default function AssessmentScreen({ questions = [], onSubmitAssessment, isSubmitting }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});

  if (!questions || questions.length === 0) {
    return (
      <div style={{ maxWidth: '640px', margin: '60px auto', padding: '24px' }}>
        <div className="glass-panel" style={{ padding: '32px', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-muted)' }}>No assessment questions available.</p>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentIndex];
  const total = questions.length;
  const progressPercent = Math.round(((currentIndex + 1) / total) * 100);

  const handleSelectAnswer = (ans) => {
    setAnswers(prev => ({
      ...prev,
      [currentQ.question_id]: ans
    }));
  };

  const handleNext = () => {
    if (currentIndex < total - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleFinalSubmit = () => {
    onSubmitAssessment(answers);
  };

  const currentAnswer = answers[currentQ.question_id] || '';
  const isAnswered = Boolean(currentAnswer);

  return (
    <div style={{ maxWidth: '780px', margin: '32px auto', padding: '0 20px' }}>
      <div className="glass-panel" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#FEF3C7', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#D97706' }}>
              <Award size={22} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A' }}>Let's Check What You Learned</h2>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Summative Mastery Assessment • Concept Verification
              </span>
            </div>
          </div>
          <span className="badge badge-amber">
            Question {currentIndex + 1} of {total}
          </span>
        </div>

        {/* Progress Bar */}
        <div style={{ width: '100%', height: '6px', background: '#E2E8F0', borderRadius: '3px', overflow: 'hidden' }}>
          <div 
            style={{ 
              width: `${progressPercent}%`, 
              height: '100%', 
              background: 'linear-gradient(90deg, #D97706, #059669)',
              transition: 'width 0.3s ease'
            }} 
          />
        </div>

        {/* Question Prompt */}
        <div style={{ background: '#F8FAFC', padding: '20px', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
            <HelpCircle size={16} color="#2563EB" />
            <span style={{ fontSize: '0.78rem', color: '#2563EB', fontWeight: 700, textTransform: 'uppercase' }}>
              {currentQ.question_type || 'Conceptual Question'}
            </span>
          </div>
          <p style={{ fontSize: '1.08rem', fontWeight: 600, color: '#0F172A', lineHeight: 1.5 }}>
            {currentQ.prompt}
          </p>
        </div>

        {/* Answer Options */}
        {currentQ.options && currentQ.options.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {currentQ.options.map((opt, idx) => {
              const isSelected = currentAnswer === opt;
              return (
                <div 
                  key={idx}
                  onClick={() => handleSelectAnswer(opt)}
                  style={{
                    padding: '14px 18px',
                    borderRadius: '10px',
                    background: isSelected ? '#EFF6FF' : '#FFFFFF',
                    border: isSelected ? '1.5px solid #2563EB' : '1px solid #E2E8F0',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    transition: 'all 0.15s ease',
                    boxShadow: 'var(--shadow-sm)'
                  }}
                >
                  <div style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    border: isSelected ? '5px solid #2563EB' : '2px solid #94A3B8',
                    background: isSelected ? '#FFFFFF' : 'transparent',
                    flexShrink: 0
                  }} />
                  <span style={{ fontSize: '0.94rem', color: isSelected ? '#1E40AF' : '#1E293B', fontWeight: isSelected ? 600 : 400 }}>
                    {opt}
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <input 
              type="text"
              value={currentAnswer}
              onChange={(e) => handleSelectAnswer(e.target.value)}
              placeholder="Type your answer here..."
              style={{
                width: '100%',
                padding: '14px 18px',
                borderRadius: '10px',
                background: '#FFFFFF',
                border: '1px solid #CBD5E1',
                color: '#0F172A',
                fontSize: '1rem',
                outline: 'none'
              }}
            />
          </div>
        )}

        {/* Navigation Buttons */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
          <button 
            type="button"
            onClick={handlePrev}
            disabled={currentIndex === 0 || isSubmitting}
            className="btn btn-secondary"
            style={{ opacity: currentIndex === 0 ? 0.4 : 1 }}
          >
            <ArrowLeft size={16} />
            <span>Previous</span>
          </button>

          {currentIndex < total - 1 ? (
            <button 
              type="button"
              onClick={handleNext}
              className="btn btn-primary"
            >
              <span>Next Question</span>
              <ArrowRight size={16} />
            </button>
          ) : (
            <button 
              id="btn-submit-assessment-final"
              type="button"
              onClick={handleFinalSubmit}
              disabled={isSubmitting}
              className="btn btn-emerald"
              style={{ padding: '12px 28px', fontSize: '1rem' }}
            >
              <Sparkles size={16} />
              <span>{isSubmitting ? 'Analyzing Responses...' : 'Submit Assessment'}</span>
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
