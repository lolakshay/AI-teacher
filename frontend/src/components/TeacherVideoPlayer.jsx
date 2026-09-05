import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Volume2, 
  VolumeX, 
  Subtitles, 
  Maximize2, 
  Sparkles, 
  Brain, 
  Award,
  Video,
  FileText,
  Headphones
} from 'lucide-react';

export default function TeacherVideoPlayer({ 
  isSpeaking, 
  emotion = 'explaining', 
  isMuted, 
  onToggleMute, 
  onReplay, 
  transcriptText = '',
  language = 'English',
  fallbackMode = 'video', // 'video' | 'audio_visual' | 'text_visual'
  onChangeFallbackMode
}) {
  const [isPlaying, setIsPlaying] = useState(true);
  const [showCaptions, setShowCaptions] = useState(true);
  const [speed, setSpeed] = useState(1.0);
  const [mouthOpen, setMouthOpen] = useState(false);
  const [blinking, setBlinking] = useState(false);

  // Mouth animation synchronized with speech
  useEffect(() => {
    let mouthInterval = null;
    if (isSpeaking && isPlaying) {
      mouthInterval = setInterval(() => {
        setMouthOpen(prev => !prev);
      }, 140 / speed);
    } else {
      setMouthOpen(false);
    }
    return () => {
      if (mouthInterval) clearInterval(mouthInterval);
    };
  }, [isSpeaking, isPlaying, speed]);

  // Natural blinking
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
    <div className="glass-panel" style={{ 
      padding: '16px', 
      display: 'flex', 
      flexDirection: 'column', 
      gap: '12px', 
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Top Controls Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className={`badge ${badgeInfo.badgeClass}`}>
            {badgeInfo.icon}
            <span>{badgeInfo.label}</span>
          </span>
        </div>

        {/* Fallback Mode Selector Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <select 
            value={fallbackMode} 
            onChange={(e) => onChangeFallbackMode && onChangeFallbackMode(e.target.value)}
            title="Video / Audio / Text Fallback Modes"
            style={{ 
              background: '#FFFFFF', 
              border: '1px solid #CBD5E1', 
              color: '#1E293B', 
              fontSize: '0.74rem',
              fontWeight: 600,
              borderRadius: '6px',
              padding: '4px 8px',
              cursor: 'pointer'
            }}
          >
            <option value="video">Interactive Video</option>
            <option value="audio_visual">Audio & Whiteboard</option>
            <option value="text_visual">Text & Whiteboard</option>
          </select>
        </div>
      </div>

      {/* Main Video Viewport Canvas */}
      <div style={{ 
        position: 'relative', 
        width: '100%', 
        height: '220px', 
        minHeight: '220px',
        flexShrink: 0,
        background: 'linear-gradient(180deg, #F8FAFC 0%, #E2E8F0 100%)',
        borderRadius: '10px',
        border: '1px solid #CBD5E1',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden'
      }}>
        
        {/* CASE A: FULL VIDEO AVATAR */}
        {fallbackMode === 'video' && (
          <div 
            className={`avatar-breathing ${isSpeaking ? 'avatar-speaking' : ''}`}
            style={{ width: '160px', height: '200px', position: 'relative' }}
          >
            <svg viewBox="0 0 200 240" width="100%" height="100%" style={{ overflow: 'visible' }}>
              <defs>
                <radialGradient id="avatarGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#2563EB" stopOpacity="0.2" />
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

              {/* Ambient Teacher Glow */}
              <circle cx="100" cy="110" r="95" fill="url(#avatarGlow)" />

              {/* Blazer */}
              <path d="M 40 240 L 48 160 Q 100 175 152 160 L 160 240 Z" fill="url(#suitGrad)" stroke="#334155" strokeWidth="2" />
              
              {/* Shirt & Tie */}
              <polygon points="85,160 100,185 115,160 100,165" fill="#F8FAFC" />
              <polygon points="96,170 104,170 106,215 100,225 94,215" fill="url(#tieGrad)" />

              {/* Neck & Head */}
              <rect x="88" y="132" width="24" height="30" rx="4" fill="url(#skinGrad)" />
              <ellipse cx="100" cy="95" rx="46" ry="52" fill="url(#skinGrad)" stroke="#DDA87A" strokeWidth="1.5" />

              {/* Hair */}
              <path d="M 52 82 Q 100 35 148 82 Q 155 105 148 115 Q 142 80 100 70 Q 58 80 52 115 Z" fill="url(#hairGrad)" />

              {/* Eyebrows */}
              <path d="M 72 74 Q 82 70 90 74" stroke="#1E293B" strokeWidth="3" strokeLinecap="round" fill="none" />
              <path d="M 110 74 Q 118 70 128 74" stroke="#1E293B" strokeWidth="3" strokeLinecap="round" fill="none" />

              {/* Eyes with blinking logic */}
              {blinking ? (
                <>
                  <line x1="72" y1="88" x2="88" y2="88" stroke="#1E293B" strokeWidth="2.5" strokeLinecap="round" />
                  <line x1="112" y1="88" x2="128" y2="88" stroke="#1E293B" strokeWidth="2.5" strokeLinecap="round" />
                </>
              ) : (
                <>
                  <ellipse cx="80" cy="88" rx="7" ry="5" fill="#FFF" />
                  <circle cx="81" cy="88" r="3.5" fill="#1E3A8A" />
                  <circle cx="82" cy="87" r="1" fill="#FFF" />

                  <ellipse cx="120" cy="88" rx="7" ry="5" fill="#FFF" />
                  <circle cx="119" cy="88" r="3.5" fill="#1E3A8A" />
                  <circle cx="120" cy="87" r="1" fill="#FFF" />
                </>
              )}

              {/* Glasses */}
              <rect x="68" y="78" width="24" height="18" rx="4" fill="none" stroke="#2563EB" strokeWidth="2" />
              <rect x="108" y="78" width="24" height="18" rx="4" fill="none" stroke="#2563EB" strokeWidth="2" />
              <line x1="92" y1="85" x2="108" y2="85" stroke="#2563EB" strokeWidth="2" />

              {/* Nose */}
              <path d="M 98 94 L 102 104 L 96 106" stroke="#C88E63" strokeWidth="2" strokeLinecap="round" fill="none" />

              {/* Mouth with real-time lip-sync */}
              {mouthOpen ? (
                <path d="M 90 120 Q 100 134 110 120 Q 100 128 90 120 Z" fill="#991B1B" stroke="#7F1D1D" strokeWidth="1" />
              ) : (
                <path d="M 90 122 Q 100 128 110 122" stroke="#A16207" strokeWidth="2.5" strokeLinecap="round" fill="none" />
              )}
            </svg>
          </div>
        )}

        {/* CASE B: AUDIO + VISUAL FALLBACK MODE */}
        {fallbackMode === 'audio_visual' && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: '#EFF6FF', border: '2px solid #2563EB', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1D4ED8' }}>
              <Headphones size={28} />
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0F172A' }}>Audio + Visual Lesson Mode</div>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Avatar muted • Spoken audio narration active</span>
            </div>
          </div>
        )}

        {/* CASE C: TEXT + VISUAL FALLBACK MODE */}
        {fallbackMode === 'text_visual' && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: '#ECFDF5', border: '2px solid #059669', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#047857' }}>
              <FileText size={28} />
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0F172A' }}>Text + Visual Study Mode</div>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Audio & Avatar muted • Visuals prioritized</span>
            </div>
          </div>
        )}
      </div>

      {/* Closed Captions Subtitle Box - Placed below canvas so avatar face is never obscured */}
      {showCaptions && transcriptText && fallbackMode !== 'text_visual' && (
        <div style={{
          background: '#F1F5F9',
          border: '1px solid #CBD5E1',
          borderRadius: '8px',
          padding: '8px 12px',
          fontSize: '0.78rem',
          color: '#1E293B',
          textAlign: 'center',
          maxHeight: '48px',
          overflowY: 'auto',
          lineHeight: 1.35
        }}>
          {transcriptText}
        </div>
      )}

      {/* Media Player Controls Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '2px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Replay */}
          <button 
            type="button"
            onClick={onReplay}
            className="btn btn-secondary"
            style={{ padding: '6px 10px', fontSize: '0.78rem' }}
            title="Replay Spoken Explanation"
          >
            <RotateCcw size={14} />
          </button>

          {/* Mute/Unmute */}
          <button 
            type="button"
            onClick={onToggleMute}
            className="btn btn-secondary"
            style={{ padding: '6px 10px', fontSize: '0.78rem' }}
            title={isMuted ? "Unmute Voice" : "Mute Voice"}
          >
            {isMuted ? <VolumeX size={14} /> : <Volume2 size={14} color="#059669" />}
          </button>

          {/* Captions Toggle */}
          <button 
            type="button"
            onClick={() => setShowCaptions(!showCaptions)}
            className={`btn ${showCaptions ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 10px', fontSize: '0.78rem' }}
            title={showCaptions ? "Hide Captions" : "Show Captions"}
          >
            <Subtitles size={14} />
          </button>

          {/* Speed Selector */}
          <select 
            value={speed} 
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            style={{ 
              background: '#FFFFFF', 
              border: '1px solid #CBD5E1', 
              color: '#1E293B', 
              fontSize: '0.75rem', 
              fontWeight: 600,
              borderRadius: '6px', 
              padding: '4px 6px',
              cursor: 'pointer'
            }}
          >
            <option value={0.75}>0.75x</option>
            <option value={1.0}>1.0x</option>
            <option value={1.25}>1.25x</option>
            <option value={1.5}>1.5x</option>
          </select>
        </div>

        {/* Audio Visualizer Wave */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '3px', height: '18px' }}>
          {[35, 75, 95, 50, 85, 40, 70].map((h, i) => (
            <div 
              key={i}
              style={{
                width: '3px',
                height: isSpeaking ? `${h}%` : '4px',
                backgroundColor: isSpeaking ? '#2563EB' : '#CBD5E1',
                borderRadius: '2px',
                transition: 'height 0.15s ease'
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
