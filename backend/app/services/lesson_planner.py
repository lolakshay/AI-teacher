"""
Lesson Planner Subsystem
Responsible for:
1. Deconstructing learning requests into ordered concepts & prerequisites
2. Designing structured LessonPlan conforming to Section 6.3
3. Initializing TeachingSteps tailored to student profile, language, and available time
"""

import uuid
from typing import List, Dict, Any, Optional
from backend.app.core.models import (
    LessonPlan, TeachingStep, LearningRequest, StudentProfile, QuestionPayload
)
from backend.app.services.visual_engine import visual_engine
from backend.app.services.material_pipeline import material_pipeline
from backend.app.services.llm_service import llm_service

class LessonPlanner:
    def create_lesson_plan(
        self,
        request: LearningRequest,
        profile: StudentProfile
    ) -> tuple[LessonPlan, List[TeachingStep]]:
        topic = request.topic or "Foundational Principles"
        lang = request.preferred_language
        rag_context = ""
        source_refs = []

        if request.material_id:
            chunks = material_pipeline.retrieve(request.material_id, topic, top_k=3)
            if chunks:
                rag_context = "\n".join([c["text"] for c in chunks])
                source_refs = [{"source": c["source_name"], "page": c["page"], "score": c["score"]} for c in chunks]

        # Topic detection for rich canonical curricula
        topic_lower = topic.lower()
        if "ohm" in topic_lower or "electric" in topic_lower or "circuit" in topic_lower:
            plan = LessonPlan(
                lesson_id=str(uuid.uuid4())[:8],
                topic="Ohm's Law & Circuit Dynamics",
                learning_objectives=[
                    "Understand what Voltage, Current, and Resistance represent physically",
                    "Master the governing equation V = I * R and its proportionalities",
                    "Predict circuit behavior when components change (e.g. increasing resistance)",
                    "Solve real-world circuit scenarios without calculation errors"
                ],
                prerequisites=["Basic concept of electric charge", "Elementary algebra (solving for unknowns)"],
                ordered_concepts=[
                    "Electric Potential (Voltage) & Charge Flow (Current)",
                    "Opposition to Flow (Resistance)",
                    "The Governing Relationship: V = I * R",
                    "Circuit Analysis & Practical Application"
                ],
                concept_dependencies={
                    "Electric Potential (Voltage) & Charge Flow (Current)": [],
                    "Opposition to Flow (Resistance)": ["Electric Potential (Voltage) & Charge Flow (Current)"],
                    "The Governing Relationship: V = I * R": ["Opposition to Flow (Resistance)"],
                    "Circuit Analysis & Practical Application": ["The Governing Relationship: V = I * R"]
                },
                estimated_duration=request.available_time,
                explanation_strategy="Physical water-pipe intuition -> Mathematical formulation -> Interactive dynamic circuit demonstration -> Diagnostic conceptual probing",
                examples=[
                    {"name": "Water Pipe Analogy", "voltage": "Pump pressure", "current": "Water flow rate", "resistance": "Valve constriction"},
                    {"name": "Household 12V LED", "voltage": "12V", "resistance": "4 Ohms", "current": "3 Amperes"}
                ],
                visual_requirements=[
                    {"type": "circuit", "description": "Interactive DC circuit with live electron flow simulation and resistance slider"},
                    {"type": "math_derivation", "description": "Rearranging V = I * R into I = V / R"}
                ],
                question_points=[
                    "What happens to current if resistance increases while voltage remains constant?",
                    "Calculate current if voltage is 24V and resistance is 6 Ohms."
                ],
                assessment_strategy="Formative concept probe during lesson + Summative 3-question mastery check",
                adaptation_rules=[
                    {"trigger": "inverting_proportionality", "action": "give_analogy", "focus": "Water constriction valve analogy"},
                    {"trigger": "math_confusion", "action": "simplify", "focus": "Isolate I = V/R step by step"}
                ]
            )

            # Generate initial teaching steps
            steps = self._build_ohms_law_steps(plan, lang, source_refs)

        elif "binary search" in topic_lower or "search" in topic_lower:
            plan = LessonPlan(
                lesson_id=str(uuid.uuid4())[:8],
                topic="Binary Search Algorithm",
                learning_objectives=[
                    "Understand why sorted order is a strict prerequisite",
                    "Master the divide-and-conquer strategy (low, mid, high pointers)",
                    "Analyze time complexity O(log n) versus linear search O(n)"
                ],
                prerequisites=["Array indexing", "Sorted sequences"],
                ordered_concepts=[
                    "Linear Search vs Divide & Conquer",
                    "The Three Pointers: Low, Mid, High",
                    "Halving the Search Space: Boundary Updates",
                    "Edge Cases & Time Complexity O(log n)"
                ],
                concept_dependencies={
                    "Linear Search vs Divide & Conquer": [],
                    "The Three Pointers: Low, Mid, High": ["Linear Search vs Divide & Conquer"],
                    "Halving the Search Space: Boundary Updates": ["The Three Pointers: Low, Mid, High"],
                    "Edge Cases & Time Complexity O(log n)": ["Halving the Search Space: Boundary Updates"]
                },
                estimated_duration=request.available_time,
                explanation_strategy="Dictionary search intuition -> Visual array pointer tracing -> Edge case testing",
                examples=[
                    {"name": "Dictionary Word Lookup", "approach": "Open in middle, check alphabetical order"}
                ],
                visual_requirements=[
                    {"type": "code_trace", "description": "Step-by-step array pointer visualization"}
                ],
                question_points=[
                    "Why MUST the array be sorted before applying Binary Search?",
                    "If arr[mid] < target, which pointer moves and how?"
                ],
                assessment_strategy="Pointer movement test + Complexity reasoning",
                adaptation_rules=[
                    {"trigger": "off_by_one", "action": "simplify", "focus": "low = mid + 1 versus low = mid"}
                ]
            )
            steps = self._build_binary_search_steps(plan, lang, source_refs)

        else:
            # Generalized topic builder
            plan = LessonPlan(
                lesson_id=str(uuid.uuid4())[:8],
                topic=topic,
                learning_objectives=[
                    f"Understand core concepts of {topic}",
                    f"Apply principles of {topic} to solve problems",
                    f"Demonstrate mastery through practical reasoning"
                ],
                prerequisites=["Foundational domain terminology"],
                ordered_concepts=[
                    f"Introduction to {topic}",
                    f"Key Mechanisms of {topic}",
                    f"Applications & Critical Probing"
                ],
                concept_dependencies={
                    f"Introduction to {topic}": [],
                    f"Key Mechanisms of {topic}": [f"Introduction to {topic}"],
                    f"Applications & Critical Probing": [f"Key Mechanisms of {topic}"]
                },
                estimated_duration=request.available_time,
                explanation_strategy="Conceptual introduction -> Subject demonstration -> Formative evaluation",
                examples=[{"name": f"Core example in {topic}"}],
                visual_requirements=[{"type": "concept_map"}],
                question_points=[f"What is the key governing principle behind {topic}?"],
                assessment_strategy="Final mastery evaluation"
            )
            steps = self._build_generic_steps(plan, lang, source_refs)

        return plan, steps

    def _build_ohms_law_steps(self, plan: LessonPlan, lang: str, source_refs: list) -> List[TeachingStep]:
        lesson_id = plan.lesson_id

        if lang.lower() == "hinglish":
            exp_intro = (
                "Namaste! Main aapka AI Teacher hoon. Aaj hum seekhenge physics ka ek bohot fundamental topic: "
                "Ohm's Law! Sochiye jab aap light switch on karte hain, to electricity kaise flow karti hai? "
                "Sabse pehle samajhte hain: Voltage (V) kya hai. Voltage ek tarah ka electrical pressure ya push hai "
                "jo electrons ko aage dhakelta hai, aur Current (I) hai un electrons ka actual flow rate!"
            )
            exp_concept2 = (
                "Ab aate hain teesre main player par: Resistance (R). Resistance ka matlab hai electrons ke raste mein aane wali "
                "rukawat ya opposition! George Simon Ohm ne discover kiya ki in teeno ka relation equation V = I * R se govern hota hai. "
                "Agar hum is equation ko Current (I) ke liye rearrange karein, to hume milta hai: I = V / R."
            )
            q_prompt = (
                "Dhyan se sochiye aur answer kijiye: Agar circuit mein Voltage (V) constant rahe, aur hum Resistance (R) ko badha dein, "
                "to Current (I) ke sath kya hoga? Kya Current badhega, kam hoga, ya same rahega?"
            )
        elif lang.lower() == "hindi":
            exp_intro = (
                "नमस्ते! मैं आपका एआई शिक्षक हूँ। आज हम भौतिकी के एक अत्यंत महत्वपूर्ण नियम — ओम का नियम (Ohm's Law) का अध्ययन करेंगे। "
                "विद्युत परिपथ में वोल्टेज (V) वह विद्युत दाब या बल है जो आवेश को गति देता है, और धारा (I) आवेश प्रवाह की दर है।"
            )
            exp_concept2 = (
                "अब बात करते हैं प्रतिरोध (Resistance - R) की। प्रतिरोध विद्युत धारा के मार्ग में आने वाली बाधा है। "
                "ओम के नियम के अनुसार: V = I * R, अर्थात धारा I = V / R होती है।"
            )
            q_prompt = (
                "यदि किसी परिपथ में वोल्टेज स्थिर रहे और प्रतिरोध (R) को बढ़ा दिया जाए, तो विद्युत धारा (I) पर क्या प्रभाव पड़ेगा?"
            )
        else:
            exp_intro = (
                "Hello! I am your AI Teacher. Today, we will explore one of the cornerstones of electrical physics: Ohm's Law. "
                "Before looking at any formula, let's understand the physical entities: Voltage (V) is the electrical potential difference "
                "— the push or pressure driving charge through a circuit. Current (I) is the actual flow rate of electrons passing a point per second."
            )
            exp_concept2 = (
                "Now let's introduce the opponent: Resistance (R). Resistance is the opposition to charge flow offered by materials and components. "
                "Ohm's Law unites these three variables in the celebrated equation: V = I * R. "
                "Rearranging for current gives us: I = V / R, showing that current is directly proportional to voltage, and inversely proportional to resistance."
            )
            q_prompt = (
                "Let's test your conceptual intuition: If the voltage in a circuit is held constant, but we increase the resistance, "
                "what happens to the electric current? Does current increase, decrease, or remain unchanged?"
            )

        step1 = TeachingStep(
            step_id=f"{lesson_id}_s1",
            lesson_id=lesson_id,
            concept_id="Electric Potential (Voltage) & Charge Flow (Current)",
            step_type="introduction",
            objective="Introduce the physical intuition behind Voltage and Current",
            explanation=exp_intro,
            example="Like a water pump creating pressure in a pipe.",
            visual_instruction=visual_engine.generate_circuit_visual(12.0, 4.0, highlight="voltage"),
            language=lang,
            difficulty="beginner",
            expected_understanding="Student understands Voltage as electrical push and Current as rate of charge flow.",
            source_references=source_refs,
            avatar_emotion="explaining"
        )

        step2 = TeachingStep(
            step_id=f"{lesson_id}_s2",
            lesson_id=lesson_id,
            concept_id="Opposition to Flow (Resistance) & Governing Law",
            step_type="demonstration",
            objective="Formulate Ohm's Law (V = I * R and I = V / R)",
            explanation=exp_concept2,
            example="If V = 12V and R = 4Ω, then Current I = 12 / 4 = 3 Amperes.",
            visual_instruction=visual_engine.generate_circuit_visual(12.0, 4.0, highlight="current"),
            language=lang,
            difficulty="beginner",
            expected_understanding="Student grasps that Current is inversely related to Resistance.",
            source_references=source_refs,
            avatar_emotion="thoughtful"
        )

        step3 = TeachingStep(
            step_id=f"{lesson_id}_s3",
            lesson_id=lesson_id,
            concept_id="The Governing Relationship: V = I * R",
            step_type="question",
            objective="Diagnose whether student understands inverse proportionality between Current and Resistance",
            explanation="Let's verify this core concept before advancing.",
            question=QuestionPayload(
                question_id="ohm_q1_proportionality",
                prompt=q_prompt,
                expected_answer="Current decreases because resistance opposes the flow of electric charge (I = V / R).",
                hints=["Look at the equation I = V / R. Where is R situated?", "Think of resistance as squeezing a water pipe."],
                question_type="diagnostic",
                pedagogical_goal="Detect misconception regarding direct vs inverse proportionality"
            ),
            visual_instruction=visual_engine.generate_circuit_visual(12.0, 4.0, highlight="resistance"),
            language=lang,
            difficulty="beginner",
            expected_understanding="Student answers that current decreases.",
            source_references=source_refs,
            avatar_emotion="attentive"
        )

        return [step1, step2, step3]

    def _build_binary_search_steps(self, plan: LessonPlan, lang: str, source_refs: list) -> List[TeachingStep]:
        lesson_id = plan.lesson_id
        step1 = TeachingStep(
            step_id=f"{lesson_id}_s1",
            lesson_id=lesson_id,
            concept_id="Linear Search vs Divide & Conquer",
            step_type="introduction",
            objective="Establish why sorted arrays allow logarithmic search",
            explanation="Binary Search solves the problem of finding an element in a sorted list in O(log n) time by halving the search space each step.",
            visual_instruction=visual_engine.for_topic("binary search", "intro"),
            language=lang,
            source_references=source_refs,
            avatar_emotion="explaining"
        )
        step2 = TeachingStep(
            step_id=f"{lesson_id}_s2",
            lesson_id=lesson_id,
            concept_id="The Three Pointers: Low, Mid, High",
            step_type="question",
            objective="Test understanding of pointer manipulation",
            explanation="Let's trace how mid is evaluated.",
            question=QuestionPayload(
                question_id="bs_q1",
                prompt="If arr[mid] is smaller than the target, which pointer must move and to what position?",
                expected_answer="low = mid + 1",
                question_type="diagnostic"
            ),
            visual_instruction=visual_engine.for_topic("binary search", "pointers"),
            language=lang,
            source_references=source_refs,
            avatar_emotion="attentive"
        )
        return [step1, step2]

    def _build_generic_steps(self, plan: LessonPlan, lang: str, source_refs: list) -> List[TeachingStep]:
        lesson_id = plan.lesson_id
        step1 = TeachingStep(
            step_id=f"{lesson_id}_s1",
            lesson_id=lesson_id,
            concept_id=plan.ordered_concepts[0],
            step_type="introduction",
            objective=f"Foundational introduction to {plan.topic}",
            explanation=f"Welcome! Today we will break down {plan.topic} step-by-step so you master the core intuition and practical application.",
            visual_instruction=visual_engine.for_topic(plan.topic, plan.ordered_concepts[0]),
            language=lang,
            source_references=source_refs,
            avatar_emotion="explaining"
        )
        step2 = TeachingStep(
            step_id=f"{lesson_id}_s2",
            lesson_id=lesson_id,
            concept_id=plan.ordered_concepts[1] if len(plan.ordered_concepts) > 1 else plan.ordered_concepts[0],
            step_type="question",
            objective="Formative check on core principle",
            explanation="Let's test your understanding with an intuitive question.",
            question=QuestionPayload(
                question_id=f"{lesson_id}_q1",
                prompt=f"Explain in your own words: What is the main purpose of {plan.topic} and how does it operate?",
                expected_answer="Accurate conceptual summary of governing principles",
                question_type="conceptual_check"
            ),
            visual_instruction=visual_engine.for_topic(plan.topic, "probing"),
            language=lang,
            source_references=source_refs,
            avatar_emotion="attentive"
        )
        return [step1, step2]

lesson_planner = LessonPlanner()
