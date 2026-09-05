/**
 * Text-to-Speech & Speech-to-Text Service
 * Connects browser speech synthesis to the Teacher Avatar for lip-sync and voice narration.
 */

class SpeechService {
  constructor() {
    this.synth = typeof window !== 'undefined' ? window.speechSynthesis : null;
    this.currentUtterance = null;
    this.isSpeaking = false;
    this.listeners = new Set();
  }

  speak(text, language = 'English', onEnd = null, onBoundary = null) {
    if (!this.synth) {
      if (onEnd) onEnd();
      return;
    }

    this.stop();

    const utterance = new SpeechSynthesisUtterance(text);
    this.currentUtterance = utterance;

    // Pick suitable voice
    const voices = this.synth.getVoices();
    const langCode = language.toLowerCase() === 'hindi' ? 'hi' : 'en';
    
    // Attempt to match language or regional voice (e.g. Indian English / Hindi)
    const matchedVoice = voices.find(v => 
      v.lang.toLowerCase().includes(langCode) || 
      (langCode === 'en' && v.lang.toLowerCase().includes('en-in'))
    ) || voices[0];

    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.rate = 1.0;
    utterance.pitch = 1.05;

    utterance.onstart = () => {
      this.isSpeaking = true;
      this._notify(true);
    };

    utterance.onboundary = (event) => {
      if (onBoundary) onBoundary(event);
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.currentUtterance = null;
      this._notify(false);
      if (onEnd) onEnd();
    };

    utterance.onerror = (e) => {
      console.warn('SpeechSynthesis error:', e);
      this.isSpeaking = false;
      this.currentUtterance = null;
      this._notify(false);
      if (onEnd) onEnd();
    };

    this.synth.speak(utterance);
  }

  stop() {
    if (this.synth && this.synth.speaking) {
      this.synth.cancel();
    }
    this.isSpeaking = false;
    this._notify(false);
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  _notify(speakingState) {
    this.listeners.forEach(cb => cb(speakingState));
  }

  startSpeechRecognition(onResult, onEnd, onError) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      if (onError) onError('Speech recognition is not supported in this browser.');
      return null;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (onResult) onResult(transcript);
    };

    recognition.onerror = (event) => {
      console.warn('SpeechRecognition error:', event.error);
      if (onError) onError(event.error);
    };

    recognition.onend = () => {
      if (onEnd) onEnd();
    };

    recognition.start();
    return recognition;
  }
}

export const speechService = new SpeechService();
