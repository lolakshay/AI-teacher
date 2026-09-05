import React, { useState } from 'react';
import { BookOpen, Upload, X, Sparkles, Clock, Globe, Award } from 'lucide-react';
import { DEMO_PRESETS } from '../data/presets';
import { uploadMaterial } from '../services/api';

export default function SetupModal({ isOpen, onClose, onStartLesson }) {
  const [topic, setTopic] = useState("Ohm's Law & Circuit Dynamics");
  const [level, setLevel] = useState("beginner");
  const [language, setLanguage] = useState("Hinglish");
  const [duration, setDuration] = useState(20);
  const [style, setStyle] = useState("analogy_driven");
  const [uploadedMaterial, setUploadedMaterial] = useState(null);
  const [uploading, setUploading] = useState(false);

  if (!isOpen) return null;

  const handleSelectPreset = (preset) => {
    setTopic(preset.topic);
    setLevel(preset.level);
    setLanguage(preset.language);
    setDuration(preset.time);
    setStyle(preset.style);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const res = await uploadMaterial(file);
      setUploadedMaterial(res.data);
    } catch (err) {
      alert("Failed to upload document: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartLesson({
      topic,
      level,
      language,
      duration,
      style,
      materialId: uploadedMaterial?.doc_id || null
    });
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div 
        className="glass-panel" 
        style={{ 
          maxWidth: '620px', 
          width: '100%', 
          maxHeight: '90vh', 
          overflowY: 'auto', 
          padding: '24px',
          position: 'relative'
        }}
      >
        <button 
          onClick={onClose}
          style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '18px' }}>
          <div style={{ padding: '8px', borderRadius: '10px', background: '#EFF6FF', color: '#2563EB' }}>
            <BookOpen size={20} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A' }}>Configure Learning Session</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Set up personalized pedagogical parameters for your AI Teacher
            </p>
          </div>
        </div>

        {/* Quick Presets */}
        <div style={{ marginBottom: '18px' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
            Curated Demonstration Presets
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
            {DEMO_PRESETS.map((preset) => (
              <div 
                key={preset.id}
                onClick={() => handleSelectPreset(preset)}
                style={{
                  padding: '10px 14px',
                  borderRadius: '10px',
                  background: topic === preset.topic ? '#EFF6FF' : '#FFFFFF',
                  border: topic === preset.topic ? '1.5px solid #2563EB' : '1px solid #E2E8F0',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  boxShadow: 'var(--shadow-sm)'
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#0F172A' }}>{preset.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{preset.description}</div>
                </div>
                <span className="badge badge-indigo">{preset.language} • {preset.time}m</span>
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* Custom Topic Input */}
          <div>
            <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
              Topic to Learn
            </label>
            <input 
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Newton's Third Law, Photosynthesis, Binary Search..."
              required
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: '8px',
                background: '#FFFFFF',
                border: '1px solid #CBD5E1',
                color: '#0F172A',
                fontSize: '0.9rem',
                outline: 'none'
              }}
            />
          </div>

          {/* Grid of parameters */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Educational Level
              </label>
              <select 
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value="beginner">Beginner (Foundational)</option>
                <option value="intermediate">Intermediate (Standard)</option>
                <option value="advanced">Advanced (Deep Dive)</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Language
              </label>
              <select 
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value="Hinglish">Hinglish (Conversational)</option>
                <option value="English">English</option>
                <option value="Hindi">Hindi (शुद्ध हिंदी)</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Available Time (Minutes)
              </label>
              <select 
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value={10}>10 minutes (Speed Overview)</option>
                <option value={20}>20 minutes (Standard Lesson)</option>
                <option value={45}>45 minutes (Full Lecture)</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Teaching Style
              </label>
              <select 
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value="analogy_driven">Analogy-Driven (Intuitive)</option>
                <option value="visual">Visual & Demonstration First</option>
                <option value="interactive">Question & Socratic Dialogue</option>
                <option value="rigorous">Rigorous Mathematical</option>
              </select>
            </div>
          </div>

          {/* Educational Document Upload (RAG) */}
          <div style={{ background: '#F8FAFC', border: '1px dashed #CBD5E1', borderRadius: '10px', padding: '14px', textAlign: 'center' }}>
            <label style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
              <Upload size={20} color="#2563EB" />
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#0F172A' }}>
                {uploadedMaterial ? `Attached: ${uploadedMaterial.filename} (${uploadedMaterial.chunk_count} chunks)` : 'Optional: Upload Textbook / Notes (PDF, DOCX)'}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {uploading ? 'Ingesting document chunks...' : 'Click to attach educational material for RAG knowledge grounding'}
              </span>
              <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileUpload} style={{ display: 'none' }} />
            </label>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" style={{ padding: '10px 24px' }}>
              <Sparkles size={16} />
              <span>Start Adaptive Lesson</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
