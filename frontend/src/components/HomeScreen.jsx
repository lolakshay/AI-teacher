import React from 'react';
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
  ShieldCheck
} from 'lucide-react';

export default function HomeScreen({ onStartLearning, onLaunchCanonicalDemo, onOpenUpload, onChooseTopic }) {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px', display: 'flex', flexDirection: 'column', gap: '48px' }}>
      
      {/* Hero Section */}
      <section style={{ 
        textAlign: 'center', 
        padding: '56px 32px', 
        borderRadius: '24px',
        background: 'linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 50%, #F1F5F9 100%)',
        border: '1px solid #CBD5E1',
        boxShadow: 'var(--shadow-md)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '20px'
      }}>
        {/* Academic Badge */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '5px 14px', borderRadius: '20px', background: '#EFF6FF', border: '1px solid #BFDBFE', color: '#1D4ED8', fontSize: '0.82rem', fontWeight: 600 }}>
          <GraduationCap size={15} />
          <span>Adaptive Multi-Modal STEM Education</span>
        </div>

        {/* Main Title */}
        <h1 style={{ 
          fontSize: 'clamp(2.2rem, 5vw, 3.4rem)', 
          fontWeight: 800, 
          letterSpacing: '-0.03em',
          lineHeight: 1.15,
          color: '#0F172A',
          maxWidth: '900px'
        }}>
          An AI Teacher That Teaches You Through Video
        </h1>

        {/* Subtitle */}
        <p style={{ 
          fontSize: 'clamp(1.05rem, 2vw, 1.25rem)', 
          color: '#475569', 
          maxWidth: '720px', 
          lineHeight: 1.6 
        }}>
          Your AI teacher adapts explanations, examples, questions, and difficulty to how you learn. Experience video-first instruction, dynamic interactive whiteboards, diagnostic probes, and real-time misconception remediation.
        </p>

        {/* Primary CTA Buttons */}
        <div style={{ display: 'flex', gap: '16px', marginTop: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
          <button 
            id="btn-home-start-learning"
            className="btn btn-primary"
            onClick={onStartLearning}
            style={{ padding: '12px 28px', fontSize: '1rem', borderRadius: '10px' }}
          >
            <span>Start Learning</span>
            <ArrowRight size={18} />
          </button>

          <button 
            id="btn-home-canonical-demo"
            className="btn btn-amber"
            onClick={onLaunchCanonicalDemo}
            style={{ padding: '12px 24px', fontSize: '1rem', borderRadius: '10px' }}
            title="Launch guided Ohm's Law demonstration"
          >
            <Play size={16} fill="currentColor" />
            <span>Demo Lesson (Ohm's Law)</span>
          </button>
        </div>

        {/* Secondary Quick Jump Options */}
        <div style={{ display: 'flex', gap: '12px', marginTop: '8px', color: 'var(--text-muted)', fontSize: '0.9rem', alignItems: 'center' }}>
          <span>Or explore via:</span>
          <button 
            onClick={onOpenUpload}
            className="btn btn-secondary" 
            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
          >
            <UploadCloud size={14} />
            <span>Upload Material</span>
          </button>
          <button 
            onClick={onChooseTopic}
            className="btn btn-secondary" 
            style={{ padding: '6px 14px', fontSize: '0.82rem' }}
          >
            <BookOpen size={14} />
            <span>Choose a Topic</span>
          </button>
        </div>
      </section>

      {/* The 6-Stage Learning Journey Grid */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0F172A' }}>The Autonomous Pedagogical Journey</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginTop: '4px' }}>
            Built to teach, not just chat. Experience complete closed-loop adaptive education.
          </p>
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', 
          gap: '20px' 
        }}>
          {/* Card 1 */}
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
              <BookOpen size={20} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>1. Topic or Material Input</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Choose any topic or upload textbooks, notes, and PDFs. Grounded via RAG to ensure zero educational hallucination.
            </p>
          </div>

          {/* Card 2 */}
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#F0FDF4', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#059669' }}>
              <BrainCircuit size={20} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>2. Personalized Lesson Plan</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Tailors language (English, Hindi, Hinglish), educational depth, available time, and teaching style to your exact profile.
            </p>
          </div>

          {/* Card 3 */}
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
              <Video size={20} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>3. Human-Like Video Teacher</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Animated avatar with real-time lip synchronization, emotional responsiveness, and natural spoken pedagogy.
            </p>
          </div>

          {/* Card 4 */}
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#FFFBEB', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#D97706' }}>
              <Activity size={20} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>4. Dynamic Educational Visuals</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Subject-aware smart whiteboard: interactive circuit simulators, step-by-step KaTeX math derivations, and algorithm code tracers.
            </p>
          </div>

          {/* Card 5 */}
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#FEF2F2', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#DC2626' }}>
              <BrainCircuit size={20} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>5. Active Adaptation & Remediation</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Diagnoses underlying misconceptions in student answers and dynamically adapts using alternative analogies, simpler models, and visual proofs.
            </p>
          </div>

          {/* Card 6 */}
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#F5F3FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#7C3AED' }}>
              <Award size={20} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>6. Assessment & Learning Report</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Summative multi-question assessment and an actionable learning report detailing mastered concepts, revision drills, and next topics.
            </p>
          </div>
        </div>
      </section>

      {/* Trust & Transparency Note */}
      <footer style={{ textAlign: 'center', borderTop: '1px solid var(--border-subtle)', paddingTop: '20px', color: 'var(--text-muted)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
        <ShieldCheck size={16} color="#10B981" />
        <span>AI Teacher uses AI-generated pedagogical avatars and grounded curriculum engines. Designed for high-fidelity personalized education.</span>
      </footer>
    </div>
  );
}
