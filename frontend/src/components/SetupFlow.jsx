import React, { useState, useEffect } from 'react';
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
  Check, 
  Compass, 
  ChevronRight, 
  Sliders, 
  ShieldCheck, 
  Activity, 
  Video, 
  Zap, 
  Search, 
  CornerDownLeft, 
  GraduationCap,
  Cpu,
  BrainCircuit
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

  // Keyboard shortcut: Ctrl + Enter / Cmd + Enter to initialize
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleSubmit();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [topic, level, existingKnowledge, goal, style, language, duration, depth, uploadedDoc]);

  // Process Document Upload with explicit 6-stage lifecycle
  const processFileUpload = async (file) => {
    if (!file) return;

    setUploadState('SELECTED');
    setUploadProgressMsg(`Selected: ${file.name}`);

    try {
      // 1. Uploading
      setUploadState('UPLOADING');
      setUploadProgressMsg('Uploading study material to secure sandbox...');
      await new Promise(r => setTimeout(r, 400));

      // 2. Processing
      setUploadState('PROCESSING');
      setUploadProgressMsg('Parsing document structure & extracting math formulas...');
      await new Promise(r => setTimeout(r, 400));

      // 3. Indexing
      setUploadState('INDEXING');
      setUploadProgressMsg('Generating vector embeddings & grounding concept graph...');

      const res = await uploadMaterial(file);

      // 4. Ready
      setUploadState('READY');
      setUploadedDoc(res.data);
      setUploadProgressMsg('Material indexed. AI Teacher is grounded in this document.');

      // Automatically suggest topic from document title
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
    if (e) e.preventDefault();
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
    <div style={{ maxWidth: '1360px', margin: '0 auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Software Top App Navigation & Status Toolbar */}
      <div className="glass-panel" style={{ 
        padding: '14px 20px', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        background: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#EFF6FF', border: '1px solid #BFDBFE', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
            <Sliders size={18} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>Curriculum Studio</span>
              <span style={{ fontSize: '0.75rem', color: '#CBD5E1' }}>/</span>
              <span style={{ fontSize: '0.85rem', color: '#0F172A', fontWeight: 700 }}>Session Configuration Console</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '1px' }}>
              Configure pedagogical architecture, learner modeling, and visual simulations.
            </p>
          </div>
        </div>

        {/* Engine Status Indicators & Quick Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '6px', fontSize: '0.74rem', color: '#475569', fontWeight: 600 }}>
            <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: '#10B981', display: 'inline-block' }} />
            <span>Gemini 3.7 Flash Engine</span>
          </div>

          <button 
            type="button" 
            onClick={onCancel} 
            className="btn btn-secondary" 
            style={{ padding: '7px 14px', fontSize: '0.8rem' }}
          >
            Cancel
          </button>

          <button 
            id="btn-start-configured-lesson-top"
            type="button" 
            onClick={handleSubmit} 
            className="btn btn-primary"
            style={{ padding: '7px 18px', fontSize: '0.82rem', gap: '6px' }}
          >
            <Sparkles size={14} />
            <span>Initialize Session</span>
            <span style={{ fontSize: '0.7rem', opacity: 0.8, background: 'rgba(255,255,255,0.2)', padding: '1px 5px', borderRadius: '4px', marginLeft: '4px' }}>↵</span>
          </button>
        </div>
      </div>

      {/* Main Software Studio Workbench (Split 2-Column Workstation) */}
      <div className="setup-studio-workbench" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 400px', gap: '20px', alignItems: 'start' }}>
        
        {/* LEFT PANE: Configuration Workstation */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          
          {/* Section 1: Subject / Knowledge Ingestion */}
          <div className="glass-panel" style={{ padding: '22px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #E2E8F0', paddingBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BookOpen size={17} color="#2563EB" />
                <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#0F172A' }}>
                  1. Curriculum Ingestion & Target Concept
                </h3>
              </div>
              
              {/* macOS / Desktop Segmented Toggle */}
              <div style={{ display: 'flex', background: '#F1F5F9', padding: '3px', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                <button
                  type="button"
                  onClick={() => setActiveTab('topic')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 14px',
                    borderRadius: '6px',
                    fontSize: '0.78rem',
                    fontWeight: 600,
                    border: 'none',
                    cursor: 'pointer',
                    background: activeTab === 'topic' ? '#FFFFFF' : 'transparent',
                    color: activeTab === 'topic' ? '#2563EB' : '#64748B',
                    boxShadow: activeTab === 'topic' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <BookOpen size={13} />
                  <span>Curriculum Topic</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('upload')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 14px',
                    borderRadius: '6px',
                    fontSize: '0.78rem',
                    fontWeight: 600,
                    border: 'none',
                    cursor: 'pointer',
                    background: activeTab === 'upload' ? '#FFFFFF' : 'transparent',
                    color: activeTab === 'upload' ? '#2563EB' : '#64748B',
                    boxShadow: activeTab === 'upload' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <UploadCloud size={13} />
                  <span>Upload Material (RAG)</span>
                </button>
              </div>
            </div>

            {/* Sub-View A: Topic Input & Curated Presets */}
            {activeTab === 'topic' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#334155', display: 'block', marginBottom: '6px' }}>
                    Target Subject / Topic to Master
                  </label>
                  <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                    <Search size={16} color="#94A3B8" style={{ position: 'absolute', left: '14px' }} />
                    <input 
                      id="input-lesson-topic"
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="Enter any STEM subject: Ohm's Law, Binary Search Trees, Newton's Laws..."
                      required
                      style={{
                        width: '100%',
                        padding: '11px 16px 11px 40px',
                        borderRadius: '8px',
                        background: '#FFFFFF',
                        border: '1px solid #CBD5E1',
                        color: '#0F172A',
                        fontSize: '0.92rem',
                        fontWeight: 600
                      }}
                    />
                  </div>
                </div>

                {/* Preset Templates */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Curated Curriculum Blueprints
                    </span>
                    <span style={{ fontSize: '0.72rem', color: '#94A3B8' }}>Select to auto-populate parameters</span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                    {DEMO_PRESETS.map((preset) => {
                      const isSelected = topic === preset.topic;
                      return (
                        <div 
                          key={preset.id}
                          onClick={() => handleSelectPreset(preset)}
                          style={{
                            padding: '12px 14px',
                            borderRadius: '9px',
                            background: isSelected ? '#EFF6FF' : '#FFFFFF',
                            border: isSelected ? '1.5px solid #2563EB' : '1px solid #E2E8F0',
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'space-between',
                            gap: '8px',
                            boxShadow: isSelected ? '0 2px 8px rgba(37,99,235,0.1)' : 'var(--shadow-sm)'
                          }}
                        >
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                              <span style={{ fontWeight: 700, fontSize: '0.85rem', color: isSelected ? '#1E40AF' : '#0F172A' }}>
                                {preset.title}
                              </span>
                              {isSelected && <CheckCircle2 size={14} color="#2563EB" style={{ flexShrink: 0, marginTop: '2px' }} />}
                            </div>
                            <p style={{ fontSize: '0.74rem', color: '#64748B', marginTop: '4px', lineHeight: 1.35, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                              {preset.description}
                            </p>
                          </div>
                          
                          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                            <span className="badge badge-indigo" style={{ fontSize: '0.66rem', padding: '2px 6px' }}>{preset.language}</span>
                            <span className="badge badge-cyan" style={{ fontSize: '0.66rem', padding: '2px 6px' }}>{preset.time}m</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Sub-View B: Document Ingestion */}
            {activeTab === 'upload' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div 
                  onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                  onDragLeave={() => setIsDragOver(false)}
                  onDrop={handleDrop}
                  style={{
                    border: isDragOver ? '2px dashed #2563EB' : '1.5px dashed #CBD5E1',
                    background: isDragOver ? '#EFF6FF' : '#F8FAFC',
                    borderRadius: '10px',
                    padding: '28px 20px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <label style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
                      <UploadCloud size={22} />
                    </div>
                    <div style={{ fontWeight: 700, fontSize: '0.94rem', color: '#0F172A' }}>
                      Ingest Reference Textbook or Class Notes
                    </div>
                    <p style={{ fontSize: '0.78rem', color: '#64748B' }}>
                      Supported formats: PDF, DOCX, PPTX, TXT, Markdown (Max 50MB)
                    </p>
                    <input 
                      type="file" 
                      accept=".pdf,.docx,.pptx,.txt,.md" 
                      onChange={handleFileChange} 
                      style={{ display: 'none' }} 
                    />
                    <span className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: '0.78rem', marginTop: '4px' }}>
                      Browse Local Drive
                    </span>
                  </label>
                </div>

                {/* Upload Status Card */}
                {uploadState !== 'IDLE' && (
                  <div style={{
                    background: uploadState === 'FAILED' ? '#FEF2F2' : uploadState === 'READY' ? '#ECFDF5' : '#EFF6FF',
                    border: uploadState === 'FAILED' ? '1px solid #FECACA' : uploadState === 'READY' ? '1px solid #A7F3D0' : '1px solid #BFDBFE',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      {uploadState === 'READY' ? (
                        <CheckCircle2 size={18} color="#059669" />
                      ) : uploadState === 'FAILED' ? (
                        <AlertCircle size={18} color="#DC2626" />
                      ) : (
                        <div style={{ width: '16px', height: '16px', border: '2px solid #2563EB', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                      )}
                      <div>
                        <span style={{ 
                          fontSize: '0.68rem', 
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          color: uploadState === 'READY' ? '#065F46' : uploadState === 'FAILED' ? '#991B1B' : '#1E40AF',
                          display: 'block'
                        }}>
                          Ingestion Status: {uploadState}
                        </span>
                        <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#0F172A', marginTop: '1px' }}>
                          {uploadProgressMsg}
                        </div>
                      </div>
                    </div>

                    {uploadState === 'READY' && uploadedDoc && (
                      <span className="badge badge-emerald" style={{ fontSize: '0.72rem' }}>
                        {uploadedDoc.chunk_count || 15} Chunks Indexed
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Section 2: Pedagogical Parameter Matrix */}
          <div className="glass-panel" style={{ padding: '22px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid #E2E8F0', paddingBottom: '12px' }}>
              <Compass size={17} color="#2563EB" />
              <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#0F172A' }}>
                2. Pedagogical Architecture & Learner Modeling
              </h3>
            </div>

            {/* Matrix Form Groups */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
              
              {/* Educational Level */}
              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '5px' }}>
                  Educational Level
                </label>
                <select 
                  value={level} 
                  onChange={(e) => setLevel(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '7px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A', fontSize: '0.84rem' }}
                >
                  <option value="beginner">Beginner (Foundations & Intuition)</option>
                  <option value="intermediate">Intermediate (Standard Curriculum)</option>
                  <option value="advanced">Advanced (Deep Dive & Rigor)</option>
                </select>
              </div>

              {/* Existing Knowledge */}
              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '5px' }}>
                  Existing Knowledge
                </label>
                <select 
                  value={existingKnowledge} 
                  onChange={(e) => setExistingKnowledge(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '7px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A', fontSize: '0.84rem' }}
                >
                  <option value="New to this">New to this (First encounter)</option>
                  <option value="Somewhat familiar">Somewhat familiar (Basic recall)</option>
                  <option value="I know the basics">Know the basics (Ready for rigor)</option>
                </select>
              </div>

              {/* Learning Objective */}
              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '5px' }}>
                  Learning Objective
                </label>
                <select 
                  value={goal} 
                  onChange={(e) => setGoal(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '7px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A', fontSize: '0.84rem' }}
                >
                  <option value="Understand concept">Understand concept intuitively</option>
                  <option value="Exam preparation">Exam preparation & Problem Solving</option>
                  <option value="Practical application">Practical Application & Labs</option>
                  <option value="Deep understanding">Theoretical Mathematical Proofs</option>
                </select>
              </div>

              {/* Teaching Style */}
              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '5px' }}>
                  Instructional Strategy
                </label>
                <select 
                  value={style} 
                  onChange={(e) => setStyle(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '7px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A', fontSize: '0.84rem' }}
                >
                  <option value="analogy_driven">Analogy-Driven (Intuitive Models)</option>
                  <option value="visual">Visual Demonstration First</option>
                  <option value="interactive">Socratic Question & Probe</option>
                  <option value="rigorous">Formulaic & Mathematical Rigor</option>
                </select>
              </div>

              {/* Language */}
              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '5px' }}>
                  Spoken Delivery Language
                </label>
                <select 
                  value={language} 
                  onChange={(e) => setLanguage(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '7px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A', fontSize: '0.84rem' }}
                >
                  <option value="Hinglish">Hinglish (Natural & Spoken)</option>
                  <option value="English">English (Standard Academic)</option>
                  <option value="Hindi">Hindi (शुद्ध हिंदी)</option>
                </select>
              </div>

              {/* Available Time */}
              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '5px' }}>
                  Session Budget (Duration)
                </label>
                <select 
                  value={duration} 
                  onChange={(e) => setDuration(Number(e.target.value))}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '7px', background: '#FFFFFF', border: '1px solid #CBD5E1', color: '#0F172A', fontSize: '0.84rem' }}
                >
                  <option value={5}>5 minutes (Speed Overview)</option>
                  <option value={20}>20 minutes (Interactive Standard)</option>
                  <option value={60}>60 minutes (Comprehensive Lecture)</option>
                </select>
              </div>

            </div>
          </div>
        </div>

        {/* RIGHT PANE: Live Session Blueprint & Inspector Card */}
        <div style={{ position: 'sticky', top: '84px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          <div className="glass-panel" style={{ padding: '22px', display: 'flex', flexDirection: 'column', gap: '18px', border: '1px solid #E2E8F0' }}>
            
            {/* Inspector Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #E2E8F0', paddingBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
                <Cpu size={16} color="#2563EB" />
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0F172A' }}>
                  Session Blueprint Inspector
                </span>
              </div>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', color: '#059669', fontWeight: 700, background: '#ECFDF5', padding: '2px 8px', borderRadius: '12px', border: '1px solid #A7F3D0' }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10B981' }} />
                Ready
              </span>
            </div>

            {/* Session Parameters At-A-Glance */}
            <div style={{ background: '#F8FAFC', borderRadius: '8px', padding: '12px 14px', border: '1px solid #E2E8F0', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748B', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
                Active Configuration
              </div>
              <div style={{ fontSize: '0.94rem', fontWeight: 800, color: '#0F172A' }}>
                {topic || "Custom Topic"}
              </div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                <span className="badge badge-indigo" style={{ fontSize: '0.7rem' }}>{level}</span>
                <span className="badge badge-emerald" style={{ fontSize: '0.7rem' }}>{language}</span>
                <span className="badge badge-amber" style={{ fontSize: '0.7rem' }}>{duration} mins</span>
              </div>
            </div>

            {/* Curriculum Roadmap Execution Pipeline */}
            <div>
              <span style={{ fontSize: '0.72rem', color: '#64748B', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em', display: 'block', marginBottom: '8px' }}>
                Autonomous Execution Pipeline
              </span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#334155' }}>
                  <div style={{ width: '18px', height: '18px', borderRadius: '50%', background: '#EFF6FF', color: '#2563EB', fontSize: '0.68rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>1</div>
                  <span>Concept Intuition & Analogy Framing</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#334155' }}>
                  <div style={{ width: '18px', height: '18px', borderRadius: '50%', background: '#EFF6FF', color: '#2563EB', fontSize: '0.68rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>2</div>
                  <span>Interactive Smart Whiteboard Simulation</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#334155' }}>
                  <div style={{ width: '18px', height: '18px', borderRadius: '50%', background: '#EFF6FF', color: '#2563EB', fontSize: '0.68rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>3</div>
                  <span>Socratic Diagnostic Probe & Misconception Check</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#334155' }}>
                  <div style={{ width: '18px', height: '18px', borderRadius: '50%', background: '#EFF6FF', color: '#2563EB', fontSize: '0.68rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>4</div>
                  <span>Dynamic Adaptation / Second Explanation Loop</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#334155' }}>
                  <div style={{ width: '18px', height: '18px', borderRadius: '50%', background: '#EFF6FF', color: '#2563EB', fontSize: '0.68rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>5</div>
                  <span>Summative Assessment & Learning Mastery Report</span>
                </div>
              </div>
            </div>

            {/* Subsystem Readiness Matrix */}
            <div style={{ borderTop: '1px solid #E2E8F0', paddingTop: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748B' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <Video size={13} color="#059669" /> Spoken Avatar Engine
                </span>
                <span style={{ color: '#059669', fontWeight: 700 }}>Synchronized</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748B' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <Activity size={13} color="#059669" /> Smart Whiteboard
                </span>
                <span style={{ color: '#059669', fontWeight: 700 }}>Interactive</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748B' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <ShieldCheck size={13} color="#059669" /> Hallucination Guard
                </span>
                <span style={{ color: '#059669', fontWeight: 700 }}>Active</span>
              </div>
            </div>

            {/* Primary Action Button */}
            <button 
              id="btn-start-configured-lesson"
              type="button" 
              onClick={handleSubmit} 
              className="btn btn-primary"
              style={{ padding: '12px 18px', width: '100%', fontSize: '0.92rem', borderRadius: '8px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}
            >
              <Sparkles size={16} />
              <span>Launch Teaching Session</span>
              <span style={{ fontSize: '0.72rem', opacity: 0.85, background: 'rgba(255,255,255,0.25)', padding: '2px 6px', borderRadius: '4px', marginLeft: 'auto' }}>
                Ctrl+Enter
              </span>
            </button>

          </div>

        </div>

      </div>

    </div>
  );
}
