import React from 'react';
import { BookOpen, X, ExternalLink, CheckCircle } from 'lucide-react';

export default function SourceModal({ isOpen, onClose, sourceReferences = [] }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="glass-panel" 
        onClick={(e) => e.stopPropagation()}
        style={{ 
          maxWidth: '520px', 
          width: '100%', 
          padding: '24px', 
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}
      >
        <button 
          onClick={onClose}
          style={{ position: 'absolute', top: '16px', right: '16px', background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ padding: '8px', borderRadius: '10px', background: '#EFF6FF', color: '#2563EB' }}>
            <BookOpen size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0F172A' }}>Educational Source References</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Verified curriculum materials grounding this lesson
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '4px' }}>
          {sourceReferences && sourceReferences.length > 0 ? (
            sourceReferences.map((ref, idx) => (
              <div 
                key={idx}
                style={{
                  background: '#F8FAFC',
                  border: '1px solid #E2E8F0',
                  borderRadius: '10px',
                  padding: '12px 16px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px',
                  boxShadow: 'var(--shadow-sm)'
                }}
              >
                <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0F172A' }}>
                  {ref.document || "Prescribed Curriculum Textbook"}
                </div>
                {ref.chapter && (
                  <div style={{ fontSize: '0.82rem', color: '#1D4ED8', fontWeight: 600 }}>
                    Chapter: {ref.chapter}
                  </div>
                )}
                {ref.section && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Section: {ref.section}
                  </div>
                )}
                {ref.page && (
                  <span className="badge badge-indigo" style={{ alignSelf: 'flex-start', marginTop: '4px' }}>
                    Page {ref.page}
                  </span>
                )}
              </div>
            ))
          ) : (
            <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Standard educational curriculum corpus.
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '6px' }}>
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
