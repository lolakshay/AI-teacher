# Complete REST API Reference Specification

**Project:** AI Teacher: Build a Human-Like AI Educator That Teaches Through Video  
**Base URL:** `http://127.0.0.1:8000/api`  
**OpenAPI Specification:** Interactive Swagger UI available at `http://127.0.0.1:8000/docs`

---

## 1. System Health & Diagnostics

### `GET /health` / `GET /api/health`
Returns runtime status for all internal subsystems without leaking credentials.

**Response `200 OK`:**
```json
{
  "status": "ok",
  "service": "AI Teacher - Human-Like Adaptive AI Educator",
  "version": "1.0.0",
  "environment": "development",
  "demo_mode": true,
  "subsystems": {
    "orchestrator": "active",
    "rag": "ready",
    "personalization_db": "connected",
    "evaluation_engine": "active",
    "adaptation_engine": "active",
    "assessment_engine": "active",
    "llm_provider": "deterministic_mock_ready",
    "voice_provider": "web_speech_api",
    "avatar_provider": "svg_animated"
  }
}
```

---

## 2. Teaching & Session Management (Agent 1 & 10)

### `POST /api/sessions/create` or `POST /api/teaching/start`
Initializes a new teaching session, executes curriculum planning, and synthesizes initial teaching steps.

**Request Body:**
```json
{
  "student_id": "demo_student_01",
  "topic": "Ohm's Law & Circuit Dynamics",
  "material_id": null,
  "educational_level": "beginner",
  "learning_objective": "Understand and apply Ohm's law",
  "preferred_language": "Hinglish",
  "teaching_style": "analogy_driven",
  "available_time": 20,
  "desired_depth": "intuitive"
}
```

**Response `200 OK`:**
```json
{
  "status": "success",
  "session": {
    "session_id": "7a8b9c0d",
    "current_step_index": 0,
    "status": "teaching",
    "steps": [
      {
        "step_id": "step_01",
        "step_type": "introduction",
        "explanation": "Namaste! Main aapka AI Teacher hoon...",
        "visual_instruction": {
          "type": "circuit",
          "title": "Interactive DC Circuit: Ohm's Law in Action",
          "data": { "voltage": 12.0, "resistance": 4.0, "current": 3.0 }
        },
        "avatar_emotion": "explaining"
      }
    ]
  }
}
```

---

### `GET /api/sessions/{session_id}/step`
Retrieves the currently active teaching step.

---

### `POST /api/sessions/{session_id}/advance` or `GET /api/teaching/{session_id}/next`
Advances the lesson to the next pedagogical step, or transitions to assessment when finished.

**Response `200 OK`:**
```json
{
  "status": "success",
  "next_step": {
    "step_id": "step_02",
    "step_type": "demonstration",
    "explanation": "Ab aate hain teesre main player par: Resistance (R)..."
  },
  "session_status": "teaching"
}
```

---

### `POST /api/sessions/{session_id}/respond` or `POST /api/teaching/{session_id}/respond`
Submits a student answer to a diagnostic probe. Evaluates reasoning and injects adaptive reteaching if a misconception is found.

**Request Body:**
```json
{
  "question_id": "ohm_q1_proportionality",
  "student_answer": "Current increase hoga.",
  "answer_type": "text"
}
```

**Response `200 OK` (Adaptive Intervention Triggered):**
```json
{
  "status": "success",
  "adaptation_occurred": true,
  "misconception_detected": "Inverted Proportionality / Direct Proportionality Fallacy",
  "evaluation": {
    "correctness": false,
    "confidence": 0.98,
    "recommended_action": "give_analogy",
    "teacher_thought": "Student exhibits classic Inverse Proportionality confusion. Deploying Water-Pipe constriction analogy.",
    "bloom_level": "Applying"
  },
  "next_step": {
    "step_id": "adapt_4f2b1a",
    "step_type": "re_explanation",
    "explanation": "Koi baat nahi, ye ek bohot hi common misunderstanding hai! Chaliye paani ke pipe se samajhte hain...",
    "visual_instruction": {
      "type": "circuit",
      "data": { "voltage": 12.0, "resistance": 12.0, "current": 1.0 }
    },
    "question": {
      "question_id": "followup_9a1b2c",
      "prompt": "Agar Resistance 4Ω se badha kar 12Ω kar dein, to Current 5A hoga ya ghat kar 1A ho jayega?",
      "question_type": "follow_up"
    },
    "avatar_emotion": "encouraging"
  }
}
```

---

### `POST /api/sessions/{session_id}/language`
Dynamically switches language mid-session while strictly preserving lesson position and learner mastery.

**Request Body:**
```json
{ "language": "Hinglish" }
```

---

## 3. Document Intelligence & RAG (Agent 2)

### `POST /api/materials/upload`
Uploads educational document (PDF, DOCX, TXT) and executes chunking and indexing.

**Multipart Form:** `file`: `<binary>`

**Response `200 OK`:**
```json
{
  "status": "success",
  "data": {
    "doc_id": "doc_3a9f1b",
    "filename": "NCERT_Class10_Electricity.pdf",
    "page_count": 14,
    "chunk_count": 28
  }
}
```

### `GET /api/materials/{doc_id}`
Returns metadata and status for an ingested document.

---

## 4. Multi-Modal Media Synthesis (Agents 4 & 5)

### `POST /api/video/generate`
Composes avatar, voice audio, and interactive whiteboard into a video scene.

### `POST /api/voice/generate`
Synthesizes speech audio waveform for lesson explanation.

### `POST /api/avatar/generate`
Generates avatar emotional posture and lip-sync phoneme mapping.

---

## 5. Assessment & Analytics (Agent 7)

### `GET /api/sessions/{session_id}/assessment`
Generates summative mastery assessment questions for the lesson topic.

### `POST /api/sessions/{session_id}/assessment/submit`
Evaluates assessment answers, updates learner state in SQLite, and generates a comprehensive learning report.

**Response `200 OK`:**
```json
{
  "status": "success",
  "report": {
    "lesson_id": "les_01",
    "score": 92.0,
    "concepts_understood": [
      "Physical intuition of Ohm's Law",
      "Governing proportionalities",
      "Circuit calculation"
    ],
    "weak_areas": [
      "Initial inverse proportionality intuition (overcome via hydraulic analogy)"
    ],
    "misconceptions": [
      "Inverted Proportionality Fallacy"
    ],
    "concepts_requiring_revision": [
      "Practice rearranging reciprocal equations (I = V/R)"
    ],
    "recommended_next_topic": "Kirchhoff's Laws & Series-Parallel Resistor Networks"
  }
}
```

---

## 6. Canonical 1-Click Hackathon Demo

### `GET /api/demo/canonical`
Instantly loads the pre-configured Ohm's Law canonical demo with beginner level, Hinglish language, and intentional misconception trigger.
