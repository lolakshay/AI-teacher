import React, { useEffect } from 'react';
import confetti from 'canvas-confetti';
import { Award, CheckCircle, AlertTriangle, ArrowRight, RotateCcw, BookOpen, Sparkles, X } from 'lucide-react';

export default function LearningReportModal({ report, onClose, onStartNextTopic }) {
  if (!report) return null;

  useEffect(() => {
    // Fire celebration confetti!
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 }
    });
  }, []);

  const { score, concepts_understood, weak_areas, misconceptions, concepts_requiring_revision, recommended_practice, recommended_next_topic, overall_progress } = report;

  return (
    <div className="modal-overlay">
      <div 
        className="glass-panel" 
        style={{ 
          maxWidth: '680px', 
          width: '100%', 
          maxHeight: '90vh', 
          overflowY: 'auto', 
          padding: '28px',
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}
      >
        {/* Close Button */}
        <button 
          onClick={onClose}
          style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>

        {/* Header with Score */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(16, 185, 129, 0.4)'
          }}>
            <Award size={32} color="#FFF" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0F172A' }}>Comprehensive Learning Report</h2>
              <span className="badge badge-emerald">Mastery: {score}%</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#475569' }}>
              {overall_progress}
            </p>
          </div>
        </div>

        {/* Diagnostic Breakdown */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          {/* Concepts Understood */}
          <div style={{ background: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: '12px', padding: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#047857', fontWeight: 700, fontSize: '0.85rem', marginBottom: '8px' }}>
              <CheckCircle size={16} color="#059669" />
              <span>Concepts Mastered</span>
            </div>
            <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: '#1E293B', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {concepts_understood?.map((c, i) => (
                <li key={i}><strong style={{ color: '#0F172A' }}>{c}</strong></li>
              ))}
            </ul>
          </div>

          {/* Misconceptions Overcome */}
          <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '12px', padding: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#B45309', fontWeight: 700, fontSize: '0.85rem', marginBottom: '8px' }}>
              <AlertTriangle size={16} color="#D97706" />
              <span>Misconceptions Addressed</span>
            </div>
            {misconceptions && misconceptions.length > 0 ? (
              <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: '#78350F', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {misconceptions.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: '0.82rem', color: '#64748B' }}>None detected during this lesson.</p>
            )}
          </div>
        </div>

        {/* Recommended Practice */}
        {recommended_practice && recommended_practice.length > 0 && (
          <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.85rem', marginBottom: '8px', color: '#1E40AF' }}>
              <Sparkles size={16} color="#2563EB" />
              <span>Recommended Practice & Drills</span>
            </div>
            <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: '#0F172A', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {recommended_practice.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommended Next Topic */}
        {recommended_next_topic && (
          <div style={{ background: 'linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%)', border: '1px solid #BFDBFE', borderRadius: '12px', padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: '#1D4ED8', textTransform: 'uppercase', fontWeight: 700 }}>Up Next In Curriculum</span>
              <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0F172A', marginTop: '2px' }}>{recommended_next_topic}</h4>
            </div>
            <button 
              className="btn btn-primary"
              onClick={() => onStartNextTopic(recommended_next_topic)}
              style={{ padding: '10px 16px' }}
            >
              <span>Learn Next Topic</span>
              <ArrowRight size={16} />
            </button>
          </div>
        )}

        {/* Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '6px' }}>
          <button className="btn btn-secondary" onClick={onClose}>
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}
