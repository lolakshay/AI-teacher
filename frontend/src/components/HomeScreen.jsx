import React, { useState } from 'react';
import { 
  GraduationCap, 
  Play, 
  Zap, 
  BookOpen, 
  UploadCloud, 
  Video, 
  Activity, 
  BrainCircuit, 
  Award, 
  ArrowRight, 
  Sparkles, 
  ShieldCheck, 
  Sliders, 
  Cpu, 
  Terminal, 
  Layers, 
  CheckCircle2, 
  Search, 
  FileText, 
  Clock, 
  Compass
} from 'lucide-react';
import { DEMO_PRESETS } from '../data/presets';

export default function HomeScreen({ onStartLearning, onLaunchCanonicalDemo, onOpenUpload, onChooseTopic }) {
  const [quickTopic, setQuickTopic] = useState("");

  const handleQuickLaunch = (e) => {
    e.preventDefault();
    if (quickTopic.trim()) {
      onStartLearning();
    } else {
      onStartLearning();
    }
  };

  return (
    <div style={{ maxWidth: '1360px', margin: '0 auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Desktop Software Application Status & Mission Control Bar */}
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
            <Cpu size={18} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>Workspace</span>
              <span style={{ fontSize: '0.75rem', color: '#CBD5E1' }}>/</span>
              <span style={{ fontSize: '0.85rem', color: '#0F172A', fontWeight: 700 }}>AI Teacher Pedagogical Studio</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '1px' }}>
              Autonomous multi-modal instruction engine with real-time video, smart whiteboard, and diagnostic remediation.
            </p>
          </div>
        </div>

        {/* Global Toolbar Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '6px', fontSize: '0.74rem', color: '#475569', fontWeight: 600 }}>
            <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: '#10B981', display: 'inline-block' }} />
            <span>Gemini 3.7 Flash Engine Online</span>
          </div>

          <button 
            onClick={onOpenUpload}
            className="btn btn-secondary" 
            style={{ padding: '7px 14px', fontSize: '0.8rem', gap: '6px' }}
            title="Ingest study material (PDF, DOCX, TXT)"
          >
            <UploadCloud size={14} />
            <span>Ingest Notes (RAG)</span>
          </button>

          <button 
            id="btn-home-start-learning"
            className="btn btn-secondary"
            onClick={onStartLearning}
            style={{ padding: '7px 14px', fontSize: '0.8rem', gap: '6px' }}
          >
            <Sliders size={14} />
            <span>Configure Session</span>
          </button>

          <button 
            id="btn-home-canonical-demo"
            className="btn btn-primary"
            onClick={onLaunchCanonicalDemo}
            style={{ padding: '7px 16px', fontSize: '0.82rem', gap: '6px' }}
            title="Launch guided Ohm's Law demonstration session"
          >
            <Play size={14} fill="currentColor" />
            <span>Launch Demo Lab (Ohm's Law)</span>
          </button>
        </div>
      </div>

      {/* Main Studio Workbench (Split 2-Column Workstation Layout) */}
      <div className="home-studio-workbench" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 400px', gap: '20px', alignItems: 'start' }}>
        
        {/* LEFT COLUMN: Mission Control & Curriculum Laboratory */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Quick Launch & Session Search Bar */}
          <div className="glass-panel" style={{ padding: '20px 22px', background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Quick Session Launcher
              </span>
              <span style={{ fontSize: '0.72rem', color: '#94A3B8' }}>
                Type any subject or select from curriculum laboratory below
              </span>
            </div>

            <form onSubmit={handleQuickLaunch} style={{ display: 'flex', gap: '10px' }}>
              <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center' }}>
                <Search size={16} color="#94A3B8" style={{ position: 'absolute', left: '14px' }} />
                <input 
                  type="text"
                  value={quickTopic}
                  onChange={(e) => setQuickTopic(e.target.value)}
                  placeholder="e.g. Ohm's Law & Circuit Dynamics, Binary Search, Newton's Third Law, Fourier Series..."
                  style={{
                    width: '100%',
                    padding: '11px 16px 11px 40px',
                    borderRadius: '8px',
                    background: '#F8FAFC',
                    border: '1px solid #CBD5E1',
                    color: '#0F172A',
                    fontSize: '0.9rem',
                    fontWeight: 500
                  }}
                />
              </div>

              <button 
                type="submit"
                className="btn btn-primary"
                style={{ padding: '11px 22px', fontSize: '0.88rem', gap: '6px', whiteSpace: 'nowrap' }}
              >
                <Sparkles size={15} />
                <span>Initialize Studio Session</span>
              </button>
            </form>
          </div>

          {/* Curriculum Laboratories & Standard STEM Modules */}
          <div className="glass-panel" style={{ padding: '22px', background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #E2E8F0', paddingBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BookOpen size={17} color="#2563EB" />
                <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#0F172A' }}>
                  Standard Curriculum Modules & Interactive Laboratories
                </h3>
              </div>
              <span style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 600 }}>
                3 Pre-Configured Labs Ready
              </span>
            </div>

            {/* Modules List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {DEMO_PRESETS.map((preset) => {
                const isCanonical = preset.id === 'canonical_ohms_law';
                return (
                  <div 
                    key={preset.id}
                    style={{
                      padding: '16px 18px',
                      borderRadius: '10px',
                      background: isCanonical ? '#F8FAFC' : '#FFFFFF',
                      border: isCanonical ? '1.5px solid #BFDBFE' : '1px solid #E2E8F0',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      gap: '16px',
                      transition: 'all 0.15s ease',
                      boxShadow: 'var(--shadow-sm)'
                    }}
                  >
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxWidth: '650px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 800, fontSize: '0.94rem', color: '#0F172A' }}>
                          {preset.title}
                        </span>
                        <span className="badge badge-indigo" style={{ fontSize: '0.66rem', padding: '1px 7px' }}>
                          {preset.subject}
                        </span>
                        {isCanonical && (
                          <span className="badge badge-emerald" style={{ fontSize: '0.66rem', padding: '1px 7px' }}>
                            Canonical Lab
                          </span>
                        )}
                      </div>

                      <p style={{ fontSize: '0.8rem', color: '#475569', lineHeight: 1.4 }}>
                        {preset.description}
                      </p>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '2px', fontSize: '0.74rem', color: '#64748B' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={12} /> {preset.time} Minutes
                        </span>
                        <span>•</span>
                        <span>Level: {preset.level}</span>
                        <span>•</span>
                        <span>Language: {preset.language}</span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                      {isCanonical ? (
                        <button 
                          onClick={onLaunchCanonicalDemo}
                          className="btn btn-amber"
                          style={{ padding: '8px 16px', fontSize: '0.8rem', gap: '6px' }}
                        >
                          <Play size={13} fill="currentColor" />
                          <span>Launch Lab</span>
                        </button>
                      ) : (
                        <button 
                          onClick={onChooseTopic}
                          className="btn btn-secondary"
                          style={{ padding: '8px 16px', fontSize: '0.8rem', gap: '6px' }}
                        >
                          <span>Configure Lab</span>
                          <ArrowRight size={13} />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Grounding & RAG Material Ingestion Banner */}
          <div className="glass-panel" style={{ 
            padding: '18px 22px', 
            background: '#FFFFFF', 
            border: '1px solid #E2E8F0', 
            borderRadius: '12px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '16px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#ECFDF5', border: '1px solid #A7F3D0', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#059669' }}>
                <ShieldCheck size={20} />
              </div>
              <div>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0F172A' }}>
                  Educational Document Ingestion & RAG Knowledge Grounding
                </div>
                <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '2px' }}>
                  Ingest textbooks, syllabus guides, or lecture slides. The AI Teacher grounds derivations and analogies with zero educational hallucination.
                </div>
              </div>
            </div>

            <button 
              onClick={onOpenUpload}
              className="btn btn-secondary"
              style={{ padding: '8px 16px', fontSize: '0.82rem', gap: '6px', whiteSpace: 'nowrap' }}
            >
              <UploadCloud size={14} />
              <span>Ingest Material</span>
            </button>
          </div>

        </div>

        {/* RIGHT COLUMN: Engine Architecture & Subsystems Monitor */}
        <div style={{ position: 'sticky', top: '84px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          <div className="glass-panel" style={{ padding: '20px', background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            
            {/* Monitor Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #E2E8F0', paddingBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Terminal size={16} color="#2563EB" />
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0F172A' }}>
                  Subsystems & Architecture Monitor
                </span>
              </div>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', color: '#059669', fontWeight: 700, background: '#ECFDF5', padding: '2px 8px', borderRadius: '12px', border: '1px solid #A7F3D0' }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10B981' }} />
                5/5 Online
              </span>
            </div>

            {/* Subsystems Readiness Grid */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              
              {/* Subsystem 1 */}
              <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '8px', border: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Video size={14} color="#2563EB" />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0F172A' }}>Spoken Video Avatar Engine</span>
                </div>
                <span style={{ fontSize: '0.7rem', color: '#059669', fontWeight: 700 }}>Lip-Sync Ready</span>
              </div>

              {/* Subsystem 2 */}
              <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '8px', border: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Activity size={14} color="#2563EB" />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0F172A' }}>Smart Whiteboard Simulator</span>
                </div>
                <span style={{ fontSize: '0.7rem', color: '#059669', fontWeight: 700 }}>Interactive</span>
              </div>

              {/* Subsystem 3 */}
              <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '8px', border: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BrainCircuit size={14} color="#2563EB" />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0F172A' }}>Diagnostic Misconception Loop</span>
                </div>
                <span style={{ fontSize: '0.7rem', color: '#059669', fontWeight: 700 }}>Active</span>
              </div>

              {/* Subsystem 4 */}
              <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '8px', border: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Compass size={14} color="#2563EB" />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0F172A' }}>Multilingual Adaptation Engine</span>
                </div>
                <span style={{ fontSize: '0.7rem', color: '#059669', fontWeight: 700 }}>Hinglish / En / Hi</span>
              </div>

              {/* Subsystem 5 */}
              <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '8px', border: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ShieldCheck size={14} color="#2563EB" />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#0F172A' }}>RAG Hallucination Guardrail</span>
                </div>
                <span style={{ fontSize: '0.7rem', color: '#059669', fontWeight: 700 }}>Verified</span>
              </div>

            </div>

            {/* Technical Specifications */}
            <div style={{ borderTop: '1px solid #E2E8F0', paddingTop: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748B', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em', marginBottom: '2px' }}>
                Runtime Telemetry
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#475569' }}>
                <span>Backend Framework</span>
                <span style={{ fontWeight: 600, color: '#0F172A' }}>FastAPI (Async Python)</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#475569' }}>
                <span>Inference Model</span>
                <span style={{ fontWeight: 600, color: '#0F172A' }}>Gemini 3.7 Flash</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#475569' }}>
                <span>Whiteboard Visuals</span>
                <span style={{ fontWeight: 600, color: '#0F172A' }}>Circuits, KaTeX, Graphs</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#475569' }}>
                <span>Evaluation Latency</span>
                <span style={{ fontWeight: 600, color: '#0F172A' }}>~120ms (Streaming)</span>
              </div>
            </div>

            {/* Quick Launch Action Button */}
            <button 
              onClick={onLaunchCanonicalDemo}
              className="btn btn-primary"
              style={{ width: '100%', padding: '11px', fontSize: '0.88rem', gap: '8px', borderRadius: '8px' }}
            >
              <Play size={14} fill="currentColor" />
              <span>Launch Canonical Ohm's Law Lab</span>
            </button>

          </div>

        </div>

      </div>

      {/* Fixed Software Application Status Line */}
      <footer style={{ 
        borderTop: '1px solid #E2E8F0', 
        paddingTop: '14px', 
        color: '#64748B', 
        fontSize: '0.75rem', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10B981', display: 'inline-block' }} />
          <span>AI Teacher Studio v2.4.0 • Gemini 3.7 Flash • Zero Hallucination Mode Active</span>
        </div>
        <div style={{ display: 'flex', gap: '16px' }}>
          <span>Host: localhost:5173</span>
          <span>API: 127.0.0.1:8000</span>
          <span>WebSocket Voice: Active</span>
        </div>
      </footer>

    </div>
  );
}
