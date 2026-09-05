import React, { useState, useEffect } from 'react';
import { Volume2, VolumeX, Sparkles, Brain, Award } from 'lucide-react';

export default function TeacherAvatar({ isSpeaking, emotion = 'explaining', onToggleMute, isMuted }) {
  const [mouthOpen, setMouthOpen] = useState(false);
  const [blinking, setBlinking] = useState(false);

  // Sync mouth animation with speech state
  useEffect(() => {
    let mouthInterval = null;
    if (isSpeaking) {
      mouthInterval = setInterval(() => {
        setMouthOpen(prev => !prev);
      }, 140);
    } else {
      setMouthOpen(false);
    }
    return () => {
      if (mouthInterval) clearInterval(mouthInterval);
    };
  }, [isSpeaking]);

  // Random natural eye blinking
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setBlinking(true);
      setTimeout(() => setBlinking(false), 180);
    }, 3800);
    return () => clearInterval(blinkInterval);
  }, []);

  const getEmotionBadge = () => {
    switch (emotion) {
      case 'encouraging':
        return { label: 'Encouraging & Patient', badgeClass: 'badge-emerald', icon: <Sparkles size={12} /> };
      case 'thoughtful':
        return { label: 'Deep Reasoning', badgeClass: 'badge-amber', icon: <Brain size={12} /> };
      case 'celebrating':
        return { label: 'Mastery Achieved!', badgeClass: 'badge-cyan', icon: <Award size={12} /> };
      case 'attentive':
        return { label: 'Listening Attentively', badgeClass: 'badge-indigo', icon: <Volume2 size={12} /> };
      default:
        return { label: 'Actively Teaching', badgeClass: 'badge-indigo', icon: <Volume2 size={12} /> };
    }
  };

  const badgeInfo = getEmotionBadge();

  return (
    <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
      {/* Status Badges */}
      <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <span className={`badge ${badgeInfo.badgeClass}`}>
          {badgeInfo.icon}
          <span>{badgeInfo.label}</span>
        </span>
        <button 
          onClick={onToggleMute}
          className="btn btn-secondary"
          style={{ padding: '6px 10px', fontSize: '0.8rem', borderRadius: '8px' }}
          title={isMuted ? "Unmute Voice" : "Mute Voice"}
        >
          {isMuted ? <VolumeX size={14} /> : <Volume2 size={14} color="#10B981" />}
          <span>{isMuted ? "Muted" : "Voice On"}</span>
        </button>
      </div>

      {/* SVG Animated Avatar Canvas */}
      <div 
        className={`avatar-breathing ${isSpeaking ? 'avatar-speaking' : ''}`}
        style={{
          width: '180px',
          height: '210px',
          position: 'relative',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center'
        }}
      >
        <svg viewBox="0 0 200 240" width="100%" height="100%" style={{ overflow: 'visible' }}>
          <defs>
            <radialGradient id="avatarGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#2563EB" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#2563EB" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="suitGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#1E293B" />
              <stop offset="100%" stopColor="#0F172A" />
            </linearGradient>
            <linearGradient id="tieGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#2563EB" />
              <stop offset="100%" stopColor="#1D4ED8" />
            </linearGradient>
            <linearGradient id="skinGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#FBD5B5" />
              <stop offset="100%" stopColor="#F2BA8C" />
            </linearGradient>
            <linearGradient id="hairGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#334155" />
              <stop offset="100%" stopColor="#1E293B" />
            </linearGradient>
          </defs>

          {/* Background Ambient Glow */}
          <circle cx="100" cy="110" r="95" fill="url(#avatarGlow)" />

          {/* Teacher Torso / Blazer */}
          <path d="M 40 240 L 48 160 Q 100 175 152 160 L 160 240 Z" fill="url(#suitGrad)" stroke="#334155" strokeWidth="2" />
          
          {/* White Shirt Collar */}
          <polygon points="85,160 100,185 115,160 100,165" fill="#F8FAFC" />
          {/* Tie */}
          <polygon points="96,170 104,170 106,215 100,225 94,215" fill="url(#tieGrad)" />

          {/* Neck */}
          <rect x="88" y="132" width="24" height="30" rx="4" fill="url(#skinGrad)" />

          {/* Head */}
          <ellipse cx="100" cy="95" rx="46" ry="52" fill="url(#skinGrad)" stroke="#DDA87A" strokeWidth="1.5" />

          {/* Hair */}
          <path d="M 52 82 Q 100 35 148 82 Q 155 105 148 115 Q 142 80 100 70 Q 58 80 52 115 Z" fill="url(#hairGrad)" />

          {/* Eyebrows */}
          <path d="M 72 74 Q 82 70 90 74" stroke="#1E293B" strokeWidth="3" strokeLinecap="round" fill="none" />
          <path d="M 110 74 Q 118 70 128 74" stroke="#1E293B" strokeWidth="3" strokeLinecap="round" fill="none" />

          {/* Eyes (with blinking logic) */}
          {blinking ? (
            <>
              <line x1="72" y1="88" x2="88" y2="88" stroke="#1E293B" strokeWidth="2.5" strokeLinecap="round" />
              <line x1="112" y1="88" x2="128" y2="88" stroke="#1E293B" strokeWidth="2.5" strokeLinecap="round" />
            </>
          ) : (
            <>
              <ellipse cx="80" cy="88" rx="7" ry="5" fill="#FFF" />
              <circle cx="81" cy="88" r="3.5" fill="#312E81" />
              <circle cx="82" cy="87" r="1" fill="#FFF" />

              <ellipse cx="120" cy="88" rx="7" ry="5" fill="#FFF" />
              <circle cx="119" cy="88" r="3.5" fill="#312E81" />
              <circle cx="120" cy="87" r="1" fill="#FFF" />
            </>
          )}

          {/* Glasses */}
          <rect x="68" y="78" width="24" height="18" rx="4" fill="none" stroke="#2563EB" strokeWidth="2" />
          <rect x="108" y="78" width="24" height="18" rx="4" fill="none" stroke="#2563EB" strokeWidth="2" />
          <line x1="92" y1="85" x2="108" y2="85" stroke="#2563EB" strokeWidth="2" />

          {/* Nose */}
          <path d="M 98 94 L 102 104 L 96 106" stroke="#C88E63" strokeWidth="2" strokeLinecap="round" fill="none" />

          {/* Mouth (with live lip-sync animation) */}
          {mouthOpen ? (
            <path d="M 90 120 Q 100 134 110 120 Q 100 128 90 120 Z" fill="#991B1B" stroke="#7F1D1D" strokeWidth="1" />
          ) : (
            <path d="M 90 122 Q 100 128 110 122" stroke="#A16207" strokeWidth="2.5" strokeLinecap="round" fill="none" />
          )}

          {/* Pointing Hand towards Smart Whiteboard */}
          <g transform="translate(142, 170)">
            <path d="M 0 10 Q 25 -5 45 -18 L 48 -14 Q 28 5 5 24 Z" fill="url(#skinGrad)" stroke="#DDA87A" strokeWidth="1.2" />
            {/* Laser Pointer beam to board */}
            <line x1="46" y1="-17" x2="72" y2="-32" stroke="#06B6D4" strokeWidth="2" strokeDasharray="3,3" />
          </g>
        </svg>
      </div>

      {/* Voice Wave Indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', height: '20px', marginTop: '6px' }}>
        {[40, 75, 100, 60, 90, 45, 80].map((height, i) => (
          <div 
            key={i}
            style={{
              width: '3px',
              height: isSpeaking ? `${height}%` : '4px',
              backgroundColor: isSpeaking ? '#2563EB' : '#334155',
              borderRadius: '2px',
              transition: 'height 0.15s ease-in-out'
            }}
          />
        ))}
      </div>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
        {isSpeaking ? 'AI Teacher is speaking...' : 'AI Teacher listening / observing'}
      </span>
    </div>
  );
}
