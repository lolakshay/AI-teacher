export const DEMO_PRESETS = [
  {
    id: 'canonical_ohms_law',
    title: "Ohm's Law & Circuit Dynamics",
    subject: "Physics",
    topic: "Ohm's Law & Circuit Dynamics",
    level: "beginner",
    language: "Hinglish",
    time: 20,
    style: "analogy_driven",
    description: "Foundation electrical physics: beginner student in Hinglish. Features circuit simulation, live water pipe analogy, and misconception diagnosis.",
    canonicalPrompt: "I am a beginner. Teach me Ohm's Law in 20 minutes in Hinglish with simple examples. Ask me questions and test me at the end.",
    testMisconceptionAnswer: "Current increases"
  },
  {
    id: 'binary_search',
    title: "Binary Search Algorithm",
    subject: "Computer Science",
    topic: "Binary Search Algorithm",
    level: "intermediate",
    language: "English",
    time: 15,
    style: "interactive",
    description: "Divide-and-conquer strategy, pointer tracing (low, mid, high), and logarithmic time complexity.",
    canonicalPrompt: "Teach me Binary Search in 15 minutes with step-by-step code traces and test my boundary conditions.",
    testMisconceptionAnswer: "low = mid"
  },
  {
    id: 'photosynthesis',
    title: "Photosynthesis & Solar Energy",
    subject: "Biology",
    topic: "Photosynthesis & Cellular Energy Transfer",
    level: "high_school",
    language: "English",
    time: 15,
    style: "visual",
    description: "Light-dependent and Calvin cycle reactions, chlorophyll absorption spectra, and biological processes.",
    canonicalPrompt: "Explain Photosynthesis with biological process diagrams and evaluate my understanding of electron transport.",
    testMisconceptionAnswer: "Plants only produce oxygen and do not respire"
  }
];
