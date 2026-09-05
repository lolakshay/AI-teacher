"""
Adaptation Engine Subsystem
Transforms diagnostic evaluation results into concrete pedagogical interventions:
1. Synthesizes adaptive re-explanations (using analogies, simplified mathematics, or step-by-step guidance)
2. Updates dynamic visuals to expose the misconception visually
3. Generates targeted follow-up probe questions
"""

import uuid
from typing import Optional
from backend.app.core.models import (
    TeachingStep, EvaluationResult, QuestionPayload, VisualInstruction
)
from backend.app.services.visual_engine import visual_engine

class AdaptationEngine:
    def create_adaptation_step(
        self,
        evaluation: EvaluationResult,
        current_step: TeachingStep,
        language: str = "Hinglish"
    ) -> TeachingStep:
        lang_lower = language.lower()
        step_id = f"adapt_{uuid.uuid4().hex[:6]}"

        if "inverting_proportionality" in (evaluation.misconception or "").lower() or "direct proportionality" in (evaluation.misconception or "").lower() or "ohm" in current_step.concept_id.lower():
            if lang_lower == "hinglish":
                explanation = (
                    "Koi baat nahi, ye ek bohot hi common misunderstanding hai! Chaliye ek real-life analogy se samajhte hain. "
                    "Sochiye ek paani ka pipe hai jisme se paani full speed mein nikal raha hai. Ab agar aap pipe ke aage hath rakh dein "
                    "ya valve ko tight kar dein — yaani resistance badha dein — to kya paani ka flow badhega ya kam hoga? "
                    "Zahir si baat hai, flow kam ho jayega! "
                    "The exact same thing happens in a circuit: Resistance electrons ke flow ko rokta hai. Isliye jab Resistance badhta hai, "
                    "to Current hamesha KAM hota hai (I = V / R)!"
                )
                q_prompt = (
                    "Ab batayiye: Agar hum Resistance ko 4 Ohms se badha kar 12 Ohms kar dein (aur Voltage 12V constant rahe), "
                    "to Current 3A se badhkar 5A hoga, ya kam hokar 1A ho jayega?"
                )
            elif lang_lower == "hindi":
                explanation = (
                    "कोई बात नहीं, यह एक बहुत स्वाभाविक भ्रम है। इसे पानी के पाइप के उदाहरण से समझते हैं। "
                    "यदि आप पानी बहते पाइप को दबा दें (प्रतिरोध बढ़ा दें), तो पानी का बहाव घट जाता है। "
                    "विद्युत परिपथ में भी यही होता है: प्रतिरोध आवेश के प्रवाह को रोकता है। अतः प्रतिरोध बढ़ने पर विद्युत धारा सदैव घटती है (I = V / R)!"
                )
                q_prompt = (
                    "अब बताइए: यदि प्रतिरोध को 4 ओम से बढ़ाकर 12 ओम कर दिया जाए (12V पर), तो धारा 3A से बढ़कर 5A होगी या घटकर 1A रह जाएगी?"
                )
            else:
                explanation = (
                    "No worries at all — this is one of the most frequent misconceptions in physics! Let's use a physical analogy. "
                    "Imagine a water hose with water flowing smoothly. If you step on the hose or squeeze the nozzle shut — which represents "
                    "increasing resistance — does the water flow increase or decrease? Of course, the flow constricts and decreases! "
                    "Electric circuits behave identically: Resistance is physical friction opposing the electrons. As Resistance increases, "
                    "Current must decrease according to I = V / R."
                )
                q_prompt = (
                    "Now let's verify: If we increase the resistance from 4 Ohms to 12 Ohms (with Voltage fixed at 12V), "
                    "does current increase to 5A or decrease to 1A?"
                )

            # Updated visual showing higher resistance (12 Ohms) and reduced current (1A)
            visual = visual_engine.generate_circuit_visual(v=12.0, r=12.0, highlight="resistance")

            return TeachingStep(
                step_id=step_id,
                lesson_id=current_step.lesson_id,
                concept_id=current_step.concept_id,
                step_type="re_explanation",
                objective="Resolve inverse proportionality misconception using hydraulic pipe analogy and circuit visualization",
                explanation=explanation,
                example="Water hose valve constriction: squeezing the valve drops the flow rate from 3 L/s to 1 L/s.",
                visual_instruction=visual,
                language=language,
                difficulty="beginner",
                question=QuestionPayload(
                    question_id=f"followup_{uuid.uuid4().hex[:6]}",
                    prompt=q_prompt,
                    expected_answer="Current decreases to 1A because I = 12 / 12 = 1A.",
                    hints=["Recall the water hose analogy.", "Use I = V / R: 12 / 12 = ?"],
                    question_type="follow_up",
                    pedagogical_goal="Verify student resolution of inverse proportionality misconception"
                ),
                expected_understanding="Student understands that Current decreases when Resistance increases.",
                avatar_emotion="encouraging"
            )

        # Generic adaptation
        return TeachingStep(
            step_id=step_id,
            lesson_id=current_step.lesson_id,
            concept_id=current_step.concept_id,
            step_type="re_explanation",
            objective=f"Clarify {current_step.concept_id} using simplified decomposition",
            explanation=(
                f"Let's break this down into smaller steps. When analyzing {current_step.concept_id}, "
                f"notice how the key factors interact directly."
            ),
            visual_instruction=current_step.visual_instruction,
            language=language,
            difficulty="beginner",
            question=QuestionPayload(
                question_id=f"followup_{uuid.uuid4().hex[:6]}",
                prompt=f"Considering this simpler perspective, how would you summarize {current_step.concept_id}?",
                expected_answer="Correct simplified answer",
                question_type="follow_up"
            ),
            expected_understanding="Student demonstrates corrected understanding.",
            avatar_emotion="encouraging"
        )

adaptation_engine = AdaptationEngine()
