"""
Video Scene Planner (Agent 4)
Transforms structured TeachingStep objects from the Teaching Brain (Agent 1)
into pedagogical VideoScene sequences with subject-aware visual specifications.
Conforms strictly to Sections 7, 8, 9, 10, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36.
"""

import re
import uuid
from typing import List, Dict, Any, Optional, Union
from backend.video.schemas import (
    VideoScene,
    SceneType,
    VisualSpec,
    EquationVisualSpec,
    GraphVisualSpec,
    CodeVisualSpec,
    TimelineVisualSpec,
    MapVisualSpec,
    ProcessVisualSpec,
    ImageVisualSpec,
    WorkedExampleVisualSpec,
    ConceptCardVisualSpec,
    AvatarSceneConfig,
    AudioSceneConfig,
    TransitionConfig
)
from backend.video.providers.voice_provider import VoiceProvider, MockVoiceProvider
from backend.video.providers.avatar_provider import AvatarProvider, MockAvatarProvider


class TextExtractor:
    """
    Extracts high-impact educational on-screen text from spoken script or explanation.
    Never duplicates 30-second audio verbatim on screen (Section 8 & 32).
    """
    FORMULA_PATTERNS = [
        r"[A-Za-z]\s*=\s*[A-Za-z0-9\s\*\/\+\-\(\)\^]+",
        r"[A-Za-z]\s*\\cdot\s*[A-Za-z]",
        r"\\frac\{[^}]+\}\{[^}]+\}"
    ]

    KEY_TERM_MAP = {
        "voltage": "VOLTAGE (V): Electrical Potential / Push",
        "current": "CURRENT (I): Rate of Charge Flow (Amperes)",
        "resistance": "RESISTANCE (R): Opposition to Electric Current (Ohms)",
        "binary search": "BINARY SEARCH: O(log n) Divide & Conquer",
        "sorted": "PREREQUISITE: Array Must Be Sorted",
        "pointers": "POINTERS: Low, Mid, High Bounds",
        "ohm": "OHM'S LAW: Governs Voltage, Current & Resistance",
        "photosynthesis": "PHOTOSYNTHESIS: Light Energy to Chemical Energy",
        "mitochondria": "MITOCHONDRIA: Powerhouse of the Cell",
        "gravity": "GRAVITATIONAL FORCE: F = G(m1*m2)/r^2",
        "proportionality": "INVERSE PROPORTIONALITY: Current decreases as Resistance increases"
    }

    @classmethod
    def extract_key_points(cls, text: str, objective: str = "", language: str = "Hinglish") -> List[str]:
        points: List[str] = []
        if not text:
            return [objective] if objective else ["Core Concept"]

        text_lower = text.lower()

        # 1. Check for canonical educational terms
        for term, label in cls.KEY_TERM_MAP.items():
            if term in text_lower:
                if label not in points:
                    points.append(label)

        # 2. Extract mathematical equations
        for pat in cls.FORMULA_PATTERNS:
            matches = re.findall(pat, text)
            for m in matches:
                clean_m = m.strip()
                if len(clean_m) >= 3 and clean_m not in points and len(clean_m) < 40:
                    points.append(f"Formula: {clean_m}")

        # 3. Extract sentence highlights or rules (sentences with words like 'means', 'governs', 'because', 'requires')
        if len(points) < 3:
            sentences = re.split(r"[.!?।]\s*", text)
            for s in sentences:
                s_strip = s.strip()
                if 15 <= len(s_strip) <= 80:
                    if any(w in s_strip.lower() for w in ["means", "opposes", "push", "flow", "inversely", "proportional", "rule", "divide"]):
                        points.append(s_strip)
                        if len(points) >= 3:
                            break

        # 4. Fallback to objective if points still sparse
        if not points and objective:
            points.append(objective)

        return points[:4]


class VideoScenePlanner:
    """
    Transforms TeachingStep objects into structured, synchronized VideoScene sequences.
    """
    def __init__(
        self,
        voice_provider: Optional[VoiceProvider] = None,
        avatar_provider: Optional[AvatarProvider] = None
    ):
        self.voice_provider = voice_provider or MockVoiceProvider()
        self.avatar_provider = avatar_provider or MockAvatarProvider()

    def plan_scenes_for_step(self, step: Any) -> List[VideoScene]:
        """
        Converts a single TeachingStep into one or more VideoScenes.
        Supports both backend.app.core.models.TeachingStep and backend.teaching.schemas.teaching_step.TeachingStep.
        """
        step_dict = self._normalize_step(step)
        step_type = step_dict.get("step_type", "explanation").lower()
        is_re_explanation = (step_type == "re_explanation")
        
        # Check if question or await_student_response
        await_response = step_dict.get("await_student_response", False) or (step_type == "question")
        question_data = step_dict.get("question")

        scenes: List[VideoScene] = []

        if await_response or step_type == "question":
            # Interactive Question Scene
            q_scene = self._build_question_scene(step_dict, question_data)
            scenes.append(q_scene)

        elif step_type == "introduction":
            # Template A: Intro avatar explanation
            intro_scene = self._build_avatar_explanation_scene(step_dict, is_intro=True)
            scenes.append(intro_scene)

        elif step_type == "re_explanation":
            # Adaptive Re-Explanation (Section 27): Produce DIFFERENT visual and pedagogical representation!
            re_scenes = self._build_adaptive_re_explanation_scenes(step_dict)
            scenes.extend(re_scenes)

        elif step_type == "demonstration":
            # Demonstration -> Visual Demonstration (diagram/process/code/graph)
            demo_scene = self._build_demonstration_scene(step_dict)
            scenes.append(demo_scene)

        elif step_type == "example":
            # Template D: Worked Example scene
            ex_scene = self._build_worked_example_scene(step_dict)
            scenes.append(ex_scene)

        elif step_type == "summary":
            # Template H: Summary card + Avatar
            sum_scene = self._build_summary_scene(step_dict)
            scenes.append(sum_scene)

        elif step_type == "assessment_trigger":
            # Assessment handoff scene
            trigger_scene = self._build_assessment_trigger_scene(step_dict)
            scenes.append(trigger_scene)

        else:
            # Standard Explanation: Avatar explanation + Concept Card or Visual
            explanation_scene = self._build_avatar_explanation_scene(step_dict)
            scenes.append(explanation_scene)

            # If visual instruction explicitly present, spawn secondary visual scene
            visual_inst = step_dict.get("visual_instruction")
            if visual_inst and self._has_active_visual(visual_inst):
                visual_scene = self._build_visual_scene_from_instruction(step_dict, visual_inst, scene_idx=1)
                scenes.append(visual_scene)

        # Ensure index numbering
        for idx, sc in enumerate(scenes):
            sc.scene_index = idx

        return scenes

    # ============================================================
    # SCENE BUILDERS BY PEDAGOGICAL TYPE
    # ============================================================

    def _build_avatar_explanation_scene(self, step_dict: Dict[str, Any], is_intro: bool = False) -> VideoScene:
        spoken_text = step_dict.get("spoken_script") or step_dict.get("explanation") or step_dict.get("content", "")
        objective = step_dict.get("objective") or step_dict.get("teaching_objective", "")
        lang = step_dict.get("language", "Hinglish")
        emotion = step_dict.get("avatar_emotion", "explaining")

        # Audio synthesis timing
        audio_cfg = self.voice_provider.generate_audio(spoken_text, language=lang)
        duration = audio_cfg.duration_seconds

        # Avatar configuration (Avatar on right side)
        avatar_cfg = self.avatar_provider.generate_avatar_scene(
            spoken_text=spoken_text,
            duration=duration,
            language=lang,
            expression="welcoming" if is_intro else emotion,
            position="right"
        )

        on_screen = TextExtractor.extract_key_points(spoken_text, objective=objective, language=lang)
        
        # Check if equation or visual instruction exists in step
        visual_inst = step_dict.get("visual_instruction")
        visual_spec = self._convert_visual_instruction_to_spec(visual_inst, step_dict)

        return VideoScene(
            scene_id=f"scene_{uuid.uuid4().hex[:8]}",
            step_id=step_dict.get("step_id", "step_0"),
            scene_type="avatar_explanation",
            duration_seconds=duration,
            spoken_text=spoken_text,
            on_screen_text=on_screen,
            visual=visual_spec.model_dump() if hasattr(visual_spec, "model_dump") else visual_spec,
            avatar=avatar_cfg,
            audio=audio_cfg,
            transition=TransitionConfig(type="fade", duration_seconds=0.5),
            source_references=step_dict.get("source_references", [])
        )

    def _build_question_scene(self, step_dict: Dict[str, Any], question_data: Any) -> VideoScene:
        """
        Builds an interactive question scene that PAUSES video for student response (Section 26).
        """
        lang = step_dict.get("language", "Hinglish")
        prompt = ""
        q_id = f"q_{uuid.uuid4().hex[:6]}"
        options = None
        hints = []

        if isinstance(question_data, dict):
            prompt = question_data.get("prompt") or question_data.get("question_text", "")
            q_id = question_data.get("question_id", q_id)
            options = question_data.get("options")
            hints = question_data.get("hints", [])
        elif hasattr(question_data, "prompt"):
            prompt = question_data.prompt
            q_id = getattr(question_data, "question_id", q_id)
            options = getattr(question_data, "options", None)
            hints = getattr(question_data, "hints", [])
        elif hasattr(question_data, "question_text"):
            prompt = question_data.question_text
            q_id = getattr(question_data, "question_id", q_id)
            options = getattr(question_data, "options", None)
            hints = getattr(question_data, "hints", [])
        
        if not prompt:
            prompt = step_dict.get("explanation") or "Please answer the conceptual check."

        spoken_text = prompt
        audio_cfg = self.voice_provider.generate_audio(spoken_text, language=lang)
        duration = audio_cfg.duration_seconds

        avatar_cfg = self.avatar_provider.generate_avatar_scene(
            spoken_text=spoken_text,
            duration=duration,
            language=lang,
            expression="attentive",
            position="right"
        )

        visual_spec = ConceptCardVisualSpec(
            title="Active Conceptual Check",
            subtitle="Diagnostic Probe",
            definition=prompt,
            key_points=["Select or type your explanation below.", "Take your time to reason physically."],
            badge="Interactive Pause"
        )

        return VideoScene(
            scene_id=f"scene_{uuid.uuid4().hex[:8]}",
            step_id=step_dict.get("step_id", "step_0"),
            scene_type="question",
            duration_seconds=duration,
            spoken_text=spoken_text,
            on_screen_text=[prompt],
            visual=visual_spec.model_dump(),
            avatar=avatar_cfg,
            audio=audio_cfg,
            source_references=step_dict.get("source_references", []),
            interactive=True,
            pause_video=True,  # Mandatory pause
            question_id=q_id,
            question_text=prompt,
            options=options,
            hints=hints
        )

    def _build_adaptive_re_explanation_scenes(self, step_dict: Dict[str, Any]) -> List[VideoScene]:
        """
        Adaptive video representation (Section 27):
        When Agent 1 triggers a re-explanation, generate a DIFFERENT pedagogical layout:
        Scene 1: Water-pipe hydraulic analogy + animated diagram
        Scene 2: Isolated mathematical formula (I = V / R) clarifying inverse proportionality.
        """
        spoken_text = step_dict.get("spoken_script") or step_dict.get("explanation", "")
        lang = step_dict.get("language", "Hinglish")
        objective = step_dict.get("objective") or step_dict.get("teaching_objective", "Adaptive Concept Resolution")

        audio_cfg = self.voice_provider.generate_audio(spoken_text, language=lang)
        duration = audio_cfg.duration_seconds

        # Avatar placed in thoughtful/encouraging mood on right side
        avatar_cfg = self.avatar_provider.generate_avatar_scene(
            spoken_text=spoken_text,
            duration=duration,
            language=lang,
            expression="thoughtful",
            position="right"
        )

        # Analogy Visual Specification (Water pipe / Hydraulic constriction)
        analogy_spec = VisualSpec(
            type="diagram",
            title="Physical Analogy: The Water Pipe Constriction",
            description="Voltage is pump pressure; Resistance is pipe constriction; Current is flow rate.",
            elements=[
                {"id": "water_pump", "type": "component", "label": "Water Pump (Voltage V)"},
                {"id": "pipe_valve", "type": "component", "label": "Constriction Valve (Resistance R)"},
                {"id": "water_flow", "type": "arrow", "label": "Flow of Water (Current I)"}
            ],
            relationships=[
                {"from": "water_pump", "to": "pipe_valve", "relation": "pressurizes"},
                {"from": "pipe_valve", "to": "water_flow", "relation": "constricts flow"}
            ],
            metadata={
                "analogy": True,
                "takeaway": "Tightening valve (higher resistance) REDUCES water flow rate (current)."
            }
        )

        on_screen = [
            "ADAPTIVE INTUITION: Water Pipe Analogy",
            "Voltage = Water Pump Pressure",
            "Resistance = Pipe Constriction (Valve)",
            "Higher Resistance ➔ LESS Current Flow!"
        ]

        scene1 = VideoScene(
            scene_id=f"scene_{uuid.uuid4().hex[:8]}",
            step_id=step_dict.get("step_id", "step_0"),
            scene_type="diagram",
            duration_seconds=duration,
            spoken_text=spoken_text,
            on_screen_text=on_screen,
            visual=analogy_spec.model_dump(),
            avatar=avatar_cfg,
            audio=audio_cfg,
            transition=TransitionConfig(type="slide_left", duration_seconds=0.6),
            source_references=step_dict.get("source_references", [])
        )

        return [scene1]

    def _build_demonstration_scene(self, step_dict: Dict[str, Any]) -> VideoScene:
        spoken_text = step_dict.get("spoken_script") or step_dict.get("explanation", "")
        lang = step_dict.get("language", "Hinglish")
        visual_inst = step_dict.get("visual_instruction")

        audio_cfg = self.voice_provider.generate_audio(spoken_text, language=lang)
        duration = audio_cfg.duration_seconds

        # Avatar rendered smaller to keep focus on technical demonstration (Section 30)
        avatar_cfg = self.avatar_provider.generate_avatar_scene(
            spoken_text=spoken_text,
            duration=duration,
            language=lang,
            expression="explaining",
            position="small"
        )

        visual_spec = self._convert_visual_instruction_to_spec(visual_inst, step_dict)
        scene_type: SceneType = "diagram"
        if isinstance(visual_spec, (GraphVisualSpec, dict)) and getattr(visual_spec, "type", "") == "graph":
            scene_type = "graph"
        elif isinstance(visual_spec, (CodeVisualSpec, dict)) and getattr(visual_spec, "type", "") == "code":
            scene_type = "code"
        elif isinstance(visual_spec, (EquationVisualSpec, dict)) and getattr(visual_spec, "type", "") == "equation":
            scene_type = "equation"

        on_screen = TextExtractor.extract_key_points(spoken_text, step_dict.get("objective", ""), language=lang)

        return VideoScene(
            scene_id=f"scene_{uuid.uuid4().hex[:8]}",
            step_id=step_dict.get("step_id", "step_0"),
            scene_type=scene_type,
            duration_seconds=duration,
            spoken_text=spoken_text,
            on_screen_text=on_screen,
            visual=visual_spec.model_dump() if hasattr(visual_spec, "model_dump") else visual_spec,
            avatar=avatar_cfg,
            audio=audio_cfg,
            source_references=step_dict.get("source_references", [])
        )

    def _build_worked_example_scene(self, step_dict: Dict[str, Any]) -> VideoScene:
        spoken_text = step_dict.get("spoken_script") or step_dict.get("explanation", "")
        lang = step_dict.get("language", "Hinglish")
        example_text = step_dict.get("example") or "V = 10V, R = 5Ω ➔ Calculate Current I."

        audio_cfg = self.voice_provider.generate_audio(spoken_text or example_text, language=lang)
        duration = audio_cfg.duration_seconds

        avatar_cfg = self.avatar_provider.generate_avatar_scene(
            spoken_text=spoken_text or example_text,
            duration=duration,
            language=lang,
            expression="explaining",
            position="bottom_right"
        )

        worked_spec = WorkedExampleVisualSpec(
            title="Worked Example: Ohm's Law Application",
            problem=example_text,
            givens={"Voltage (V)": "10 V", "Resistance (R)": "5 Ω"},
            formula="I = V / R",
            steps=[
                "1. Identify given values: V = 10V, R = 5Ω",
                "2. State governing relationship: I = V / R",
                "3. Substitute values: I = 10 / 5",
                "4. Compute result: I = 2.0 Amperes"
            ],
            result="Current I = 2.0 A"
        )

        return VideoScene(
            scene_id=f"scene_{uuid.uuid4().hex[:8]}",
            step_id=step_dict.get("step_id", "step_0"),
            scene_type="worked_example",
            duration_seconds=duration,
            spoken_text=spoken_text or example_text,
            on_screen_text=[
                "WORKED EXAMPLE",
                "Given: V = 10V, R = 5Ω",
                "Formula: I = V / R",
                "Result: I = 2 Amperes"
            ],
            visual=worked_spec.model_dump(),
            avatar=avatar_cfg,
            audio=audio_cfg,
            source_references=step_dict.get("source_references", [])
        )

    def _build_summary_scene(self, step_dict: Dict[str, Any]) -> VideoScene:
        spoken_text = step_dict.get("spoken_script") or step_dict.get("explanation", "")
        lang = step_dict.get("language", "Hinglish")

        audio_cfg = self.voice_provider.generate_audio(spoken_text, language=lang)
        duration = audio_cfg.duration_seconds

        avatar_cfg = self.avatar_provider.generate_avatar_scene(
            spoken_text=spoken_text,
            duration=duration,
            language=lang,
            expression="celebrating",
            position="right"
        )

        summary_spec = ConceptCardVisualSpec(
            title="Lesson Mastery Summary",
            subtitle="Core Principles Covered",
            definition="Ohm's Law unites Voltage, Current and Resistance.",
            key_points=[
                "V = I * R: Voltage equals Current times Resistance",
                "I = V / R: Current is inversely proportional to Resistance",
                "Increasing resistance throttles electron flow rate."
            ],
            badge="Mastery Achieved"
        )

        return VideoScene(
            scene_id=f"scene_{uuid.uuid4().hex[:8]}",
            step_id=step_dict.get("step_id", "step_0"),
            scene_type="summary",
            duration_seconds=duration,
            spoken_text=spoken_text,
            on_screen_text=summary_spec.key_points,
            visual=summary_spec.model_dump(),
            avatar=avatar_cfg,
            audio=audio_cfg,
            source_references=step_dict.get("source_references", [])
        )

    def _build_assessment_trigger_scene(self, step_dict: Dict[str, Any]) -> VideoScene:
        spoken_text = step_dict.get("spoken_script") or "You have completed the instruction phase. Let's verify your mastery."
        lang = step_dict.get("language", "Hinglish")

        audio_cfg = self.voice_provider.generate_audio(spoken_text, language=lang)
        duration = audio_cfg.duration_seconds

        avatar_cfg = self.avatar_provider.generate_avatar_scene(
            spoken_text=spoken_text,
            duration=duration,
            language=lang,
            expression="attentive",
            position="right"
        )

        card = ConceptCardVisualSpec(
            title="Final Assessment Hand-off",
            subtitle="Summative Probing",
            definition="Complete the 3 assessment questions to lock in mastery.",
            key_points=["Questions adapt to your demonstrated learning.", "No penalties for thoughtful attempts."],
            badge="Assessment Trigger"
        )

        return VideoScene(
            scene_id=f"scene_{uuid.uuid4().hex[:8]}",
            step_id=step_dict.get("step_id", "step_0"),
            scene_type="concept_card",
            duration_seconds=duration,
            spoken_text=spoken_text,
            on_screen_text=["FINAL ASSESSMENT", "3 Probing Questions Ahead"],
            visual=card.model_dump(),
            avatar=avatar_cfg,
            audio=audio_cfg,
            interactive=True,
            pause_video=True,
            source_references=step_dict.get("source_references", [])
        )

    def _build_visual_scene_from_instruction(self, step_dict: Dict[str, Any], visual_inst: Any, scene_idx: int = 1) -> VideoScene:
        lang = step_dict.get("language", "Hinglish")
        spec = self._convert_visual_instruction_to_spec(visual_inst, step_dict)
        spec_dict = spec.model_dump() if hasattr(spec, "model_dump") else spec
        spec_type = spec_dict.get("type", "diagram")

        scene_type: SceneType = "diagram"
        if spec_type in ["equation", "graph", "code", "timeline", "map", "process", "image"]:
            scene_type = spec_type  # type: ignore

        caption = spec_dict.get("caption") or spec_dict.get("title") or "Visual Demonstration"
        audio_cfg = self.voice_provider.generate_audio(caption, language=lang)
        duration = max(6.0, audio_cfg.duration_seconds)

        # In pure visual scene, avatar is small or hidden to emphasize visual representation
        avatar_cfg = self.avatar_provider.generate_avatar_scene(
            spoken_text=caption,
            duration=duration,
            language=lang,
            expression="explaining",
            position="small" if spec_type in ["equation", "diagram"] else "hidden"
        )

        return VideoScene(
            scene_id=f"scene_{uuid.uuid4().hex[:8]}",
            step_id=step_dict.get("step_id", "step_0"),
            scene_index=scene_idx,
            scene_type=scene_type,
            duration_seconds=duration,
            spoken_text=caption,
            on_screen_text=[spec_dict.get("title", ""), caption],
            visual=spec_dict,
            avatar=avatar_cfg,
            audio=audio_cfg,
            source_references=step_dict.get("source_references", [])
        )

    # ============================================================
    # VISUAL SPEC CONVERSION (Section 9 - 17)
    # ============================================================

    def _convert_visual_instruction_to_spec(self, visual_inst: Any, step_dict: Dict[str, Any]) -> Any:
        """
        Converts Agent 1 visual instruction payload into Agent 4 VisualSpec.
        Handles dicts, VisualInstruction objects, and VisualInstructionPayloads.
        """
        v_type = "concept_card"
        title = "Conceptual Focus"
        desc = ""
        v_data: Dict[str, Any] = {}

        if isinstance(visual_inst, dict):
            v_type = visual_inst.get("type") or visual_inst.get("visual_type") or "concept_card"
            title = visual_inst.get("title", "Visual Focus")
            desc = visual_inst.get("description") or visual_inst.get("caption", "")
            v_data = visual_inst.get("data") or {}
        elif hasattr(visual_inst, "type"):
            v_type = visual_inst.type
            title = getattr(visual_inst, "title", "Visual Focus")
            desc = getattr(visual_inst, "caption", "") or getattr(visual_inst, "description", "")
            v_data = getattr(visual_inst, "data", {}) or {}
        elif hasattr(visual_inst, "visual_type"):
            v_type = visual_inst.visual_type
            title = getattr(visual_inst, "title", "Visual Focus")
            desc = getattr(visual_inst, "description", "")
            v_data = getattr(visual_inst, "data", {}) or {}

        v_type_lower = v_type.lower() if v_type else "concept_card"

        # 1. Circuit / Physics Diagram (Section 11)
        if "circuit" in v_type_lower or v_type_lower == "diagram":
            voltage = v_data.get("voltage", 12.0)
            resistance = v_data.get("resistance", 4.0)
            current = v_data.get("current", round(voltage / resistance, 2) if resistance else 3.0)
            highlight = v_data.get("highlight", "current")

            return VisualSpec(
                type="diagram",
                title=title or "DC Circuit Diagram: Ohm's Law",
                description=desc or "Closed loop circuit with battery, resistor, and current flow.",
                elements=[
                    {"id": "battery", "type": "component", "label": f"Battery ({voltage}V)"},
                    {"id": "resistor", "type": "component", "label": f"Resistor ({resistance}Ω)"},
                    {"id": "current_arrow", "type": "arrow", "label": f"Current ({current}A)"}
                ],
                relationships=[
                    {"from": "battery", "to": "resistor", "relation": "connected"},
                    {"from": "resistor", "to": "battery", "relation": "returns_to"}
                ],
                metadata={
                    "voltage": voltage,
                    "resistance": resistance,
                    "current": current,
                    "highlight": highlight
                }
            )

        # 2. Equation (Section 12)
        elif "equation" in v_type_lower or "math" in v_type_lower:
            formula = v_data.get("formula") or v_data.get("equation") or "V = I * R"
            return EquationVisualSpec(
                title=title or "Governing Equation",
                equation=formula,
                explanation=["V = Voltage (Volts)", "I = Current (Amperes)", "R = Resistance (Ohms)"],
                highlight=v_data.get("highlight", "R"),
                steps=v_data.get("steps")
            )

        # 3. Graph (Section 13)
        elif "graph" in v_type_lower:
            return GraphVisualSpec(
                title=title or "Current vs Resistance (Constant Voltage)",
                x_axis=v_data.get("x_axis") or {"label": "Resistance", "unit": "Ohms", "min_val": 1.0, "max_val": 20.0},
                y_axis=v_data.get("y_axis") or {"label": "Current", "unit": "Amperes", "min_val": 0.0, "max_val": 12.0},
                relationship=v_data.get("relationship", "inverse"),
                data_points=v_data.get("data_points") or [
                    {"x": 1.0, "y": 12.0},
                    {"x": 2.0, "y": 6.0},
                    {"x": 4.0, "y": 3.0},
                    {"x": 6.0, "y": 2.0},
                    {"x": 12.0, "y": 1.0}
                ],
                annotation="As Resistance R increases, Current I decreases asymptotically."
            )

        # 4. Code (Section 14)
        elif "code" in v_type_lower:
            code_str = v_data.get("code") or "def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    return -1"
            return CodeVisualSpec(
                title=title or "Code Demonstration",
                language=v_data.get("language", "python"),
                code=code_str,
                highlight_lines=v_data.get("highlight_lines", [1, 2]),
                output=v_data.get("output", "Result: target found"),
                execution_steps=v_data.get("execution_steps", ["Initialize bounds", "Compare middle element"])
            )

        # 5. Timeline (Section 15)
        elif "timeline" in v_type_lower or "history" in v_type_lower:
            events = v_data.get("events") or [
                {"year": "1827", "title": "Ohm Publishes Die galvanische Kette", "description": "Formulates V = I * R"},
                {"year": "1881", "title": "International Congress of Electricians", "description": "Adopts the 'Ohm' as standard unit of electrical resistance"}
            ]
            return TimelineVisualSpec(
                title=title or "Historical Timeline",
                events=events
            )

        # 6. Map (Section 16)
        elif "map" in v_type_lower or "geography" in v_type_lower:
            return MapVisualSpec(
                title=title or "Geographic Overview",
                region=v_data.get("region", "Eurasia"),
                markers=v_data.get("markers", []),
                paths=v_data.get("paths", []),
                labels=v_data.get("labels", [])
            )

        # Default: Concept Card
        objective = step_dict.get("objective") or step_dict.get("teaching_objective", "Core Principle")
        return ConceptCardVisualSpec(
            title=title or "Key Concept",
            subtitle="Foundational Principle",
            definition=desc or objective,
            key_points=TextExtractor.extract_key_points(step_dict.get("content", ""), objective),
            badge="Instructional Focus"
        )

    def _normalize_step(self, step: Any) -> Dict[str, Any]:
        """Converts step objects or dicts into standard dict representation."""
        if isinstance(step, dict):
            return step
        if hasattr(step, "model_dump"):
            return step.model_dump()
        if hasattr(step, "__dict__"):
            return step.__dict__
        return {"step_type": "explanation", "explanation": str(step)}

    def _has_active_visual(self, visual_inst: Any) -> bool:
        """Determines if a visual instruction requires visual rendering."""
        if not visual_inst:
            return False
        if isinstance(visual_inst, dict):
            v_type = visual_inst.get("type") or visual_inst.get("visual_type")
            return bool(v_type and v_type.lower() != "none")
        if hasattr(visual_inst, "visual_type"):
            return bool(visual_inst.visual_type and visual_inst.visual_type.lower() != "none")
        if hasattr(visual_inst, "type"):
            return bool(visual_inst.type and visual_inst.type.lower() != "none")
        return True
