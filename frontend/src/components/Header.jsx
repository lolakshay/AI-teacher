import React from 'react';
import { 
  GraduationCap, 
  Play, 
  BookOpen, 
  Globe, 
  Home, 
  Layers
} from 'lucide-react';

export default function Header({ 
  currentScreen, 
  onGoHome, 
  onLoadCanonical, 
  onOpenSetup, 
  currentTopic, 
  currentConcept,
  language,
  onChangeLanguage 
}) {
  return (
    <header className="glass-panel" style={{ 
      margin: '16px 24px', 
      padding: '12px 24px', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between', 
      zIndex: 50,
      flexWrap: 'wrap',
      gap: '12px'
    }}>
      
      {/* Brand & Current Topic Orientation */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <button 
          onClick={onGoHome}
          style={{ 
            background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)', 
            border: 'none', 
            width: '40px', 
            height: '40px', 
            borderRadius: '10px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            cursor: 'pointer',
            boxShadow: '0 2px 8px rgba(37, 99, 235, 0.35)'
          }}
          title="Return to Home"
        >
          <GraduationCap size={22} color="#FFF" />
        </button>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span 
              onClick={onGoHome}
              style={{ 
                fontSize: '1.25rem', 
                fontWeight: 800, 
                letterSpacing: '-0.02em', 
                color: '#0F172A',
                cursor: 'pointer'
              }}
            >
              AI Teacher
            </span>
          </div>
          
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>{currentTopic || 'Interactive Video Learning'}</span>
            {currentConcept && (
              <>
                <span>•</span>
                <span style={{ color: '#2563EB', fontWeight: 600 }}>Focus: {currentConcept}</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Right Controls: Language Selector, Demo Lesson, Setup */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        
        {/* Language Selector Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#F1F5F9', padding: '5px 10px', borderRadius: '8px', border: '1px solid #CBD5E1' }}>
          <Globe size={14} color="#0284C7" />
          <select 
            id="select-language"
            value={language || 'Hinglish'}
            onChange={(e) => onChangeLanguage && onChangeLanguage(e.target.value)}
            style={{ 
              background: 'transparent', 
              border: 'none', 
              color: '#0F172A', 
              fontSize: '0.82rem', 
              fontWeight: 600,
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            <option value="Hinglish" style={{ background: '#FFFFFF', color: '#0F172A' }}>Hinglish (हिंग्लिश)</option>
            <option value="English" style={{ background: '#FFFFFF', color: '#0F172A' }}>English</option>
            <option value="Hindi" style={{ background: '#FFFFFF', color: '#0F172A' }}>Hindi (हिंदी)</option>
          </select>
        </div>

        {/* Canonical Demo Lesson Button */}
        <button 
          id="btn-header-canonical"
          className="btn btn-amber"
          onClick={onLoadCanonical}
          style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          title="Load guided Ohm's Law demonstration"
        >
          <Play size={14} fill="currentColor" />
          <span>Demo Lesson</span>
        </button>

        {/* New Lesson / Topic Button */}
        <button 
          id="btn-header-new-lesson"
          className="btn btn-secondary"
          onClick={onOpenSetup}
          style={{ padding: '8px 14px', fontSize: '0.82rem' }}
        >
          <BookOpen size={14} />
          <span>New Lesson</span>
        </button>
      </div>

    </header>
  );
}
