import React, { useState } from 'react';
import { 
  BookOpen, 
  UploadCloud, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  Globe, 
  Layers, 
  FileText, 
  AlertCircle, 
  ArrowRight,
  RotateCcw,
  Check,
  Compass
} from 'lucide-react';
import { uploadMaterial } from '../services/api';
import { DEMO_PRESETS } from '../data/presets';

export default function SetupFlow({ initialMode = 'topic', onStartLesson, onCancel }) {
  // Navigation tabs: 'topic' or 'upload'
  const [activeTab, setActiveTab] = useState(initialMode === 'upload' ? 'upload' : 'topic');

  // Form parameters
  const [topic, setTopic] = useState("Ohm's Law & Circuit Dynamics");
  const [level, setLevel] = useState("beginner");
  const [existingKnowledge, setExistingKnowledge] = useState("New to this");
  const [goal, setGoal] = useState("Understand concept");
  const [style, setStyle] = useState("analogy_driven");
  const [language, setLanguage] = useState("Hinglish");
  const [duration, setDuration] = useState(20);
  const [depth, setDepth] = useState("intuitive");

  // Document Upload States: IDLE, SELECTED, UPLOADING, PROCESSING, INDEXING, READY, FAILED
  const [uploadState, setUploadState] = useState('IDLE');
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [uploadProgressMsg, setUploadProgressMsg] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);

  // Handle Preset selection
  const handleSelectPreset = (preset) => {
    setTopic(preset.topic);
    setLevel(preset.level);
    setLanguage(preset.language);
    setDuration(preset.time);
    setStyle(preset.style);
  };

  // Process Document Upload with explicit 6-stage lifecycle
  const processFileUpload = async (file) => {
    if (!file) return;

    setUploadState('SELECTED');
    setUploadProgressMsg(`Selected: ${file.name}`);

    try {
      // 1. Uploading
      setUploadState('UPLOADING');
      setUploadProgressMsg('Uploading your study material...');
      await new Promise(r => setTimeout(r, 400));

      // 2. Processing
      setUploadState('PROCESSING');
      setUploadProgressMsg('Reading and understanding your material...');
      await new Promise(r => setTimeout(r, 400));

      // 3. Indexing
      setUploadState('INDEXING');
      setUploadProgressMsg('Grounding concepts and extracting key pedagogical topics...');

      const res = await uploadMaterial(file);

      // 4. Ready
      setUploadState('READY');
      setUploadedDoc(res.data);
      setUploadProgressMsg('Material ready! Your AI Teacher will ground the lesson in your document.');

      // Automatically suggest topic from document title if available
      const cleanName = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
      setTopic(cleanName);
    } catch (err) {
      setUploadState('FAILED');
      setUploadProgressMsg(`Unable to process document: ${err.message || 'Please verify file format.'}`);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFileUpload(e.target.files[0]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartLesson({
      topic,
      level,
      existingKnowledge,
      goal,
      style,
      language,
      duration,
      depth,
      materialId: uploadedDoc?.doc_id || null,
      documentName: uploadedDoc?.filename || null
    });
  };

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto', padding: '24px 16px' }}>
      <div className="glass-panel" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Personalize Your AI Teacher Lesson</h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Tailor how the AI teacher explains, questions, and guides you.
            </p>
          </div>
          <button 
            type="button" 
            onClick={onCancel} 
            className="btn btn-secondary" 
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            Back to Home
          </button>
        </div>

        {/* Mode Selector Tabs: Topic vs Document */}
        <div style={{ display: 'flex', gap: '10px', background: '#F1F5F9', padding: '6px', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
          <button
            type="button"
            onClick={() => setActiveTab('topic')}
            className={`btn ${activeTab === 'topic' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ flex: 1, padding: '10px 16px', borderRadius: '8px' }}
          >
            <BookOpen size={16} />
            <span>Choose Topic</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('upload')}
            className={`btn ${activeTab === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ flex: 1, padding: '10px 16px', borderRadius: '8px' }}
          >
            <UploadCloud size={16} />
            <span>Upload Material (PDF / DOCX / TXT)</span>
          </button>
        </div>

        {/* Tab 1: Topic Selection with Curated Presets */}
        {activeTab === 'topic' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155' }}>
              What do you want to learn today?
            </label>
            <input 
              id="input-lesson-topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Ohm's Law & Circuit Dynamics, Binary Search, Newton's Third Law..."
              required
              style={{
                width: '100%',
                padding: '12px 16px',
                borderRadius: '10px',
                background: '#FFFFFF',
                border: '1px solid #CBD5E1',
                color: '#0F172A',
                fontSize: '1rem',
                outline: 'none'
              }}
            />

            {/* Quick Demo Presets */}
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                Curriculum Topic Presets
              </span>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '10px', marginTop: '8px' }}>
                {DEMO_PRESETS.map((preset) => (
                  <div 
                    key={preset.id}
                    onClick={() => handleSelectPreset(preset)}
                    style={{
                      padding: '12px 14px',
                      borderRadius: '10px',
                      background: topic === preset.topic ? '#EFF6FF' : '#FFFFFF',
                      border: topic === preset.topic ? '1.5px solid #2563EB' : '1px solid #E2E8F0',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      boxShadow: 'var(--shadow-sm)'
                    }}
                  >
                    <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#0F172A' }}>{preset.title}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{preset.description}</div>
                    <div style={{ display: 'flex', gap: '6px', marginTop: '6px' }}>
                      <span className="badge badge-indigo" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>{preset.language}</span>
                      <span className="badge badge-cyan" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>{preset.time}m</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Document Upload UI with 6 Status States */}
        {activeTab === 'upload' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div 
              onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
              style={{
                border: isDragOver ? '2px dashed #2563EB' : '2px dashed #CBD5E1',
                background: isDragOver ? '#EFF6FF' : '#F8FAFC',
                borderRadius: '14px',
                padding: '36px 20px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <label style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
                  <UploadCloud size={24} />
                </div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0F172A' }}>
                  Drag and drop your notes or textbook here
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Supported formats: PDF, DOCX, PPTX, TXT, Markdown (Max 50MB)
                </p>
                <input 
                  type="file" 
                  accept=".pdf,.docx,.pptx,.txt,.md" 
                  onChange={handleFileChange} 
                  style={{ display: 'none' }} 
                />
                <span className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '0.85rem', marginTop: '6px' }}>
                  Browse Files
                </span>
              </label>
            </div>

            {/* Upload Lifecycle Status Box */}
            {uploadState !== 'IDLE' && (
              <div style={{
                background: uploadState === 'FAILED' ? '#FEF2F2' : uploadState === 'READY' ? '#ECFDF5' : '#EFF6FF',
                border: uploadState === 'FAILED' ? '1px solid #FECACA' : uploadState === 'READY' ? '1px solid #A7F3D0' : '1px solid #BFDBFE',
                borderRadius: '10px',
                padding: '14px 18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {uploadState === 'READY' ? (
                    <CheckCircle2 size={20} color="#059669" />
                  ) : uploadState === 'FAILED' ? (
                    <AlertCircle size={20} color="#DC2626" />
                  ) : (
                    <div style={{ width: '18px', height: '18px', border: '2px solid #2563EB', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                  )}
                  <div>
                    <span className="badge" style={{ 
                      fontSize: '0.7rem', 
                      background: uploadState === 'READY' ? '#D1FAE5' : uploadState === 'FAILED' ? '#FEE2E2' : '#DBEAFE', 
                      color: uploadState === 'READY' ? '#065F46' : uploadState === 'FAILED' ? '#991B1B' : '#1E40AF',
                      marginBottom: '4px'
                    }}>
                      Status: {uploadState}
                    </span>
                    <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#0F172A' }}>
                      {uploadProgressMsg}
                    </div>
                  </div>
                </div>

                {uploadState === 'READY' && uploadedDoc && (
                  <span className="badge badge-emerald">
                    {uploadedDoc.chunk_count || 15} Chunks Indexed
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Section 2: Conversational Personalization ("How should I teach you?") */}
        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Compass size={18} color="#2563EB" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0F172A' }}>How should your AI Teacher teach you?</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
            
            {/* Level */}
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Educational Level
              </label>
              <select 
                value={level} 
                onChange={(e) => setLevel(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value="beginner">Beginner (Foundations & Intuition)</option>
                <option value="intermediate">Intermediate (Standard Curriculum)</option>
                <option value="advanced">Advanced (Deep Dive & Rigor)</option>
              </select>
            </div>

            {/* Existing Knowledge */}
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Existing Knowledge
              </label>
              <select 
                value={existingKnowledge} 
                onChange={(e) => setExistingKnowledge(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value="New to this">New to this</option>
                <option value="Somewhat familiar">Somewhat familiar</option>
                <option value="I know the basics">I know the basics</option>
              </select>
            </div>

            {/* Learning Goal */}
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Learning Objective
              </label>
              <select 
                value={goal} 
                onChange={(e) => setGoal(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value="Understand concept">Understand concept intuitively</option>
                <option value="Exam preparation">Exam preparation & Problem Solving</option>
                <option value="Practical application">Practical Real-World Application</option>
                <option value="Deep understanding">Deep Theoretical Understanding</option>
              </select>
            </div>

            {/* Teaching Style */}
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Preferred Teaching Style
              </label>
              <select 
                value={style} 
                onChange={(e) => setStyle(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value="analogy_driven">Examples + Visuals (Analogy-Driven)</option>
                <option value="visual">Visual Demonstration First</option>
                <option value="interactive">Socratic Question & Answer</option>
                <option value="rigorous">Technical & Mathematical Rigor</option>
              </select>
            </div>

            {/* Language */}
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Preferred Language
              </label>
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value="Hinglish">Hinglish (Conversational)</option>
                <option value="English">English</option>
                <option value="Hindi">Hindi (शुद्ध हिंदी)</option>
              </select>
            </div>

            {/* Available Time */}
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '6px' }}>
                Available Time
              </label>
              <select 
                value={duration} 
                onChange={(e) => setDuration(Number(e.target.value))}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A' }}
              >
                <option value={5}>5 minutes (Speed Overview)</option>
                <option value={20}>20 minutes (Standard Interactive Lesson)</option>
                <option value={60}>60 minutes (Comprehensive Lecture)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
          <button 
            type="button" 
            onClick={onCancel} 
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button 
            id="btn-start-configured-lesson"
            type="button" 
            onClick={handleSubmit} 
            className="btn btn-primary"
            style={{ padding: '12px 28px', fontSize: '1rem' }}
          >
            <Sparkles size={18} />
            <span>Generate Lesson & Start Teaching</span>
          </button>
        </div>

      </div>
    </div>
  );
}
