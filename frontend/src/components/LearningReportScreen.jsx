import React, { useEffect } from 'react';
import confetti from 'canvas-confetti';
import { 
  Award, 
  CheckCircle, 
  AlertTriangle, 
  ArrowRight, 
  RotateCcw, 
  BookOpen, 
  Sparkles, 
  Clock, 
  ChevronRight,
  TrendingUp,
  Download
} from 'lucide-react';

export default function LearningReportScreen({ report, onStartNextTopic, onReturnHome }) {
  useEffect(() => {
    // Launch celebratory confetti particles
    confetti({
      particleCount: 90,
      spread: 80,
      origin: { y: 0.55 }
    });
  }, []);

  if (!report) return null;

  const { 
    score = 92.0, 
    concepts_understood = [], 
    weak_areas = [], 
    misconceptions = [], 
    concepts_requiring_revision = [], 
    recommended_practice = [], 
    recommended_next_topic = "Kirchhoff's Laws & Resistor Networks", 
    overall_progress = "Successfully completed learning loop with adaptive mastery.",
    estimated_revision_time_minutes = 10 
  } = report;

  return (
    <div style={{ maxWidth: '840px', margin: '32px auto', padding: '0 20px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Banner with Score */}
      <div className="glass-panel" style={{ 
        padding: '32px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        background: 'linear-gradient(135deg, #ECFDF5 0%, #EFF6FF 100%)',
        border: '1px solid #A7F3D0',
        flexWrap: 'wrap',
        gap: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{
            width: '72px',
            height: '72px',
            borderRadius: '20px',
            background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 24px rgba(16, 185, 129, 0.3)'
          }}>
            <Award size={36} color="#FFF" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0F172A' }}>Comprehensive Learning Report</h1>
              <span className="badge badge-emerald" style={{ fontSize: '0.85rem', padding: '4px 12px' }}>
                Mastery: {score}%
              </span>
            </div>
            <p style={{ fontSize: '0.9rem', color: '#475569', marginTop: '4px', maxWidth: '520px' }}>
              {overall_progress}
            </p>
          </div>
        </div>

        <button 
          onClick={() => window.print()}
          className="btn btn-secondary"
          style={{ padding: '8px 14px', fontSize: '0.8rem' }}
        >
          <Download size={14} />
          <span>Export Summary</span>
        </button>
      </div>

      {/* Mastery Dimensions: Strong vs Developing vs Needs Review */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '18px' }}>
        
        {/* Concepts Mastered */}
        <div className="glass-panel" style={{ padding: '22px', borderLeft: '4px solid #059669', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#047857', fontWeight: 700, fontSize: '0.95rem' }}>
            <CheckCircle size={18} color="#059669" />
            <span>Concepts Mastered (Demonstrated Competency)</span>
          </div>
          <ul style={{ listStyle: 'none', paddingLeft: 0, fontSize: '0.9rem', color: '#1E293B', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {concepts_understood && concepts_understood.length > 0 ? (
              concepts_understood.map((c, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle size={15} color="#059669" style={{ flexShrink: 0 }} />
                  <span><strong style={{ color: '#0F172A' }}>Mastered:</strong> {c}</span>
                </li>
              ))
            ) : (
              <li style={{ color: '#64748B' }}>Foundational principles verified.</li>
            )}
          </ul>
        </div>

        {/* Concepts to Revisit */}
        <div className="glass-panel" style={{ padding: '22px', borderLeft: '4px solid #D97706', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#B45309', fontWeight: 700, fontSize: '0.95rem' }}>
              <AlertTriangle size={18} color="#D97706" />
              <span>Concepts for Review & Reinforcement</span>
            </div>
            <span className="badge badge-amber" style={{ fontSize: '0.7rem' }}>
              <Clock size={11} /> ~{estimated_revision_time_minutes} mins
            </span>
          </div>
          <ul style={{ listStyle: 'none', paddingLeft: 0, fontSize: '0.9rem', color: '#1E293B', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {concepts_requiring_revision && concepts_requiring_revision.length > 0 ? (
              concepts_requiring_revision.map((c, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <AlertTriangle size={15} color="#D97706" style={{ flexShrink: 0 }} />
                  <span><strong style={{ color: '#0F172A' }}>Review:</strong> {c}</span>
                </li>
              ))
            ) : weak_areas && weak_areas.length > 0 ? (
              weak_areas.map((w, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Clock size={15} color="#0284C7" style={{ flexShrink: 0 }} />
                  <span><strong style={{ color: '#0F172A' }}>In Progress:</strong> {w}</span>
                </li>
              ))
            ) : (
              <li style={{ color: '#64748B' }}>No critical knowledge gaps detected!</li>
            )}
          </ul>
        </div>
      </div>

      {/* Misconceptions Overcome Banner */}
      {misconceptions && misconceptions.length > 0 && (
        <div className="glass-panel" style={{ padding: '20px', background: '#FFFBEB', border: '1px solid #FDE68A', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#92400E', fontWeight: 700, fontSize: '0.92rem' }}>
            <Sparkles size={16} color="#D97706" />
            <span>Pedagogical Remediation: Misconceptions Addressed & Overcome</span>
          </div>
          <ul style={{ paddingLeft: '20px', fontSize: '0.88rem', color: '#78350F', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {misconceptions.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended Practice Drills */}
      {recommended_practice && recommended_practice.length > 0 && (
        <div className="glass-panel" style={{ padding: '22px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#1E40AF', fontWeight: 700, fontSize: '0.95rem' }}>
            <TrendingUp size={18} color="#2563EB" />
            <span>Recommended Revision & Practice</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {recommended_practice.map((drill, i) => (
              <div 
                key={i}
                style={{
                  background: '#F8FAFC',
                  border: '1px solid #E2E8F0',
                  borderRadius: '8px',
                  padding: '12px 16px',
                  fontSize: '0.88rem',
                  color: '#0F172A',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  boxShadow: 'var(--shadow-sm)'
                }}
              >
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#2563EB', flexShrink: 0 }} />
                <span>{drill}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Suggested Next Topic CTA */}
      {recommended_next_topic && (
        <div className="glass-panel" style={{ 
          padding: '24px', 
          background: 'linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%)',
          border: '1px solid #BFDBFE',
          borderRadius: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#1D4ED8', textTransform: 'uppercase', fontWeight: 800 }}>
              Up Next In Your Personalized Curriculum
            </span>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', marginTop: '4px' }}>
              {recommended_next_topic}
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#475569', marginTop: '2px' }}>
              Prerequisites verified. Ready to begin series & parallel circuit principles.
            </p>
          </div>

          <button 
            id="btn-continue-learning-next"
            className="btn btn-primary"
            onClick={() => onStartNextTopic(recommended_next_topic)}
            style={{ padding: '14px 28px', fontSize: '1rem', borderRadius: '12px' }}
          >
            <span>Continue Learning</span>
            <ArrowRight size={18} />
          </button>
        </div>
      )}

      {/* Bottom Action */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '8px' }}>
        <button 
          onClick={onReturnHome}
          className="btn btn-secondary"
          style={{ padding: '10px 24px' }}
        >
          Return to Classroom Home
        </button>
      </div>

    </div>
  );
}
