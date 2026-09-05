/**
 * Centralized API Service for AI Teacher
 * Implements full backend integration with automatic offline fallback.
 * Strictly adheres to shared backend contracts.
 */

import {
  CANONICAL_DEMO_DATA,
  MOCK_ADAPTIVE_STEP,
  MOCK_EVALUATION_INCORRECT,
  MOCK_EVALUATION_CORRECT,
  MOCK_ASSESSMENT_QUESTIONS,
  MOCK_LEARNING_REPORT
} from '../data/mockData.js';

const API_BASE = typeof window !== 'undefined' ? '/api' : 'http://127.0.0.1:8000/api';
const STORAGE_KEY = 'ai_teacher_active_session';

// Helper for session storage
export function saveSessionToStorage(sessionData) {
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessionData));
    }
  } catch (e) {
    console.warn('Failed to save session to localStorage:', e);
  }
}

export function loadSessionFromStorage() {
  try {
    if (typeof localStorage !== 'undefined') {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    }
    return null;
  } catch (e) {
    console.warn('Failed to parse session from localStorage:', e);
    return null;
  }
}

export function clearSessionFromStorage() {
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY);
    }
  } catch (e) {
    console.warn('Failed to clear session from localStorage:', e);
  }
}

/**
 * 1-Click Golden Demo Loader
 */
export async function loadCanonicalDemo() {
  try {
    const res = await fetch(`${API_BASE}/demo/canonical`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data;
  } catch (err) {
    console.info('[AI Teacher] Backend unreachable or demo endpoint returned error. Using robust offline canonical demo data.', err);
    return JSON.parse(JSON.stringify(CANONICAL_DEMO_DATA));
  }
}

/**
 * Initialize / Create Teaching Session
 */
export async function createSession(request, profile = null) {
  try {
    const res = await fetch(`${API_BASE}/sessions/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ request, profile })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[AI Teacher] Falling back to client-synthesized session:', err);
    // Construct valid client-side SessionState
    const isOhm = (request.topic || '').toLowerCase().includes('ohm') || (request.topic || '').toLowerCase().includes('circuit');
    const base = isOhm ? JSON.parse(JSON.stringify(CANONICAL_DEMO_DATA)) : null;

    if (base) {
      base.session.learning_request.preferred_language = request.preferred_language || 'Hinglish';
      base.session.learning_request.educational_level = request.educational_level || 'beginner';
      base.session.learning_request.teaching_style = request.teaching_style || 'analogy_driven';
      base.session.session_id = 'sess_' + Math.random().toString(36).substring(2, 9);
      return { status: 'success', session: base.session };
    }

    // Generic dynamic topic lesson plan
    const topic = request.topic || "Physics Fundamentals";
    const customSession = {
      session_id: 'sess_' + Math.random().toString(36).substring(2, 9),
      status: "teaching",
      current_step_index: 0,
      current_concept: topic,
      learning_request: request,
      lesson_plan: {
        lesson_id: 'plan_' + Math.random().toString(36).substring(2, 7),
        topic: topic,
        learning_objectives: [`Understand the core principles of ${topic}`, `Apply key relationships in ${topic}`],
        ordered_concepts: [`Introduction to ${topic}`, `Deep Principles & Mechanisms`, `Practical Assessment`],
        estimated_duration: request.available_time || 20
      },
      steps: [
        {
          step_id: "step_custom_1",
          lesson_id: "plan_custom",
          concept_id: topic,
          step_type: "introduction",
          objective: `Foundational overview of ${topic}`,
          explanation: `Welcome to this focused lesson on ${topic}. We will explore how its foundational principles connect and apply them step by step.`,
          language: request.preferred_language || "English",
          difficulty: request.educational_level || "beginner",
          avatar_emotion: "explaining",
          visual_instruction: {
            type: "concept_map",
            title: `${topic}: Conceptual Architecture`,
            caption: `Key principles and relationship map for ${topic}`,
            data: {
              concepts: [`Foundations of ${topic}`, `Core Governing Formula`, `Applied Systems`],
              active_concept: `Foundations of ${topic}`,
              dependencies: {}
            }
          }
        },
        {
          step_id: "step_custom_2",
          lesson_id: "plan_custom",
          concept_id: topic,
          step_type: "question",
          objective: `Formative check on ${topic}`,
          explanation: `Let us verify how you connect the core principle. Consider the question below.`,
          language: request.preferred_language || "English",
          difficulty: request.educational_level || "beginner",
          avatar_emotion: "attentive",
          question: {
            question_id: "q_custom_1",
            prompt: `In ${topic}, what happens to system equilibrium when key parameters are doubled?`,
            options: [
              "System adjusts inversely to maintain conservation",
              "System amplifies without bound",
              "System experiences immediate decay",
              "No observable change occurs"
            ],
            hints: ["Think about conservation laws and reciprocal relationships."],
            question_type: "conceptual_check"
          },
          visual_instruction: {
            type: "math_derivation",
            title: `Derivation Model: ${topic}`,
            caption: "Mathematical representation of the governing equation",
            data: {
              steps: [
                { latex: "F_{net} = \\sum_{i=1}^n f_i", explanation: "Equilibrium condition across boundaries" },
                { latex: "\\Delta S \\ge 0", explanation: "Thermodynamic / governing directionality" }
              ],
              active_step: 0
            }
          }
        }
      ]
    };
    return { status: 'success', session: customSession };
  }
}

export async function getSession(sessionId) {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[AI Teacher] getSession fallback to stored session:', err);
    const stored = loadSessionFromStorage();
    return { status: 'success', session: stored?.session || CANONICAL_DEMO_DATA.session };
  }
}

export async function getCurrentStep(sessionId) {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/step`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { status: 'success', step: CANONICAL_DEMO_DATA.current_step };
  }
}

export async function advanceStep(sessionId) {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/advance`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.info('[AI Teacher] advanceStep fallback triggered.');
    const stored = loadSessionFromStorage();
    if (stored && stored.session) {
      stored.session.current_step_index = (stored.session.current_step_index || 0) + 1;
      const nextStep = stored.session.steps[stored.session.current_step_index];
      if (nextStep) {
        saveSessionToStorage(stored);
        return {
          status: 'success',
          next_step: nextStep,
          session_status: nextStep.step_type === 'question' ? 'questioning' : 'teaching'
        };
      }
      return { status: 'success', next_step: null, session_status: 'assessment' };
    }
    return { status: 'success', next_step: null, session_status: 'assessment' };
  }
}

export async function respondToQuestion(sessionId, questionId, studentAnswer, answerType = 'text') {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_id: questionId,
        student_answer: studentAnswer,
        answer_type: answerType
      })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.info('[AI Teacher] respondToQuestion fallback simulation.', err);
    // Check if the answer triggers the canonical misconception
    const lower = studentAnswer.toLowerCase();
    const isMisconception = lower.includes('increase') && !lower.includes('decrease');

    if (isMisconception) {
      return {
        status: 'success',
        evaluation: MOCK_EVALUATION_INCORRECT,
        next_step: MOCK_ADAPTIVE_STEP,
        session_status: 'adapting',
        adaptation_occurred: true,
        misconception_detected: MOCK_EVALUATION_INCORRECT.misconception
      };
    } else {
      return {
        status: 'success',
        evaluation: MOCK_EVALUATION_CORRECT,
        next_step: null,
        session_status: 'assessment',
        adaptation_occurred: false,
        misconception_detected: null
      };
    }
  }
}

export async function getAssessment(sessionId) {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/assessment`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.info('[AI Teacher] getAssessment fallback to mock assessment questions.');
    return {
      status: 'success',
      questions: MOCK_ASSESSMENT_QUESTIONS
    };
  }
}

export async function submitAssessment(sessionId, answers) {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/assessment/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(answers || {})
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.info('[AI Teacher] submitAssessment fallback to mock learning report.');
    return {
      status: 'success',
      report: MOCK_LEARNING_REPORT
    };
  }
}

export async function uploadMaterial(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/materials/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.info('[AI Teacher] uploadMaterial simulated success:', file.name);
    // Simulate realistic ingestion result
    return {
      status: 'success',
      data: {
        doc_id: 'doc_' + Math.random().toString(36).substring(2, 8),
        filename: file.name,
        chunk_count: Math.floor(Math.random() * 20) + 12,
        preview: "Textbook excerpt covering Voltage, Current, Resistance, and Ohm's Law principles with circuit diagrams."
      }
    };
  }
}

export async function requestAdaptation(sessionId, type = 'simplify') {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/adapt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ adaptation_type: type })
    });
    if (res.ok) return await res.json();
  } catch (err) {
    // Graceful fallback
  }

  // Client-side adaptation step
  return {
    status: 'success',
    adaptive_step: {
      ...MOCK_ADAPTIVE_STEP,
      objective: type === 'simplify' ? "Simplified breakdown with intuitive everyday analogies" : "Concrete worked numerical example",
      explanation: type === 'simplify'
        ? "Let's simplify this: Think of Voltage as people pushing a cart, and Resistance as rough uphill ground. If the ground gets rougher (more resistance), the cart slows down (less current)!"
        : "Let's work through a practical example: Suppose you have a 9-Volt battery powering a toy bulb with a resistance of 3 Ohms. Current I = 9 / 3 = 3 Amps."
    }
  };
}
