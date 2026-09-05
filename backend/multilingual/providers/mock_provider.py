"""
Deterministic Mock Translation and Adaptation Provider.
Ensures zero-cost, fully offline testability, deterministic output,
and instant fallback for hackathon and CI environments.
Conforms to Sections 24, 45, 46, 47, 48, 49, 50, 51.
"""

import re
from typing import Dict, Any, Optional, List
from backend.multilingual.providers.base import TranslationProvider
from backend.multilingual.models.language import normalize_language_code

class MockTranslationProvider(TranslationProvider):
    """
    Deterministic pedagogical adaptation provider.
    Provides precise, tested educational adaptations for core curriculum scenarios
    (Ohm's Law, Machine Learning, Binary Search, Code Execution) and robust pattern-based
    educational adaptations for arbitrary STEM content.
    """

    # Direct canonical phrase adaptations
    KNOWN_EXACT_MAP = {
        # Ohm's Law canonical statements
        "If voltage remains constant and resistance increases, current decreases.": {
            "hi": "यदि voltage constant रहे और resistance बढ़ता है, तो current घटता है। (I = V / R)",
            "hi-en": "Agar voltage constant rahe aur resistance badhta hai, toh current decrease hota hai (I = V / R).",
            "en": "If voltage remains constant and resistance increases, current decreases."
        },
        "Voltage is the potential difference between two points.": {
            "hi": "Voltage को दो बिंदुओं के बीच potential difference के रूप में समझा जा सकता है।",
            "hi-en": "Voltage ko do points ke beech potential difference ke roop mein samajh sakte hain.",
            "en": "Voltage is the potential difference between two points."
        },
        "The resistance opposes current flow.": {
            "hi": "Resistance विद्युत धारा (current) के प्रवाह का विरोध करता है।",
            "hi-en": "Resistance current ke flow ko oppose karta hai.",
            "en": "The resistance opposes current flow."
        },
        "According to Ohm's law, V = IR.": {
            "hi": "Ohm's law के अनुसार, V = IR होता है।",
            "hi-en": "Ohm's law ke according, V = IR hota hai.",
            "en": "According to Ohm's law, V = IR."
        },

        # Questions
        "If resistance increases at constant voltage, what happens to current?": {
            "hi": "अगर voltage constant रहे और resistance बढ़ जाए, तो current पर क्या प्रभाव पड़ेगा?",
            "hi-en": "Agar resistance increase ho aur voltage constant rahe, toh current ka kya hoga?",
            "en": "If resistance increases at constant voltage, what happens to current?"
        },
        "If voltage remains constant and resistance increases, what happens to current?": {
            "hi": "यदि voltage स्थिर रहे और resistance बढ़े, तो current पर क्या असर पड़ेगा?",
            "hi-en": "Agar voltage constant rahe aur resistance increase ho, toh current par kya effect padega?",
            "en": "If voltage remains constant and resistance increases, what happens to current?"
        },
        "What happens to current when resistance increases at constant voltage?": {
            "hi": "अगर voltage constant है और resistance increase होता है, तो current पर क्या effect पड़ेगा?",
            "hi-en": "Agar resistance badhta hai aur voltage constant hai, toh current ka kya hoga?",
            "en": "What happens to current when resistance increases at constant voltage?"
        },
        "What is resistance?": {
            "hi": "Resistance क्या होता है?",
            "hi-en": "Resistance ko kaise define karenge?",
            "en": "What is resistance?"
        },

        # Machine Learning
        "Gradient descent updates model parameters to minimize the loss function.": {
            "hi": "Gradient descent मॉडल parameters को अपडेट करता है ताकि loss function न्यूनतम हो सके।",
            "hi-en": "Gradient descent model parameters ko update karta hai taaki loss function minimize ho sake.",
            "en": "Gradient descent updates model parameters to minimize the loss function."
        },

        # Binary Search / Algorithms
        "Binary search divides the search space in half at each step.": {
            "hi": "Binary search प्रत्येक चरण में search space को आधा कर देता है।",
            "hi-en": "Binary search har step par search space ko half kar deta hai.",
            "en": "Binary search divides the search space in half at each step."
        }
    }

    # Reverse lookup for Hindi -> English translation
    REVERSE_HINDI_MAP = {
        "अगर resistance बढ़ता है और voltage constant है, तो current क्या होगा?": "If resistance increases at constant voltage, what happens to current?",
        "resistance kya hota hai?": "What is resistance?",
        "current decrease hoga.": "Current decreases.",
        "current kam hoga.": "Current decreases.",
        "voltage ko do points ke beech potential difference ke roop mein samajh sakte hain.": "Voltage can be understood as the potential difference between two points."
    }

    def _extract_and_mask_code(self, text: str) -> tuple[str, dict[str, str]]:
        code_map = {}
        counter = 0
        def repl(match):
            nonlocal counter
            tag = f"__CODE_BLOCK_{counter}__"
            code_map[tag] = match.group(0)
            counter += 1
            return tag
        masked = re.sub(r"```[a-zA-Z0-9_\-]*\n.*?```", repl, text, flags=re.DOTALL)
        return masked, code_map

    def _unmask_code(self, text: str, code_map: dict[str, str]) -> str:
        for tag, code in code_map.items():
            text = text.replace(tag, code)
        return text

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[Dict[str, Any]] = None,
        terminology: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        src = normalize_language_code(source_language)
        tgt = normalize_language_code(target_language)

        # Same language requested -> immediate return
        if src == tgt:
            return {
                "translated_text": text,
                "source_language": src,
                "target_language": tgt,
                "preserved_terms": terminology or []
            }

        # Check reverse map (e.g. Hindi/Hinglish -> English)
        if tgt == "en":
            for hindi_k, eng_v in self.REVERSE_HINDI_MAP.items():
                if hindi_k.lower() in text.lower().strip():
                    return {
                        "translated_text": eng_v,
                        "source_language": src,
                        "target_language": tgt,
                        "preserved_terms": terminology or []
                    }

        # Mask code blocks so they are never altered
        masked_text, code_map = self._extract_and_mask_code(text)

        # Check exact canonical map
        clean_text = masked_text.strip()
        if clean_text in self.KNOWN_EXACT_MAP and tgt in self.KNOWN_EXACT_MAP[clean_text]:
            res = self.KNOWN_EXACT_MAP[clean_text][tgt]
            res = self._unmask_code(res, code_map)
            return {
                "translated_text": res,
                "source_language": src,
                "target_language": tgt,
                "preserved_terms": terminology or []
            }

        # Substring / sentence-level match check
        adapted = masked_text
        for k, v in self.KNOWN_EXACT_MAP.items():
            if k in adapted and tgt in v:
                adapted = adapted.replace(k, v[tgt])

        # If unchanged and we're translating to Hindi / Hinglish, apply robust pattern substitutions
        if adapted == masked_text:
            if tgt == "hi-en":
                adapted = self._pattern_adapt_hinglish(masked_text)
            elif tgt == "hi":
                adapted = self._pattern_adapt_hindi(masked_text)
            elif tgt == "en":
                adapted = masked_text

        # Restore code blocks
        final_text = self._unmask_code(adapted, code_map)

        return {
            "translated_text": final_text,
            "source_language": src,
            "target_language": tgt,
            "preserved_terms": terminology or []
        }

    def _pattern_adapt_hinglish(self, text: str) -> str:
        res = text
        # Common educational patterns preserving formulas and technical terms
        subs = [
            (r"Using\s+([A-Za-z\s=*_+\-/^]+),\s*calculate\s+current\s+when\s+(.*?)\.", r"\1 ka use karke, current calculate kijiye jab \2 ho."),
            (r"Run this Python function:\s*", r"Is Python function ko run kijiye:\n"),
            (r"Run this code:\s*", r"Is code ko run kijiye:\n"),
            (r"Let's explore\s+(.*?)\.", r"Aayiye \1 ko detail mein samajhte hain."),
            (r"In this step, we will discuss\s+(.*?)\.", r"Is step mein hum \1 ke baare mein discuss karenge."),
            (r"Notice how\s+(.*?)\.", r"Dhyan se dekhiye ki kaise \1 hota hai."),
            (r"As you can see,\s*", r"Jaisa ki aap dekh sakte hain, "),
            (r"For example,\s*", r"Example ke liye, "),
            (r"This means that\s*", r"Iska matlab ye hai ki "),
            (r"increases", r"increase hota hai"),
            (r"decreases", r"decrease hota hai"),
            (r"remains constant", r"constant rehta hai"),
        ]
        for pat, repl in subs:
            res = re.sub(pat, repl, res, flags=re.IGNORECASE)
        return res

    def _pattern_adapt_hindi(self, text: str) -> str:
        res = text
        subs = [
            (r"Using\s+([A-Za-z\s=*_+\-/^]+),\s*calculate\s+current\s+when\s+(.*?)\.", r"\1 का उपयोग करके, current की गणना करें जब \2 हो।"),
            (r"Run this Python function:\s*", r"इस Python फ़ंक्शन को चलाएं:\n"),
            (r"Run this code:\s*", r"इस कोड को चलाएं:\n"),
            (r"Let's explore\s+(.*?)\.", r"आइए \1 को समझते हैं।"),
            (r"In this step, we will discuss\s+(.*?)\.", r"इस चरण में हम \1 पर चर्चा करेंगे।"),
            (r"For example,\s*", r"उदाहरण के लिए, "),
            (r"increases", r"बढ़ता है"),
            (r"decreases", r"घटता है"),
            (r"remains constant", r"स्थिर रहता है"),
        ]
        for pat, repl in subs:
            res = re.sub(pat, repl, res, flags=re.IGNORECASE)
        return res

    def adapt_teaching_step(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        topic: Optional[str] = None,
        concept_id: Optional[str] = None,
        learner_level: str = "beginner",
        teaching_style: str = "analogy_driven",
        terminology: Optional[List[str]] = None,
        example: Optional[str] = None
    ) -> Dict[str, Any]:
        translation_res = self.translate(
            text=source_text,
            source_language=source_language,
            target_language=target_language,
            terminology=terminology
        )
        spoken = translation_res["translated_text"]
        
        # Display text preserves formulas and code as display representation
        display = source_text if ("```" in source_text or "=" in source_text) else spoken

        adapted_example = None
        if example:
            ex_res = self.translate(
                text=example,
                source_language=source_language,
                target_language=target_language,
                terminology=terminology
            )
            adapted_example = ex_res["translated_text"]

        return {
            "spoken_text": spoken,
            "display_text": display,
            "example": adapted_example,
            "preserved_terms": translation_res.get("preserved_terms", []),
            "notes": f"Deterministic mock adaptation to {target_language} ({teaching_style})"
        }
