"""
Assessment Question Generator conforming to Sections 8, 9, 10, 11, 12, 32, 33, 51.
Generates grounded, validated, multi-modal assessment questions with deterministic fallbacks.
"""

import random
import uuid
import logging
from typing import List, Dict, Any, Optional

from backend.assessment.models.config import AssessmentConfig
from backend.assessment.models.question import AssessmentQuestion
from backend.assessment.validators.assessment_validator import assessment_validator
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """
    Orchestrates creation and assembly of assessment questions.
    Uses LLM for grounded generation when available, backed by verified pedagogical templates.
    """

    def generate_questions(
        self,
        config: AssessmentConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> List[AssessmentQuestion]:
        """
        Main entrypoint: generates balanced, validated assessment questions.
        """
        context = context or {}
        topic = config.topic or "Foundational Science"
        rag_chunks = context.get("rag_context") or config.source_references or []

        # 1. Try LLM generation if client available
        questions: List[AssessmentQuestion] = []
        try:
            questions = self._generate_with_llm(config, context, rag_chunks)
        except Exception as e:
            logger.warning(f"LLM question generation failed or unconfigured: {e}. Using deterministic templates.")
            questions = []

        # 2. Validate LLM questions; if empty or invalid, use grounded templates
        is_valid, errors = assessment_validator.validate_assessment(questions, config)
        if not is_valid or len(questions) < config.question_count:
            logger.info(f"Using template generator for topic: {topic}")
            questions = self._generate_from_templates(config, context, rag_chunks)

        # 3. Apply randomization if requested, with reproducible seed
        if config.randomize:
            rng = random.Random(config.random_seed) if config.random_seed is not None else random.Random()
            rng.shuffle(questions)

        # 4. Limit to question_count while ensuring minimum 1
        final_count = max(1, min(config.question_count, len(questions)))
        final_questions = questions[:final_count]

        # 5. Final validation guarantee
        assessment_validator.ensure_valid(final_questions, config)
        return final_questions

    def _generate_from_templates(
        self,
        config: AssessmentConfig,
        context: Optional[Dict[str, Any]],
        rag_chunks: List[Dict[str, Any]]
    ) -> List[AssessmentQuestion]:
        """
        Provides rich, pedagogical template questions with exact concepts and weights.
        """
        topic_lower = config.topic.lower()
        lang_lower = (config.language or "english").lower()
        aid = config.assessment_id

        # Attach first RAG source reference if available
        base_source = [rag_chunks[0]] if rag_chunks else []

        if "ohm" in topic_lower or "circuit" in topic_lower:
            if lang_lower == "hinglish":
                return [
                    AssessmentQuestion(
                        question_id=f"ohm_q1_{aid[:6]}",
                        assessment_id=aid,
                        text="Ohm's Law ka fundamental formula kya hai, aur usme har variable kya represent karta hai?",
                        type="short_answer",
                        expected_answer="V = I * R (Voltage = Current * Resistance)",
                        expected_concept="ohms_law_formula",
                        difficulty=0.3,
                        points=1.0,
                        rubric=["States V = I*R", "Identifies V as Voltage, I as Current, R as Resistance"],
                        source_references=base_source,
                        metadata={"bloom_level": "Remembering"}
                    ),
                    AssessmentQuestion(
                        question_id=f"ohm_q2_{aid[:6]}",
                        assessment_id=aid,
                        text="Circuit Calculation: Agar ek circuit mein Voltage 10 V hai aur Resistance 5 Ohms hai, to Current kitna flow karega?",
                        type="numerical",
                        expected_value=2.0,
                        unit="A",
                        tolerance=0.05,
                        expected_concept="voltage_calculation",
                        difficulty=0.4,
                        points=2.0,
                        rubric=["Calculates I = V/R = 10/5 = 2 A", "Correct unit Amperes"],
                        source_references=base_source,
                        metadata={"bloom_level": "Applying"}
                    ),
                    AssessmentQuestion(
                        question_id=f"ohm_q3_{aid[:6]}",
                        assessment_id=aid,
                        text="Conceptual Check: Agar voltage constant rahe aur circuit ki resistance badh jaye, to current par kya asar hoga?",
                        type="conceptual",
                        expected_answer="Current kam hoga (I = V/R ke mutabiq inverse relationship hai).",
                        expected_concept="inverse_relationship",
                        difficulty=0.5,
                        points=2.0,
                        rubric=["Recognizes current decreases", "Mentions inverse relationship or I = V/R"],
                        source_references=base_source,
                        metadata={"bloom_level": "Understanding"}
                    ),
                    AssessmentQuestion(
                        question_id=f"ohm_q4_{aid[:6]}",
                        assessment_id=aid,
                        text="MCQ: Current ki SI unit kya hoti hai?",
                        type="mcq",
                        options=["Volt", "Ampere", "Ohm", "Watt"],
                        correct_option="Ampere",
                        expected_concept="units_measurement",
                        difficulty=0.2,
                        points=1.0,
                        source_references=base_source,
                        metadata={"bloom_level": "Remembering"}
                    ),
                    AssessmentQuestion(
                        question_id=f"ohm_q5_{aid[:6]}",
                        assessment_id=aid,
                        text="Problem Solving: Ek 24 V battery ek 12 Ω resistor se connected hai. Resistor ko double karke 24 Ω karne par naya current kitna hoga?",
                        type="numerical",
                        expected_value=1.0,
                        unit="A",
                        tolerance=0.05,
                        expected_concept="inverse_relationship",
                        difficulty=0.6,
                        points=3.0,
                        rubric=["Original current = 2A", "New current = 24/24 = 1A"],
                        source_references=base_source,
                        metadata={"bloom_level": "Analyzing"}
                    )
                ]
            else:
                # English Ohm's Law
                return [
                    AssessmentQuestion(
                        question_id=f"ohm_q1_{aid[:6]}",
                        assessment_id=aid,
                        text="What is the fundamental mathematical formula for Ohm's Law and what does each variable represent?",
                        type="short_answer",
                        expected_answer="V = I * R (Voltage = Current * Resistance)",
                        expected_concept="ohms_law_formula",
                        difficulty=0.3,
                        points=1.0,
                        rubric=["States V = I * R", "Identifies V = Voltage, I = Current, R = Resistance"],
                        source_references=base_source,
                        metadata={"bloom_level": "Remembering"}
                    ),
                    AssessmentQuestion(
                        question_id=f"ohm_q2_{aid[:6]}",
                        assessment_id=aid,
                        text="Circuit Calculation: If V = 10 V and R = 5 Ω, calculate the current flowing through the circuit.",
                        type="numerical",
                        expected_value=2.0,
                        unit="A",
                        tolerance=0.05,
                        expected_concept="voltage_calculation",
                        difficulty=0.4,
                        points=2.0,
                        rubric=["Applies I = V / R", "Yields 2 A"],
                        source_references=base_source,
                        metadata={"bloom_level": "Applying"}
                    ),
                    AssessmentQuestion(
                        question_id=f"ohm_q3_{aid[:6]}",
                        assessment_id=aid,
                        text="Conceptual Reasoning: If voltage remains constant and resistance increases, what happens to the current?",
                        type="conceptual",
                        expected_answer="Current decreases because current is inversely proportional to resistance (I = V/R).",
                        expected_concept="inverse_relationship",
                        difficulty=0.5,
                        points=2.0,
                        rubric=["Identifies current decreases", "Explains inverse relationship"],
                        source_references=base_source,
                        metadata={"bloom_level": "Understanding"}
                    ),
                    AssessmentQuestion(
                        question_id=f"ohm_q4_{aid[:6]}",
                        assessment_id=aid,
                        text="Which unit measures electrical resistance in the SI system?",
                        type="mcq",
                        options=["Volt", "Ampere", "Ohm", "Joule"],
                        correct_option="Ohm",
                        expected_concept="units_measurement",
                        difficulty=0.2,
                        points=1.0,
                        source_references=base_source,
                        metadata={"bloom_level": "Remembering"}
                    ),
                    AssessmentQuestion(
                        question_id=f"ohm_q5_{aid[:6]}",
                        assessment_id=aid,
                        text="Circuit Analysis: If voltage is 24 V across a 12 Ω resistor, and resistance is doubled to 24 Ω, calculate the new current.",
                        type="numerical",
                        expected_value=1.0,
                        unit="A",
                        tolerance=0.05,
                        expected_concept="inverse_relationship",
                        difficulty=0.6,
                        points=3.0,
                        rubric=["Calculates 24 / 24 = 1 A", "Demonstrates inverse scaling"],
                        source_references=base_source,
                        metadata={"bloom_level": "Analyzing"}
                    )
                ]

        # Generic STEM / Algorithm template
        return [
            AssessmentQuestion(
                question_id=f"gen_q1_{aid[:6]}",
                assessment_id=aid,
                text=f"Explain the primary principle and governing equation behind {config.topic}.",
                type="conceptual",
                expected_answer=f"Fundamental definition and operational principles of {config.topic}",
                expected_concept=f"{config.topic.lower().replace(' ', '_')}_fundamentals",
                difficulty=0.3,
                points=1.0,
                source_references=base_source,
                metadata={"bloom_level": "Understanding"}
            ),
            AssessmentQuestion(
                question_id=f"gen_q2_{aid[:6]}",
                assessment_id=aid,
                text=f"Which of the following best describes the core operational mechanism of {config.topic}?",
                type="mcq",
                options=[
                    f"Core mechanism of {config.topic}",
                    "Unrelated opposite behavior",
                    "Random state alteration",
                    "None of the above"
                ],
                correct_option=f"Core mechanism of {config.topic}",
                expected_concept=f"{config.topic.lower().replace(' ', '_')}_mechanism",
                difficulty=0.4,
                points=2.0,
                source_references=base_source,
                metadata={"bloom_level": "Remembering"}
            ),
            AssessmentQuestion(
                question_id=f"gen_q3_{aid[:6]}",
                assessment_id=aid,
                text=f"How do key parameters interact when primary inputs scale in {config.topic}?",
                type="short_answer",
                expected_answer="Proportional response and parameter dependency analysis",
                expected_concept=f"{config.topic.lower().replace(' ', '_')}_dynamics",
                difficulty=0.6,
                points=2.0,
                source_references=base_source,
                metadata={"bloom_level": "Analyzing"}
            )
        ]

    def _generate_with_llm(
        self,
        config: AssessmentConfig,
        context: Dict[str, Any],
        rag_chunks: List[Dict[str, Any]]
    ) -> List[AssessmentQuestion]:
        """
        Uses LLM with grounded prompt to synthesize structured questions.
        """
        from backend.app.services.llm_service import gemini_client
        if not gemini_client:
            return []

        rag_summary = "\n".join([
            f"- Doc: {c.get('document_id', 'doc')}, Section: {c.get('section', 'N/A')}: {c.get('text', '')[:200]}"
            for c in rag_chunks[:3]
        ])

        system_instruction = (
            "You are AGENT 7: Expert Assessment Designer for an AI Educator. "
            "Generate formal, grounded assessment questions based STRICTLY on the taught topic and provided material. "
            "Do NOT invent concepts outside the topic. Output ONLY a valid JSON list of question objects."
        )

        user_prompt = f"""
Topic: {config.topic}
Question Count: {config.question_count}
Target Concepts: {config.coverage}
Language: {config.language}
Difficulty: {config.difficulty}
Allowed Types: {config.question_types}
Grounded Material:
{rag_summary}

Generate exactly {config.question_count} questions. For each question include:
- question_id (str)
- text (str)
- type ("mcq" | "short_answer" | "numerical" | "conceptual")
- options (list of str, required if mcq, else null)
- correct_option (str, required if mcq, else null)
- expected_answer (str or null)
- expected_value (float or null, if numerical)
- unit (str or null, if numerical)
- tolerance (float, default 0.05)
- expected_concept (str)
- difficulty (float, 0.0 to 1.0)
- points (float, e.g. 1.0 to 3.0)
- rubric (list of str)
"""
        result_json = llm_service.generate_json(user_prompt, system_instruction, fallback_data={})
        if isinstance(result_json, list):
            parsed = []
            for item in result_json:
                item["assessment_id"] = config.assessment_id
                if rag_chunks:
                    item["source_references"] = [rag_chunks[0]]
                parsed.append(AssessmentQuestion(**item))
            return parsed

        return []


question_generator = QuestionGenerator()
