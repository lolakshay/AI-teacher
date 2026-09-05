"""
Terminology Management and Domain Glossary Service.
Provides curated educational glossaries and placeholder protection
to prevent technical terms from being mangled during translation.
Conforms to Sections 11, 12, 15.
"""

import re
from typing import Dict, List, Optional, Tuple
from backend.multilingual.models.terminology import TerminologyEntry, DisplayPolicy

class TerminologyService:
    def __init__(self):
        self._glossary: Dict[str, TerminologyEntry] = {}
        self._init_curated_glossaries()

    def _init_curated_glossaries(self):
        entries = [
            # Physics & Circuits
            TerminologyEntry(
                source_term="resistance",
                preferred_term="resistance",
                localized_term="प्रतिरोध",
                display_policy="preserve_original",
                domain="physics",
                pronunciation_hint="ri-ZIS-tuhns",
                context_hint="Opposition to electric charge flow"
            ),
            TerminologyEntry(
                source_term="voltage",
                preferred_term="voltage",
                localized_term="विभवांतर",
                display_policy="preserve_original",
                domain="physics",
                pronunciation_hint="VOL-tij",
                context_hint="Electrical potential difference"
            ),
            TerminologyEntry(
                source_term="current",
                preferred_term="current",
                localized_term="विद्युत धारा",
                display_policy="preserve_original",
                domain="physics",
                pronunciation_hint="KUR-uhnt",
                context_hint="Flow of electric charge per second"
            ),
            TerminologyEntry(
                source_term="Ohm's law",
                preferred_term="Ohm's law",
                localized_term="ओम का नियम",
                display_policy="preserve_original",
                domain="physics",
                context_hint="Governs relationship V = IR"
            ),
            TerminologyEntry(
                source_term="potential difference",
                preferred_term="potential difference",
                localized_term="विभवांतर",
                display_policy="preserve_original",
                domain="physics"
            ),
            TerminologyEntry(
                source_term="resistor",
                preferred_term="resistor",
                localized_term="प्रतिरोधक",
                display_policy="preserve_original",
                domain="physics"
            ),

            # Machine Learning
            TerminologyEntry(
                source_term="gradient descent",
                preferred_term="gradient descent",
                localized_term="ग्रेडिएंट डिसेंट",
                display_policy="preserve_original",
                domain="ml",
                pronunciation_hint="GRAY-dee-uhnt dih-SENT",
                context_hint="Optimization algorithm iteratively minimizing loss"
            ),
            TerminologyEntry(
                source_term="loss function",
                preferred_term="loss function",
                localized_term="हानि फलन",
                display_policy="preserve_original",
                domain="ml",
                context_hint="Measures discrepancy between predicted and ground-truth values"
            ),
            TerminologyEntry(
                source_term="neural network",
                preferred_term="neural network",
                localized_term="तंत्रिका नेटवर्क",
                display_policy="preserve_original",
                domain="ml"
            ),
            TerminologyEntry(
                source_term="backpropagation",
                preferred_term="backpropagation",
                localized_term="बैकप्रॉपैगैशन",
                display_policy="preserve_original",
                domain="ml"
            ),
            TerminologyEntry(
                source_term="learning rate",
                preferred_term="learning rate",
                localized_term="लर्निंग रेट",
                display_policy="preserve_original",
                domain="ml"
            ),

            # Computer Science / Algorithms
            TerminologyEntry(
                source_term="binary search",
                preferred_term="binary search",
                localized_term="बाइनरी सर्च",
                display_policy="preserve_original",
                domain="programming",
                context_hint="Logarithmic search in sorted collections"
            ),
            TerminologyEntry(
                source_term="time complexity",
                preferred_term="time complexity",
                localized_term="समय जटिलता",
                display_policy="preserve_original",
                domain="programming"
            ),
            TerminologyEntry(
                source_term="pointer",
                preferred_term="pointer",
                localized_term="पॉइंटर",
                display_policy="preserve_original",
                domain="programming"
            ),
            TerminologyEntry(
                source_term="recursion",
                preferred_term="recursion",
                localized_term="रिकर्शन",
                display_policy="preserve_original",
                domain="programming"
            ),

            # General STEM / Mathematics
            TerminologyEntry(
                source_term="inverse relationship",
                preferred_term="inverse relationship",
                localized_term="व्युत्क्रमानुपाती संबंध",
                display_policy="preserve_original",
                domain="physics"
            ),
            TerminologyEntry(
                source_term="direct proportionality",
                preferred_term="direct proportionality",
                localized_term="समानुपाती संबंध",
                display_policy="preserve_original",
                domain="physics"
            ),
        ]

        for entry in entries:
            self.add_term(entry)

    def add_term(self, entry: TerminologyEntry):
        self._glossary[entry.source_term.lower()] = entry

    def get_term(self, term: str) -> Optional[TerminologyEntry]:
        return self._glossary.get(term.strip().lower())

    def detect_terms(self, text: str, domain: Optional[str] = None) -> List[TerminologyEntry]:
        """Detects known technical terms present in the text."""
        detected = []
        text_lower = text.lower()
        for term_key, entry in self._glossary.items():
            if domain and entry.domain != domain and entry.domain != "general":
                continue
            # Match whole words / phrases using boundary check
            pattern = rf"\b{re.escape(term_key)}\b"
            if re.search(pattern, text_lower):
                detected.append(entry)
        return detected

    def protect_terms_for_translation(
        self,
        text: str,
        terms_to_protect: Optional[List[str]] = None,
        target_lang: str = "hi"
    ) -> Tuple[str, Dict[str, str]]:
        """
        Replaces sensitive terms with protected placeholders (e.g. __TECH_TERM_0__)
        so that translation models or services do not alter them.
        Returns (protected_text, placeholder_map).
        """
        placeholder_map: Dict[str, str] = {}
        counter = 0
        protected_text = text

        terms = terms_to_protect or []
        # Auto-detect any known terms if not explicitly specified
        detected = self.detect_terms(text)
        all_terms = set(terms + [d.source_term for d in detected])

        # Sort longer phrases first so substrings aren't replaced prematurely
        sorted_terms = sorted(all_terms, key=len, reverse=True)

        for term in sorted_terms:
            entry = self.get_term(term)
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            
            def repl(match):
                nonlocal counter
                matched_text = match.group(0)
                placeholder = f"__TECH_TERM_{counter}__"
                counter += 1
                if entry:
                    if entry.display_policy in ("preserve_original", "original_only"):
                        placeholder_map[placeholder] = matched_text
                    elif entry.display_policy == "bilingual":
                        if entry.localized_term and entry.localized_term.lower() != matched_text.lower():
                            placeholder_map[placeholder] = f"{matched_text} ({entry.localized_term})"
                        else:
                            placeholder_map[placeholder] = matched_text
                    else:
                        placeholder_map[placeholder] = entry.render_for_language(target_lang)
                else:
                    placeholder_map[placeholder] = matched_text
                return placeholder

            protected_text = pattern.sub(repl, protected_text)

        return protected_text, placeholder_map


    def restore_protected_terms(self, translated_text: str, placeholder_map: Dict[str, str]) -> str:
        """Restores protected placeholders with their final rendered terms."""
        restored = translated_text
        for placeholder, replacement in placeholder_map.items():
            restored = restored.replace(placeholder, replacement)
        return restored

terminology_service = TerminologyService()
