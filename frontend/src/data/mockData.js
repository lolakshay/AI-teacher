/**
 * Comprehensive Mock Data for AI Teacher Frontend & Standalone Demo Mode
 * Matches the shared backend contracts:
 * - SessionState
 * - TeachingStep
 * - VisualInstruction
 * - QuestionPayload
 * - EvaluationResult
 * - LearningReport
 */

export const CANONICAL_DEMO_DATA = {
  session: {
    session_id: "demo_canonical_01",
    status: "teaching",
    current_step_index: 0,
    current_concept: "Electric Potential (Voltage) & Charge Flow (Current)",
    learning_request: {
      request_id: "req_demo_01",
      student_id: "demo_student_01",
      topic: "Ohm's Law & Circuit Dynamics",
      educational_level: "beginner",
      existing_knowledge: "None",
      learning_objective: "Understand foundational circuit principles and master V=I*R",
      preferred_language: "Hinglish",
      teaching_style: "analogy_driven",
      available_time: 20,
      desired_depth: "intuitive"
    },
    student_profile: {
      student_id: "demo_student_01",
      educational_level: "beginner",
      known_topics: ["Basic Electric Charge", "Simple Algebra"],
      weak_topics: [],
      strong_topics: [],
      learning_objectives: ["Understand foundational circuit principles and master V=I*R"],
      preferred_language: "Hinglish",
      preferred_teaching_style: "analogy_driven",
      preferred_depth: "intuitive",
      current_learning_path: ["Electric Potential", "Resistance", "Ohm's Law", "Circuit Calculations"]
    },
    lesson_plan: {
      lesson_id: "plan_ohm_01",
      topic: "Ohm's Law & Circuit Dynamics",
      learning_objectives: [
        "Master the governing relationship V = I * R",
        "Understand direct and inverse proportionalities in electric circuits",
        "Apply Ohm's Law to practical numerical problems"
      ],
      prerequisites: ["Concept of electrical charge", "Basic fractions"],
      ordered_concepts: [
        "Voltage & Current Intuition",
        "Resistance & Opposition to Flow",
        "The Governing Formula: V = I * R",
        "Circuit Parameter Calculation",
        "Practical Circuit Applications"
      ],
      estimated_duration: 20,
      explanation_strategy: "Step-by-step conceptual grounding with visual demonstration and interactive check"
    },
    steps: [
      {
        step_id: "ohm_step_1",
        lesson_id: "plan_ohm_01",
        concept_id: "Voltage & Current Intuition",
        step_type: "introduction",
        objective: "Build physical intuition for Voltage (pressure) and Current (flow rate)",
        explanation: "Namaste! Welcome to our lesson on Ohm's Law. Electricity ko samajhne ke liye, imagine kijiye ek water pipe system. Voltage wo 'pressure' ya force hai jo electrons ko aage dhakelta hai, aur Current wo flow rate hai jo actually flow ho raha hai.",
        example: "Jaise pani ki tanki ki height badhane se pipe mein pani ka pressure badhta hai, waise hi battery ka Voltage electrons ko push karta hai.",
        language: "Hinglish",
        difficulty: "beginner",
        avatar_emotion: "explaining",
        visual_instruction: {
          type: "circuit",
          title: "Interactive DC Circuit: Voltage & Electron Push",
          caption: "Observe how voltage creates potential difference and pushes charge",
          data: {
            voltage: 12.0,
            resistance: 4.0,
            current: 3.0,
            formula: "I = V / R",
            highlight: "voltage",
            electron_speed: 4.5,
            analogy: "Water Pipe: Voltage is the pump pressure pushing water through the circuit."
          }
        },
        source_references: [
          { document: "NCERT Physics Class 10", chapter: "Electricity", section: "12.2 Electric Potential and Potential Difference", page: 201 }
        ]
      },
      {
        step_id: "ohm_step_2",
        lesson_id: "plan_ohm_01",
        concept_id: "The Governing Formula: V = I * R",
        step_type: "demonstration",
        objective: "Derive the mathematical relationship V = I * R and explain each variable",
        explanation: "Ab dekhte hain Resistance kya hai. Resistance flow ke raaste mein rukaawat hai. Georg Simon Ohm ne discover kiya ki agar Voltage constant ho, toh Resistance badhane se Current kam ho jata hai! Formula hai: V = I * R, yaani I = V / R.",
        example: "Agar Voltage 12 Volts hai aur Resistance 4 Ohms hai, toh Current hoga: 12 / 4 = 3 Amperes.",
        language: "Hinglish",
        difficulty: "beginner",
        avatar_emotion: "thoughtful",
        visual_instruction: {
          type: "math_derivation",
          title: "Mathematical Derivation & Formula Relationships",
          caption: "Step-by-step algebraic breakdown of Ohm's Law",
          data: {
            steps: [
              { latex: "V = I \\cdot R", explanation: "Standard form: Voltage equals Current multiplied by Resistance" },
              { latex: "I = \\frac{V}{R}", explanation: "Rearranging for Current: Current is inversely proportional to Resistance" },
              { latex: "R = \\frac{V}{I}", explanation: "Rearranging for Resistance: Resistance equals Voltage divided by Current" }
            ],
            active_step: 1
          }
        },
        source_references: [
          { document: "NCERT Physics Class 10", chapter: "Electricity", section: "12.3 Ohm's Law", page: 204 }
        ]
      },
      {
        step_id: "ohm_step_3",
        lesson_id: "plan_ohm_01",
        concept_id: "Circuit Parameter Calculation",
        step_type: "question",
        objective: "Formative check: Verify understanding of the inverse relationship between resistance and current",
        explanation: "Chaliye ek quick concept check karte hain! Neeche diye gaye question ko dhyan se padhiye aur apna answer submit kijiye.",
        language: "Hinglish",
        difficulty: "beginner",
        avatar_emotion: "attentive",
        question: {
          question_id: "ohm_q1",
          prompt: "If voltage remains constant across a circuit and resistance increases, what happens to current?",
          expected_answer: "Current decreases because resistance opposes the flow of electric charge (I = V/R).",
          options: [
            "Current increases",
            "Current decreases",
            "Current remains unchanged",
            "Current fluctuates randomly"
          ],
          hints: [
            "Formula I = V / R ko yaad kijiye. Agar denominator (R) badhega, toh fraction ki value kya hogi?",
            "Water pipe analogy: Agar pipe ko patla kar dein (zyada resistance), toh pani ka flow kam hoga ya zyada?"
          ],
          question_type: "conceptual_check",
          pedagogical_goal: "Verify inverse proportionality comprehension before advancing to multi-resistor circuits."
        },
        visual_instruction: {
          type: "circuit",
          title: "Circuit Probe: Variable Resistance in Action",
          caption: "Adjust the slider above or think conceptually about increasing R",
          data: {
            voltage: 12.0,
            resistance: 4.0,
            current: 3.0,
            formula: "I = V / R",
            highlight: "resistance",
            electron_speed: 4.5
          }
        }
      }
    ]
  },
  current_step: null
};

CANONICAL_DEMO_DATA.current_step = CANONICAL_DEMO_DATA.session.steps[0];

export const MOCK_ADAPTIVE_STEP = {
  step_id: "ohm_adaptive_step_1",
  lesson_id: "plan_ohm_01",
  concept_id: "Inverse Relationship: Current vs Resistance",
  step_type: "re_explanation",
  objective: "Targeted remediation of inverse proportionality misconception using hydraulic water-pipe analogy",
  explanation: "Let's look at this another way. Aapne socha ki Current badhega, lekin actually Resistance ek 'rukaawat' ya speed-breaker jaisa hai. Imagine kijiye ek water pipe system jisme aap ek valve ko tight kar rahe hain. Jab rukaawat (resistance) badhegi, toh pani ka flow (current) kam ho jayega, badhega nahi!",
  example: "Mathematical proof: 12V / 4Ω = 3A. Agar resistance badhakar 12Ω kar dein, toh 12V / 12Ω = 1A. Yaani current 3A se girkar 1A ho gaya!",
  language: "Hinglish",
  difficulty: "beginner",
  avatar_emotion: "encouraging",
  visual_instruction: {
    type: "circuit",
    title: "Adaptive View: High Resistance = Reduced Current",
    caption: "Notice the electron speed slowed down as Resistance increased from 4Ω to 12Ω",
    data: {
      voltage: 12.0,
      resistance: 12.0,
      current: 1.0,
      formula: "I = 12V / 12Ω = 1.0A",
      highlight: "resistance",
      electron_speed: 1.2,
      analogy: "Water Pipe Constriction: High resistance restricts electron flow rate."
    }
  },
  question: {
    question_id: "ohm_followup_q1",
    prompt: "Now with this water-pipe analogy in mind: If we increase resistance even more, will current flow faster or slower?",
    expected_answer: "Current will decrease / flow slower.",
    options: [
      "Current will decrease (flow slower)",
      "Current will increase (flow faster)",
      "Current will stop completely regardless of voltage",
      "Current will remain constant"
    ],
    hints: [
      "More obstruction means less flow.",
      "Denominator R gets bigger, so I = V/R becomes smaller."
    ],
    question_type: "follow_up",
    pedagogical_goal: "Confirm resolution of inverse proportionality misconception."
  }
};

export const MOCK_EVALUATION_INCORRECT = {
  correctness: false,
  confidence: 0.98,
  concept: "Inverse Proportionality (I = V/R)",
  misconception: "Direct proportionality confusion: Believing current increases when resistance increases",
  knowledge_gap: "Understanding resistance as opposition to charge flow rather than flow enhancement",
  reasoning_quality: "Common intuitive confusion",
  recommended_action: "give_analogy",
  teacher_thought: "Student confuses direct and inverse variation. Deploying physical hydraulic constriction analogy and numerical recalculation.",
  bloom_level: "Understanding"
};

export const MOCK_EVALUATION_CORRECT = {
  correctness: true,
  confidence: 0.99,
  concept: "Inverse Proportionality (I = V/R)",
  misconception: null,
  knowledge_gap: null,
  reasoning_quality: "High conceptual alignment",
  recommended_action: "continue",
  teacher_thought: "Student demonstrated solid grasp of the inverse relationship. Ready to advance to summative assessment.",
  bloom_level: "Application"
};

export const MOCK_ASSESSMENT_QUESTIONS = [
  {
    question_id: "assess_q1",
    prompt: "What is the fundamental formula of Ohm's Law relating Voltage (V), Current (I), and Resistance (R)?",
    options: [
      "V = I * R",
      "V = I / R",
      "I = V * R",
      "R = V * I"
    ],
    question_type: "mcq",
    difficulty: "beginner"
  },
  {
    question_id: "assess_q2",
    prompt: "Numerical Calculation: A circuit provides 24 Volts across a 6 Ohm resistor. What is the current flowing in Amperes?",
    question_type: "numerical",
    unit: "A",
    placeholder: "Enter value in Amperes...",
    expected_answer: "4",
    difficulty: "intermediate"
  },
  {
    question_id: "assess_q3",
    prompt: "Practical Reasoning: When a ceiling fan speed regulator reduces the fan's speed, what is it doing to the internal circuit resistance?",
    options: [
      "It increases resistance, reducing current to the motor",
      "It decreases resistance, increasing current to the motor",
      "It keeps resistance constant and doubles the voltage",
      "It breaks the circuit intermittently"
    ],
    question_type: "mcq",
    difficulty: "conceptual"
  }
];

export const MOCK_LEARNING_REPORT = {
  lesson_id: "plan_ohm_01",
  score: 92.0,
  concepts_understood: [
    "Ohm's Law fundamental relationship (V = I * R)",
    "Voltage as electrical driving pressure",
    "Current calculation with fixed resistors"
  ],
  weak_areas: [
    "Initial inverse proportionality intuition (overcome via hydraulic analogy)"
  ],
  misconceptions: [
    "Believed current increases when resistance increases under constant voltage"
  ],
  concepts_requiring_revision: [
    "Practice rearranging reciprocal equations (I = V/R, R = V/I)"
  ],
  estimated_revision_time_minutes: 10,
  recommended_practice: [
    "Solve 5 dual-resistor voltage divider circuits",
    "Experiment with the virtual Ohm's Law circuit slider to test extreme values (0.1Ω to 10kΩ)",
    "Review difference between Ohmic vs Non-Ohmic conductors"
  ],
  recommended_next_topic: "Kirchhoff's Laws & Series-Parallel Resistor Networks",
  overall_progress: "Completed Ohm's Law foundational loop with verified adaptive remediation.",
  completed_at: new Date().toISOString()
};
