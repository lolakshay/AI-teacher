import React, { useState, useEffect } from 'react';
import { Send, Mic, MicOff, HelpCircle, AlertCircle, Sparkles, CheckCircle, CheckCircle2, Lightbulb, Headphones } from 'lucide-react';
import { speechService } from '../services/tts';

export default function StudentInteraction({ question, onSubmitAnswer, isSubmitting }) {
  const [answer, setAnswer] = useState('');
  const [selectedOption, setSelectedOption] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [showHints, setShowHints] = useState(false);

  // Clear inputs when question changes
  useEffect(() => {
    setAnswer('');
    setSelectedOption(null);
    setShowHints(false);
  }, [question?.question_id]);

  if (!question) {
    return (
      <div className="glass-panel" style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '110px' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Headphones size={16} color="#3B82F6" />
          <span>Active Learning: Listen to the teacher or interact with the whiteboard. Interactive concept questions will appear here.</span>
        </p>
      </div>
    );
  }

  const { prompt, options, hints, question_type, unit } = question;
  const isMCQ = options && options.length > 0;
  const isNumerical = question_type === 'numerical';

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    const finalAnswer = isMCQ ? selectedOption : answer;
    if (!finalAnswer || isSubmitting) return;

    onSubmitAnswer(finalAnswer, isMCQ ? 'option' : isNumerical ? 'numerical' : 'text');
  };

  const handleVoiceInput = () => {
    if (isRecording) {
      setIsRecording(false);
      return;
    }

    setIsRecording(true);
    speechService.startSpeechRecognition(
      (transcript) => {
        setAnswer(transcript);
        setIsRecording(false);
      },
      () => setIsRecording(false),
      (err) => {
        console.warn('Speech error:', err);
        setIsRecording(false);
      }
    );
  };

  return (
    <div className="glass-panel" style={{ 
      padding: '20px', 
      display: 'flex', 
      flexDirection: 'column', 
      gap: '14px', 
      border: '1px solid rgba(99, 102, 241, 0.35)',
      boxShadow: 'var(--shadow-glow)'
    }}>
      
      {/* Header: Transitions from Teaching to "Your Turn" */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
        <div style={{ padding: '8px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.2)', color: '#818CF8' }}>
          <HelpCircle size={22} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-emerald">Your Turn</span>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
              {question_type ? question_type.replace('_', ' ') : 'Formative Probe'}
            </span>
          </div>
          <p style={{ fontSize: '1.02rem', fontWeight: 600, color: '#0F172A', lineHeight: '1.5' }}>
            {prompt}
          </p>
        </div>
      </div>

      {/* Evaluating Status State */}
      {isSubmitting && (
        <div style={{
          background: '#EFF6FF',
          border: '1px solid #BFDBFE',
          borderRadius: '10px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: '#1D4ED8',
          fontSize: '0.9rem'
        }}>
          <div style={{ width: '18px', height: '18px', border: '2px solid #2563EB', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
          <span>Let's see how you approached that...</span>
        </div>
      )}

      {/* Case 1: Multiple Choice Options UI */}
      {isMCQ && !isSubmitting && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '8px' }}>
          {options.map((opt, idx) => {
            const isSelected = selectedOption === opt;
            return (
              <div 
                key={idx}
                onClick={() => setSelectedOption(opt)}
                style={{
                  padding: '12px 16px',
                  borderRadius: '10px',
                  background: isSelected ? '#EFF6FF' : '#F8FAFC',
                  border: isSelected ? '1px solid #2563EB' : '1px solid #E2E8F0',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  border: isSelected ? '5px solid #2563EB' : '2px solid #CBD5E1',
                  background: isSelected ? '#FFFFFF' : 'transparent'
                }} />
                <span style={{ fontSize: '0.92rem', color: isSelected ? '#1E40AF' : '#1E293B', fontWeight: isSelected ? 600 : 400 }}>
                  {opt}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Case 2: Numerical or Free-form Text Input */}
      {!isMCQ && !isSubmitting && (
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <input 
              id="input-student-answer"
              type={isNumerical ? 'number' : 'text'}
              step="any"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder={isNumerical ? "Enter numerical calculation result..." : "Type your answer or explanation here..."}
              disabled={isSubmitting}
              style={{
                width: '100%',
                padding: '12px 16px',
                borderRadius: '10px',
                background: '#FFFFFF',
                border: '1px solid #CBD5E1',
                color: '#0F172A',
                fontSize: '0.95rem',
                outline: 'none'
              }}
            />
            {unit && (
              <span style={{ position: 'absolute', right: '14px', top: '12px', color: '#64748B', fontSize: '0.85rem', fontWeight: 600 }}>
                {unit}
              </span>
            )}
          </div>

          {!isNumerical && (
            <button 
              type="button"
              onClick={handleVoiceInput}
              className={`btn ${isRecording ? 'btn-danger' : 'btn-secondary'}`}
              title={isRecording ? "Stop Listening" : "Speak your answer via Speech-to-Text"}
              style={{ padding: '12px 14px' }}
            >
              {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
          )}
        </form>
      )}

      {/* Submit Button */}
      {!isSubmitting && (
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2px' }}>
          <button 
            id="btn-submit-answer"
            type="button"
            onClick={handleSubmit}
            disabled={isMCQ ? !selectedOption : !answer.trim()}
            className="btn btn-primary"
            style={{ padding: '10px 24px' }}
          >
            <Send size={16} />
            <span>Submit Answer</span>
          </button>
        </div>
      )}

      {/* Evaluator Shortcuts for Hackathon Golden Demo */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        paddingTop: '8px', 
        borderTop: '1px solid var(--border-subtle)', 
        flexWrap: 'wrap', 
        gap: '8px' 
      }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button 
            id="btn-test-misconception"
            type="button"
            className="btn btn-amber"
            onClick={() => {
              setSelectedOption("Current increases");
              setAnswer("Current increases");
              onSubmitAnswer("Current increases", isMCQ ? "option" : "text");
            }}
            style={{ padding: '6px 12px', fontSize: '0.78rem' }}
            title="Demonstrate how AI diagnoses misconceptions by testing 'Current increases'"
          >
            <AlertCircle size={14} />
            <span>Test Misconception: "Current increases"</span>
          </button>
          
          <button 
            type="button"
            className="btn btn-emerald"
            onClick={() => {
              const correctStr = "Current decreases";
              setSelectedOption(correctStr);
              setAnswer("Current decreases because resistance opposes flow");
              onSubmitAnswer("Current decreases because resistance opposes flow", isMCQ ? "option" : "text");
            }}
            style={{ padding: '6px 12px', fontSize: '0.78rem' }}
          >
            <CheckCircle2 size={14} />
            <span>Submit Correct Response</span>
          </button>
        </div>

        {/* Hints Accordion */}
        {hints && hints.length > 0 && (
          <div>
            <button 
              type="button"
              className="btn btn-secondary"
              onClick={() => setShowHints(!showHints)}
              style={{ padding: '4px 10px', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
            >
              <Lightbulb size={13} color="#FCD34D" />
              <span>{showHints ? 'Hide Hint' : 'Need a Hint?'}</span>
            </button>
          </div>
        )}
      </div>

      {showHints && hints && (
        <div style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: '8px', padding: '10px 14px', fontSize: '0.82rem', color: '#FDE68A' }}>
          {hints.map((hint, idx) => (
            <div key={idx} style={{ marginBottom: '4px' }}>• {hint}</div>
          ))}
        </div>
      )}
    </div>
  );
}
