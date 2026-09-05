import React, { useEffect, useState } from 'react';
import { Sparkles, CheckCircle2, BookOpen, Layers, Video, Activity } from 'lucide-react';

export default function LessonPreparing({ topic, language, level, isReady, onPreparationComplete }) {
  const [activeStage, setActiveStage] = useState(0);

  const stages = [
    { title: "Understanding learning objectives & prerequisites", icon: <BookOpen size={18} /> },
    { title: "Planning concept progression & pedagogical strategy", icon: <Layers size={18} /> },
    { title: "Preparing subject-aware visuals & interactive simulations", icon: <Activity size={18} /> },
    { title: "Preparing your AI Teacher avatar & voice engine", icon: <Video size={18} /> }
  ];

  useEffect(() => {
    const timer1 = setTimeout(() => setActiveStage(1), 600);
    const timer2 = setTimeout(() => setActiveStage(2), 1200);
    const timer3 = setTimeout(() => setActiveStage(3), 1800);
    const timer4 = setTimeout(() => {
      setActiveStage(4);
      if (onPreparationComplete) {
        onPreparationComplete();
      }
    }, 2400);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, [onPreparationComplete]);

  return (
    <div style={{ maxWidth: '640px', margin: '80px auto', padding: '0 20px' }}>
      <div className="glass-panel" style={{ padding: '40px 32px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '24px' }}>
        
        {/* Animated Glow Spinner */}
        <div style={{ position: 'relative', width: '80px', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{
            position: 'absolute',
            inset: 0,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #6366F1, #06B6D4)',
            filter: 'blur(12px)',
            opacity: 0.5,
            animation: 'speakingPulse 2s infinite ease-in-out'
          }} />
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: '#EFF6FF',
            border: '2px solid #2563EB',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2
          }}>
            <Sparkles size={28} color="#2563EB" />
          </div>
        </div>

        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0F172A' }}>
            Preparing Your AI Teacher Lesson
          </h2>
          <p style={{ fontSize: '0.9rem', color: '#475569', marginTop: '4px' }}>
            Topic: <strong style={{ color: '#0F172A' }}>{topic}</strong> • {level} • {language}
          </p>
        </div>

        {/* Stages Checklist */}
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '12px', textAlign: 'left', marginTop: '8px' }}>
          {stages.map((stage, idx) => {
            const isCompleted = activeStage > idx;
            const isCurrent = activeStage === idx;

            return (
              <div 
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px',
                  padding: '12px 16px',
                  borderRadius: '10px',
                  background: isCurrent ? '#EFF6FF' : isCompleted ? '#ECFDF5' : '#F8FAFC',
                  border: isCurrent ? '1.5px solid #2563EB' : isCompleted ? '1px solid #A7F3D0' : '1px solid #E2E8F0',
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{ color: isCompleted ? '#059669' : isCurrent ? '#2563EB' : '#94A3B8' }}>
                  {isCompleted ? <CheckCircle2 size={20} color="#059669" /> : stage.icon}
                </div>
                <span style={{ 
                  fontSize: '0.9rem', 
                  fontWeight: isCurrent || isCompleted ? 600 : 400,
                  color: isCompleted ? '#065F46' : isCurrent ? '#1E40AF' : '#64748B'
                }}>
                  {stage.title}
                </span>
                {isCurrent && (
                  <div style={{ marginLeft: 'auto', width: '14px', height: '14px', border: '2px solid #2563EB', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                )}
              </div>
            );
          })}
        </div>

        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Please hold on while your personalized pedagogical trajectory is initialized.
        </span>
      </div>
    </div>
  );
}
