import React, { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';
import Header from './components/Header';
import HomeScreen from './components/HomeScreen';
import SetupFlow from './components/SetupFlow';
import LessonPreparing from './components/LessonPreparing';
import TeacherVideoPlayer from './components/TeacherVideoPlayer';
import VisualPanel from './components/VisualPanel';
import TeacherDialogue from './components/TeacherDialogue';
import StudentInteraction from './components/StudentInteraction';
import AdaptationHUD from './components/AdaptationHUD';
import AdaptationNotice from './components/AdaptationNotice';
import LessonProgress from './components/LessonProgress';
import AssessmentScreen from './components/AssessmentScreen';
import LearningReportScreen from './components/LearningReportScreen';
import SourceModal from './components/SourceModal';

import { 
  loadCanonicalDemo, 
  createSession, 
  advanceStep, 
  respondToQuestion, 
  getAssessment, 
  submitAssessment,
  requestAdaptation,
  saveSessionToStorage,
  loadSessionFromStorage,
  clearSessionFromStorage
} from './services/api';
import { speechService } from './services/tts';

export default function App() {
  // Screen state machine: 'home' | 'setup' | 'preparing' | 'teaching' | 'assessment' | 'report'
  const [currentScreen, setCurrentScreen] = useState('home');

  // Core pedagogical session state
  const [session, setSession] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [assessmentQuestions, setAssessmentQuestions] = useState([]);
  const [learningReport, setLearningReport] = useState(null);

  // Audio / Video stream state
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [fallbackMode, setFallbackMode] = useState('video'); // 'video' | 'audio_visual' | 'text_visual'

  // Diagnostic & adaptation states
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastEvaluation, setLastEvaluation] = useState(null);
  const [adaptationCount, setAdaptationCount] = useState(0);
  const [activeMisconception, setActiveMisconception] = useState(null);

  // Modals & transient notices
  const [isSourceModalOpen, setIsSourceModalOpen] = useState(false);
  const [languageNotice, setLanguageNotice] = useState(null);
  const [setupInitialMode, setSetupInitialMode] = useState('topic');

  // Subscribe to voice synthesizer for avatar lip-sync
  useEffect(() => {
    const unsubscribe = speechService.subscribe((speaking) => {
      setIsSpeaking(speaking);
    });
    return () => unsubscribe();
  }, []);

  // Speak explanation when current step changes
  useEffect(() => {
    if (currentScreen === 'teaching' && currentStep?.explanation && !isMuted && fallbackMode !== 'text_visual') {
      speechService.speak(currentStep.explanation, session?.learning_request?.preferred_language || currentStep.language || 'English');
    }
  }, [currentStep, isMuted, currentScreen, fallbackMode, session?.learning_request?.preferred_language]);

  // Load existing session from storage if present on first load
  useEffect(() => {
    const stored = loadSessionFromStorage();
    if (stored && stored.session && stored.current_step) {
      setSession(stored.session);
      setCurrentStep(stored.current_step);
      setCurrentScreen('teaching');
    }
  }, []);

  // Save active session to storage on updates
  useEffect(() => {
    if (session && currentStep && currentScreen === 'teaching') {
      saveSessionToStorage({ session, current_step: currentStep });
    }
  }, [session, currentStep, currentScreen]);

  // 1. Action: Launch Canonical Golden Demo (Ohm's Law)
  const handleLaunchCanonicalDemo = async () => {
    speechService.stop();
    setCurrentScreen('preparing');
    try {
      const data = await loadCanonicalDemo();
      setSession(data.session);
      setCurrentStep(data.current_step || data.session.steps[0]);
      setLastEvaluation(null);
      setActiveMisconception(null);
      setAdaptationCount(0);
      setLearningReport(null);
    } catch (err) {
      console.error("Failed to load canonical demo:", err);
    }
  };

  // 2. Action: Start custom lesson from Setup form
  const handleStartCustomLesson = async (params) => {
    speechService.stop();
    setCurrentScreen('preparing');
    try {
      const request = {
        student_id: "std_" + Math.random().toString(36).substring(2, 7),
        topic: params.topic,
        material_id: params.materialId,
        educational_level: params.level,
        existing_knowledge: params.existingKnowledge,
        learning_objective: params.goal,
        preferred_language: params.language,
        teaching_style: params.style,
        available_time: params.duration,
        desired_depth: params.depth
      };
      const res = await createSession(request);
      setSession(res.session);
      setCurrentStep(res.session.steps[0]);
      setLastEvaluation(null);
      setActiveMisconception(null);
      setAdaptationCount(0);
      setLearningReport(null);
    } catch (err) {
      alert("Error initializing lesson: " + err.message);
      setCurrentScreen('setup');
    }
  };

  // 3. Action: Complete preparation screen animation
  const handlePreparationComplete = () => {
    setCurrentScreen('teaching');
  };

  // 4. Action: Advance to next teaching step
  const handleAdvanceStep = async () => {
    if (!session) return;
    speechService.stop();
    try {
      const res = await advanceStep(session.session_id);
      if (res.session_status === 'assessment' || !res.next_step) {
        handleTriggerAssessment();
      } else {
        setCurrentStep(res.next_step);
      }
    } catch (err) {
      console.error("Failed to advance step:", err);
      handleTriggerAssessment();
    }
  };

  // 5. Action: Submit response to active question
  const handleSubmitAnswer = async (answer, answerType = 'text') => {
    if (!session || !currentStep) return;
    speechService.stop();
    setIsSubmitting(true);

    try {
      const qId = currentStep.question?.question_id || 'q_current';
      const res = await respondToQuestion(session.session_id, qId, answer, answerType);
      
      setLastEvaluation(res.evaluation);

      if (res.adaptation_occurred) {
        // Misconception detected -> AI Teacher adapts seamlessly
        setActiveMisconception(res.misconception_detected);
        setAdaptationCount(prev => prev + 1);
        setCurrentStep(res.next_step);
      } else {
        // Correct answer -> clear misconception and advance
        setActiveMisconception(null);
        if (res.session_status === 'assessment' || !res.next_step) {
          handleTriggerAssessment();
        } else {
          setCurrentStep(res.next_step);
        }
      }
    } catch (err) {
      alert("Evaluation error: " + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 6. Action: Start final assessment
  const handleTriggerAssessment = async () => {
    speechService.stop();
    setIsSubmitting(true);
    try {
      const res = await getAssessment(session?.session_id || 'sess_demo');
      setAssessmentQuestions(res.questions || []);
      setCurrentScreen('assessment');
    } catch (err) {
      console.error("Failed to fetch assessment:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 7. Action: Submit final assessment answers
  const handleSubmitAssessmentAnswers = async (answers) => {
    speechService.stop();
    setIsSubmitting(true);
    try {
      const reportRes = await submitAssessment(session?.session_id || 'sess_demo', answers);
      setLearningReport(reportRes.report);
      clearSessionFromStorage();
      setCurrentScreen('report');
    } catch (err) {
      console.error("Failed to compile assessment report:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 8. Action: Replay speech
  const handleReplaySpeech = () => {
    if (currentStep?.explanation && fallbackMode !== 'text_visual') {
      speechService.speak(currentStep.explanation, session?.learning_request?.preferred_language || currentStep.language || 'English');
    }
  };

  // 9. Action: Language switching on the fly (Section 27 & 28)
  const handleChangeLanguage = (newLang) => {
    if (!session) return;
    setSession(prev => ({
      ...prev,
      learning_request: {
        ...prev.learning_request,
        preferred_language: newLang
      }
    }));
    setLanguageNotice(`Continuing lesson in ${newLang}...`);
    setTimeout(() => setLanguageNotice(null), 3000);

    // Replay in new language voice if available
    if (currentStep?.explanation && !isMuted) {
      speechService.speak(currentStep.explanation, newLang);
    }
  };

  // 10. Action: In-Lesson Teacher Assistance ("Explain more simply" / "Give an example")
  const handleRequestSimplify = async () => {
    if (!session) return;
    try {
      const res = await requestAdaptation(session.session_id, 'simplify');
      if (res.adaptive_step) {
        setCurrentStep(res.adaptive_step);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleRequestExample = async () => {
    if (!session) return;
    try {
      const res = await requestAdaptation(session.session_id, 'example');
      if (res.adaptive_step) {
        setCurrentStep(res.adaptive_step);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const canAdvance = currentStep && currentStep.step_type !== 'question' && currentStep.step_type !== 're_explanation';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      
      {/* Top Application Navigation Header */}
      <Header 
        currentScreen={currentScreen}
        onGoHome={() => {
          speechService.stop();
          setCurrentScreen('home');
        }}
        onLoadCanonical={handleLaunchCanonicalDemo}
        onOpenSetup={() => {
          speechService.stop();
          setSetupInitialMode('topic');
          setCurrentScreen('setup');
        }}
        currentTopic={session?.lesson_plan?.topic || session?.learning_request?.topic}
        currentConcept={currentStep?.concept_id}
        language={session?.learning_request?.preferred_language || 'Hinglish'}
        onChangeLanguage={handleChangeLanguage}
      />

      {/* Language Change Toast Notification */}
      {languageNotice && (
        <div style={{
          position: 'fixed',
          top: '80px',
          right: '30px',
          zIndex: 1000,
          background: 'rgba(6, 182, 212, 0.9)',
          color: '#FFF',
          padding: '8px 16px',
          borderRadius: '8px',
          fontSize: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          boxShadow: 'var(--shadow-md)'
        }}>
          <Globe size={14} />
          <span>{languageNotice}</span>
        </div>
      )}

      {/* VIEW 1: HOME SCREEN */}
      {currentScreen === 'home' && (
        <HomeScreen 
          onStartLearning={() => {
            setSetupInitialMode('topic');
            setCurrentScreen('setup');
          }}
          onLaunchCanonicalDemo={handleLaunchCanonicalDemo}
          onOpenUpload={() => {
            setSetupInitialMode('upload');
            setCurrentScreen('setup');
          }}
          onChooseTopic={() => {
            setSetupInitialMode('topic');
            setCurrentScreen('setup');
          }}
        />
      )}

      {/* VIEW 2: SETUP & PERSONALIZATION SCREEN */}
      {currentScreen === 'setup' && (
        <SetupFlow 
          initialMode={setupInitialMode}
          onStartLesson={handleStartCustomLesson}
          onCancel={() => setCurrentScreen('home')}
        />
      )}

      {/* VIEW 3: LESSON PREPARATION SCREEN */}
      {currentScreen === 'preparing' && (
        <LessonPreparing 
          topic={session?.lesson_plan?.topic || "Ohm's Law & Circuit Dynamics"}
          language={session?.learning_request?.preferred_language || "Hinglish"}
          level={session?.learning_request?.educational_level || "beginner"}
          onPreparationComplete={handlePreparationComplete}
        />
      )}

      {/* VIEW 4: TEACHING WORKSPACE */}
      {currentScreen === 'teaching' && (
        <main style={{ 
          flex: 1, 
          padding: '0 24px 24px', 
          display: 'grid', 
          gridTemplateColumns: '320px 1fr', 
          gap: '20px',
          alignItems: 'start'
        }}>
          
          {/* Left Column: Video Player, Pedagogical HUD, Curriculum Progress (Sticky with dedicated scrollbar) */}
          <aside 
            className="teaching-sidebar-left"
            style={{ 
              position: 'sticky', 
              top: '84px', 
              maxHeight: 'calc(100vh - 104px)', 
              overflowY: 'auto', 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '16px',
              paddingRight: '6px'
            }}
          >
            <TeacherVideoPlayer 
              isSpeaking={isSpeaking}
              emotion={currentStep?.avatar_emotion || 'explaining'}
              isMuted={isMuted}
              onToggleMute={() => setIsMuted(!isMuted)}
              onReplay={handleReplaySpeech}
              transcriptText={currentStep?.explanation || ''}
              language={session?.learning_request?.preferred_language || 'English'}
              fallbackMode={fallbackMode}
              onChangeFallbackMode={setFallbackMode}
            />

            <AdaptationHUD 
              lastEvaluation={lastEvaluation}
              activeMisconception={activeMisconception}
              adaptationCount={adaptationCount}
            />

            <LessonProgress 
              lessonPlan={session?.lesson_plan}
              currentStepIndex={session?.current_step_index ?? 0}
              totalSteps={session?.steps?.length ?? 3}
              onTriggerAssessment={handleTriggerAssessment}
              status={session?.status}
              currentConcept={currentStep?.concept_id}
            />
          </aside>

          {/* Right Column: Dynamic Visual Board, Dialogue, Adaptation Notice, Question Interaction */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            
            {/* Visual Teaching Panel (Circuits, Math, Graphs, Code, Concept Maps) */}
            <VisualPanel 
              visualInstruction={currentStep?.visual_instruction}
            />

            {/* Encouraging Adaptation Banner if Misconception Detected */}
            {activeMisconception && (
              <AdaptationNotice 
                misconception={activeMisconception}
                teacherThought={lastEvaluation?.teacher_thought}
                onDismiss={() => setActiveMisconception(null)}
              />
            )}

            {/* Teacher Dialogue & Spoken Captions */}
            <TeacherDialogue 
              step={currentStep}
              onAdvance={handleAdvanceStep}
              onReplaySpeech={handleReplaySpeech}
              isSpeaking={isSpeaking}
              canAdvance={canAdvance}
              onRequestSimplify={handleRequestSimplify}
              onRequestExample={handleRequestExample}
              onOpenSource={() => setIsSourceModalOpen(true)}
            />

            {/* Interactive Question & Student Response Zone */}
            <StudentInteraction 
              question={currentStep?.question}
              onSubmitAnswer={handleSubmitAnswer}
              isSubmitting={isSubmitting}
            />
          </div>
        </main>
      )}

      {/* VIEW 5: INTERACTIVE ASSESSMENT SCREEN */}
      {currentScreen === 'assessment' && (
        <AssessmentScreen 
          questions={assessmentQuestions}
          onSubmitAssessment={handleSubmitAssessmentAnswers}
          isSubmitting={isSubmitting}
        />
      )}

      {/* VIEW 6: COMPREHENSIVE LEARNING REPORT SCREEN */}
      {currentScreen === 'report' && (
        <LearningReportScreen 
          report={learningReport}
          onStartNextTopic={(nextTopic) => {
            handleStartCustomLesson({
              topic: nextTopic,
              level: session?.learning_request?.educational_level || "beginner",
              language: session?.learning_request?.preferred_language || "Hinglish",
              duration: 20,
              style: "analogy_driven"
            });
          }}
          onReturnHome={() => setCurrentScreen('home')}
        />
      )}

      {/* RAG Source Citation Modal */}
      <SourceModal 
        isOpen={isSourceModalOpen}
        onClose={() => setIsSourceModalOpen(false)}
        sourceReferences={currentStep?.source_references || []}
      />
    </div>
  );
}
