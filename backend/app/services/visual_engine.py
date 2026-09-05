"""
Visual Engine Subsystem
Produces subject-aware visual instructions and payloads:
- Physics: Interactive circuit diagrams, current flow simulation
- Mathematics: Step-by-step KaTeX equations
- Programming: Code blocks with step tracers
- Biology/General: Concept maps and labeled diagrams
"""

from typing import Dict, Any, Optional
from backend.app.core.models import VisualInstruction

class VisualEngine:
    @staticmethod
    def generate_circuit_visual(v: float = 12.0, r: float = 4.0, highlight: str = "current") -> VisualInstruction:
        i = round(v / r, 2) if r > 0 else 0.0
        return VisualInstruction(
            type="circuit",
            title="Interactive DC Circuit: Ohm's Law in Action",
            caption=f"Voltage (V) = {v}V, Resistance (R) = {r}Ω ➔ Resulting Current (I) = {i}A",
            data={
                "voltage": v,
                "resistance": r,
                "current": i,
                "formula": "I = V / R",
                "highlight": highlight,
                "electron_speed": min(10.0, max(0.5, i * 1.5)),
                "analogy": "Water Pipe: Voltage is water pressure; Resistance is pipe constriction; Current is flow rate."
            }
        )

    @staticmethod
    def generate_math_visual(steps: list[dict], active_step: int = 0) -> VisualInstruction:
        return VisualInstruction(
            type="math_derivation",
            title="Mathematical Derivation & Formula Relationships",
            caption="Step-by-step algebraic breakdown",
            data={
                "steps": steps,
                "active_step": active_step
            }
        )

    @staticmethod
    def generate_code_visual(code: str, language: str, trace_state: dict) -> VisualInstruction:
        return VisualInstruction(
            type="code_trace",
            title="Algorithm Execution & Variable State Trace",
            caption="Real-time execution pointers and state",
            data={
                "code": code,
                "language": language,
                "trace_state": trace_state
            }
        )

    @staticmethod
    def generate_concept_map_visual(concepts: list[str], active_concept: str, dependencies: dict) -> VisualInstruction:
        return VisualInstruction(
            type="concept_map",
            title="Curriculum Knowledge Graph & Prerequisites",
            caption=f"Current focus: {active_concept}",
            data={
                "concepts": concepts,
                "active_concept": active_concept,
                "dependencies": dependencies
            }
        )

    @staticmethod
    def for_topic(topic: str, concept: str, context: Optional[dict] = None) -> VisualInstruction:
        topic_lower = topic.lower()
        concept_lower = concept.lower()

        if "ohm" in topic_lower or "circuit" in topic_lower or "current" in topic_lower or "resistance" in topic_lower:
            r_val = 4.0
            if context and context.get("increased_resistance"):
                r_val = 12.0
            return VisualEngine.generate_circuit_visual(v=12.0, r=r_val, highlight="resistance" if r_val > 4 else "current")
        
        elif "binary search" in topic_lower or "algorithm" in topic_lower or "code" in topic_lower:
            code_sample = (
                "def binary_search(arr, target):\n"
                "    low = 0\n"
                "    high = len(arr) - 1\n"
                "    while low <= high:\n"
                "        mid = (low + high) // 2\n"
                "        if arr[mid] == target:\n"
                "            return mid\n"
                "        elif arr[mid] < target:\n"
                "            low = mid + 1\n"
                "        else:\n"
                "            high = mid - 1\n"
                "    return -1"
            )
            return VisualEngine.generate_code_visual(
                code=code_sample,
                language="python",
                trace_state={"low": 0, "mid": 4, "high": 9, "target": 23, "arr": [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]}
            )
        
        else:
            steps = [
                {"latex": "V = I \\cdot R", "explanation": "Standard definition: Voltage equals Current times Resistance"},
                {"latex": "I = \\frac{V}{R}", "explanation": "Rearranging for Current: Current is inversely proportional to Resistance"},
                {"latex": "R \\uparrow \\implies I \\downarrow", "explanation": "If Resistance increases with constant Voltage, Current must decrease!"}
            ]
            return VisualEngine.generate_math_visual(steps=steps, active_step=1)

visual_engine = VisualEngine()
