"""
Safe Persistent Student Profile Repository conforming to Sections 8, 9, 36, 37, 39, 40, 52, 53.
Provides:
- StudentProfileRepository (Abstract Base Class)
- SQLiteProfileRepository (Production Thread-Safe Relational DB with Lock & Transactions)
- InMemoryProfileRepository (High-Speed Fallback / Testing)
"""

import json
import sqlite3
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from backend.personalization.schemas import (
    StudentProfile, StudentPreferences, LearnerKnowledge,
    MisconceptionRecord, LearnerEvidence, LearningHistoryEntry,
    AssessmentHistoryEntry, CurrentLearningPath, PathNode
)


class StudentProfileRepository(ABC):
    """Abstract interface decoupling engine from concrete storage."""

    @abstractmethod
    def create_profile(self, profile: StudentProfile) -> StudentProfile:
        pass

    @abstractmethod
    def get_profile(self, student_id: str) -> Optional[StudentProfile]:
        pass

    @abstractmethod
    def update_profile(self, student_id: str, updates: Dict[str, Any]) -> Optional[StudentProfile]:
        pass

    @abstractmethod
    def delete_profile(self, student_id: str) -> bool:
        pass

    @abstractmethod
    def save_knowledge_state(self, student_id: str, knowledge: LearnerKnowledge) -> LearnerKnowledge:
        pass

    @abstractmethod
    def get_knowledge_state(self, student_id: str, concept_id: Optional[str] = None) -> Dict[str, LearnerKnowledge]:
        pass

    @abstractmethod
    def add_learning_history(self, student_id: str, entry: LearningHistoryEntry) -> LearningHistoryEntry:
        pass

    @abstractmethod
    def get_learning_history(self, student_id: str, limit: int = 10) -> List[LearningHistoryEntry]:
        pass

    @abstractmethod
    def add_assessment_history(self, student_id: str, entry: AssessmentHistoryEntry) -> AssessmentHistoryEntry:
        pass

    @abstractmethod
    def get_assessment_history(self, student_id: str, limit: int = 10) -> List[AssessmentHistoryEntry]:
        pass

    @abstractmethod
    def reset_profile(self, student_id: str, reset_type: str) -> bool:
        pass


class SQLiteProfileRepository(StudentProfileRepository):
    """
    SQLite-backed repository with thread-safe connection locking, transactional
    consistency, and partial update support.
    """

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Default to backend/data/learner_profiles.db
            backend_dir = Path(__file__).resolve().parent.parent
            data_dir = backend_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = data_dir / "learner_profiles.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self):
        with self._lock:
            with self._get_connection() as conn:
                conn.executescript("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    educational_level TEXT NOT NULL DEFAULT 'beginner',
                    preferred_language TEXT NOT NULL DEFAULT 'English',
                    preferred_teaching_style TEXT NOT NULL DEFAULT 'analogy_based',
                    preferred_depth TEXT NOT NULL DEFAULT 'standard',
                    learning_objectives TEXT NOT NULL DEFAULT '[]',
                    known_concepts TEXT NOT NULL DEFAULT '[]',
                    strong_concepts TEXT NOT NULL DEFAULT '[]',
                    weak_concepts TEXT NOT NULL DEFAULT '[]',
                    profile_schema_version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS student_preferences (
                    student_id TEXT PRIMARY KEY,
                    preferred_language TEXT NOT NULL DEFAULT 'English',
                    preferred_teaching_style TEXT NOT NULL DEFAULT 'analogy_based',
                    preferred_depth TEXT NOT NULL DEFAULT 'standard',
                    interaction_frequency TEXT NOT NULL DEFAULT 'medium',
                    example_preference TEXT NOT NULL DEFAULT 'real_world',
                    explanation_preference TEXT NOT NULL DEFAULT 'mixed',
                    typical_duration INTEGER DEFAULT 20,
                    inferred_json TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS concept_mastery (
                    student_id TEXT NOT NULL,
                    concept_id TEXT NOT NULL,
                    concept_name TEXT NOT NULL,
                    mastery_score REAL NOT NULL DEFAULT 0.0,
                    confidence REAL NOT NULL DEFAULT 0.0,
                    status TEXT NOT NULL DEFAULT 'unknown',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    correct_attempts INTEGER NOT NULL DEFAULT 0,
                    incorrect_attempts INTEGER NOT NULL DEFAULT 0,
                    last_assessed_at TEXT,
                    last_taught_at TEXT,
                    PRIMARY KEY (student_id, concept_id),
                    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS misconceptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    concept_id TEXT NOT NULL,
                    misconception TEXT NOT NULL,
                    first_detected TEXT NOT NULL,
                    last_detected TEXT NOT NULL,
                    occurrences INTEGER NOT NULL DEFAULT 1,
                    resolved INTEGER NOT NULL DEFAULT 0,
                    resolution_notes TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS learner_evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    concept_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    session_id TEXT,
                    question_id TEXT,
                    result TEXT NOT NULL,
                    score REAL NOT NULL DEFAULT 0.0,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    misconception TEXT,
                    details_json TEXT NOT NULL DEFAULT '{}',
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS learning_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    lesson_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    duration_minutes REAL NOT NULL DEFAULT 0.0,
                    concepts_covered TEXT NOT NULL DEFAULT '[]',
                    concepts_mastered TEXT NOT NULL DEFAULT '[]',
                    concepts_struggled TEXT NOT NULL DEFAULT '[]',
                    assessment_score REAL,
                    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS assessment_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    assessment_id TEXT NOT NULL,
                    lesson_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    score REAL NOT NULL DEFAULT 0.0,
                    concept_scores_json TEXT NOT NULL DEFAULT '{}',
                    weak_concepts_json TEXT NOT NULL DEFAULT '[]',
                    strong_concepts_json TEXT NOT NULL DEFAULT '[]',
                    misconceptions_json TEXT NOT NULL DEFAULT '[]',
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS learning_paths (
                    student_id TEXT PRIMARY KEY,
                    path_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    nodes_json TEXT NOT NULL DEFAULT '[]',
                    current_node TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
                );
                """)

    def create_profile(self, profile: StudentProfile) -> StudentProfile:
        with self._lock:
            existing = self.get_profile(profile.student_id)
            if existing:
                # Section 9: If profile already exists, do not overwrite historical learning data.
                # Update only explicitly supplied preferences and core parameters.
                return self.update_profile(profile.student_id, {
                    "educational_level": profile.educational_level,
                    "preferred_language": profile.preferred_language,
                    "preferred_teaching_style": profile.preferred_teaching_style,
                    "preferred_depth": profile.preferred_depth,
                    "learning_objectives": profile.learning_objectives,
                    "known_concepts": profile.known_concepts,
                    "preferences": profile.preferences.model_dump()
                })

            now_iso = datetime.now(timezone.utc).isoformat()
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO students (
                        student_id, educational_level, preferred_language,
                        preferred_teaching_style, preferred_depth,
                        learning_objectives, known_concepts, strong_concepts,
                        weak_concepts, profile_schema_version, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.student_id,
                    profile.educational_level,
                    profile.preferred_language,
                    profile.preferred_teaching_style,
                    profile.preferred_depth,
                    json.dumps(profile.learning_objectives),
                    json.dumps(profile.known_concepts),
                    json.dumps(profile.strong_concepts),
                    json.dumps(profile.weak_concepts),
                    profile.profile_schema_version,
                    profile.created_at or now_iso,
                    profile.updated_at or now_iso
                ))

                pref = profile.preferences
                conn.execute("""
                    INSERT INTO student_preferences (
                        student_id, preferred_language, preferred_teaching_style,
                        preferred_depth, interaction_frequency, example_preference,
                        explanation_preference, typical_duration, inferred_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.student_id,
                    pref.preferred_language or profile.preferred_language,
                    pref.preferred_teaching_style or profile.preferred_teaching_style,
                    pref.preferred_depth or profile.preferred_depth,
                    pref.interaction_frequency,
                    pref.example_preference,
                    pref.explanation_preference,
                    pref.typical_session_duration_minutes or 20,
                    json.dumps(profile.inferred_preferences)
                ))

                if profile.current_learning_path:
                    conn.execute("""
                        INSERT INTO learning_paths (student_id, path_id, title, nodes_json, current_node)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        profile.student_id,
                        profile.current_learning_path.path_id,
                        profile.current_learning_path.title,
                        json.dumps([n.model_dump() for n in profile.current_learning_path.nodes]),
                        profile.current_learning_path.current_node
                    ))

            # Store any initial concept mastery provided
            for k in profile.concept_mastery.values():
                self.save_knowledge_state(profile.student_id, k)

            return self.get_profile(profile.student_id)

    def get_profile(self, student_id: str) -> Optional[StudentProfile]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
                s_row = cur.fetchone()
                if not s_row:
                    return None

                cur.execute("SELECT * FROM student_preferences WHERE student_id = ?", (student_id,))
                p_row = cur.fetchone()

                cur.execute("SELECT * FROM learning_paths WHERE student_id = ?", (student_id,))
                path_row = cur.fetchone()

            # Load concept mastery
            concept_mastery = self.get_knowledge_state(student_id)

            # Load histories
            learning_history = self.get_learning_history(student_id, limit=50)
            assessment_history = self.get_assessment_history(student_id, limit=50)

            # Load preferences
            if p_row:
                preferences = StudentPreferences(
                    preferred_language=p_row["preferred_language"],
                    preferred_teaching_style=p_row["preferred_teaching_style"],
                    preferred_depth=p_row["preferred_depth"],
                    interaction_frequency=p_row["interaction_frequency"],
                    example_preference=p_row["example_preference"],
                    explanation_preference=p_row["explanation_preference"],
                    typical_session_duration_minutes=p_row["typical_duration"]
                )
                inferred = json.loads(p_row["inferred_json"]) if p_row["inferred_json"] else {}
            else:
                preferences = StudentPreferences()
                inferred = {}

            # Load learning path
            learning_path = None
            if path_row:
                nodes_data = json.loads(path_row["nodes_json"])
                learning_path = CurrentLearningPath(
                    path_id=path_row["path_id"],
                    title=path_row["title"],
                    nodes=[PathNode(**n) for n in nodes_data],
                    current_node=path_row["current_node"]
                )

            # Extract dynamic weak / strong / misconceptions from concept_mastery
            dynamic_weak: List[str] = []
            dynamic_strong: List[str] = []
            all_misconceptions: List[MisconceptionRecord] = []

            for c_id, k in concept_mastery.items():
                if k.status == "mastered":
                    dynamic_strong.append(c_id)
                elif k.status in ("weak", "misconception"):
                    dynamic_weak.append(c_id)
                for m in k.misconceptions:
                    all_misconceptions.append(m)

            static_known = json.loads(s_row["known_concepts"])
            static_weak = json.loads(s_row["weak_concepts"])
            static_strong = json.loads(s_row["strong_concepts"])

            combined_weak = list(set(static_weak + dynamic_weak))
            combined_strong = list(set(static_strong + dynamic_strong))

            return StudentProfile(
                student_id=s_row["student_id"],
                educational_level=s_row["educational_level"],
                preferred_language=preferences.preferred_language or s_row["preferred_language"],
                preferred_teaching_style=preferences.preferred_teaching_style or s_row["preferred_teaching_style"],
                preferred_depth=preferences.preferred_depth or s_row["preferred_depth"],
                learning_objectives=json.loads(s_row["learning_objectives"]),
                known_concepts=static_known,
                strong_concepts=combined_strong,
                weak_concepts=combined_weak,
                misconceptions=all_misconceptions,
                current_learning_path=learning_path,
                learning_history=learning_history,
                assessment_history=assessment_history,
                concept_mastery=concept_mastery,
                preferences=preferences,
                inferred_preferences=inferred,
                profile_schema_version=s_row["profile_schema_version"],
                created_at=s_row["created_at"],
                updated_at=s_row["updated_at"]
            )

    def update_profile(self, student_id: str, updates: Dict[str, Any]) -> Optional[StudentProfile]:
        """
        Safe partial PATCH operation (Section 39).
        Modifies only specified fields; never deletes history or concept mastery.
        """
        with self._lock:
            existing = self.get_profile(student_id)
            if not existing:
                return None

            now_iso = datetime.now(timezone.utc).isoformat()
            with self._get_connection() as conn:
                # 1. Update students table
                student_fields = {}
                for field in [
                    "educational_level", "preferred_language",
                    "preferred_teaching_style", "preferred_depth"
                ]:
                    if field in updates and updates[field] is not None:
                        student_fields[field] = updates[field]

                for list_field in ["learning_objectives", "known_concepts", "strong_concepts", "weak_concepts"]:
                    if list_field in updates and updates[list_field] is not None:
                        student_fields[list_field] = json.dumps(updates[list_field])

                if student_fields:
                    set_clause = ", ".join(f"{k} = ?" for k in student_fields.keys()) + ", updated_at = ?"
                    values = list(student_fields.values()) + [now_iso, student_id]
                    conn.execute(f"UPDATE students SET {set_clause} WHERE student_id = ?", values)

                # 2. Update preferences table
                pref_updates = updates.get("preferences", {})
                # Also reflect top-level language/style/depth in preferences
                if "preferred_language" in updates and updates["preferred_language"]:
                    pref_updates["preferred_language"] = updates["preferred_language"]
                if "preferred_teaching_style" in updates and updates["preferred_teaching_style"]:
                    pref_updates["preferred_teaching_style"] = updates["preferred_teaching_style"]
                if "preferred_depth" in updates and updates["preferred_depth"]:
                    pref_updates["preferred_depth"] = updates["preferred_depth"]

                if pref_updates:
                    p_fields = {}
                    for k in [
                        "preferred_language", "preferred_teaching_style", "preferred_depth",
                        "interaction_frequency", "example_preference", "explanation_preference",
                        "typical_duration"
                    ]:
                        if k in pref_updates and pref_updates[k] is not None:
                            p_fields[k] = pref_updates[k]

                    if p_fields:
                        set_clause = ", ".join(f"{k} = ?" for k in p_fields.keys())
                        values = list(p_fields.values()) + [student_id]
                        conn.execute(f"UPDATE student_preferences SET {set_clause} WHERE student_id = ?", values)

                # 3. Update learning path if provided
                if "current_learning_path" in updates and updates["current_learning_path"]:
                    path = updates["current_learning_path"]
                    path_id = path.get("path_id", "") if isinstance(path, dict) else path.path_id
                    title = path.get("title", "") if isinstance(path, dict) else path.title
                    nodes = path.get("nodes", []) if isinstance(path, dict) else [n.model_dump() for n in path.nodes]
                    current_node = path.get("current_node", "") if isinstance(path, dict) else path.current_node

                    conn.execute("""
                        INSERT INTO learning_paths (student_id, path_id, title, nodes_json, current_node)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(student_id) DO UPDATE SET
                            path_id = excluded.path_id,
                            title = excluded.title,
                            nodes_json = excluded.nodes_json,
                            current_node = excluded.current_node
                    """, (student_id, path_id, title, json.dumps(nodes), current_node))

            return self.get_profile(student_id)

    def delete_profile(self, student_id: str) -> bool:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                return cur.rowcount > 0

    def save_knowledge_state(self, student_id: str, knowledge: LearnerKnowledge) -> LearnerKnowledge:
        with self._lock:
            # Ensure student exists or create minimal stub
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO students (
                        student_id, educational_level, preferred_language,
                        preferred_teaching_style, preferred_depth,
                        learning_objectives, known_concepts, strong_concepts,
                        weak_concepts, profile_schema_version, created_at, updated_at
                    ) VALUES (?, 'beginner', 'English', 'analogy_based', 'standard', '[]', '[]', '[]', '[]', 1, ?, ?)
                """, (student_id, datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()))

                conn.execute("""
                    INSERT OR IGNORE INTO student_preferences (student_id) VALUES (?)
                """, (student_id,))

                # Upsert concept_mastery
                conn.execute("""
                    INSERT INTO concept_mastery (
                        student_id, concept_id, concept_name, mastery_score, confidence,
                        status, attempts, correct_attempts, incorrect_attempts,
                        last_assessed_at, last_taught_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, concept_id) DO UPDATE SET
                        concept_name = excluded.concept_name,
                        mastery_score = excluded.mastery_score,
                        confidence = excluded.confidence,
                        status = excluded.status,
                        attempts = excluded.attempts,
                        correct_attempts = excluded.correct_attempts,
                        incorrect_attempts = excluded.incorrect_attempts,
                        last_assessed_at = excluded.last_assessed_at,
                        last_taught_at = excluded.last_taught_at
                """, (
                    student_id,
                    knowledge.concept_id,
                    knowledge.concept_name,
                    knowledge.mastery_score,
                    knowledge.confidence,
                    knowledge.status,
                    knowledge.attempts,
                    knowledge.correct_attempts,
                    knowledge.incorrect_attempts,
                    knowledge.last_assessed_at,
                    knowledge.last_taught_at
                ))

                # Upsert misconceptions
                for m in knowledge.misconceptions:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT id FROM misconceptions
                        WHERE student_id = ? AND concept_id = ? AND lower(misconception) = lower(?)
                    """, (student_id, knowledge.concept_id, m.misconception))
                    row = cur.fetchone()
                    if row:
                        conn.execute("""
                            UPDATE misconceptions SET
                                last_detected = ?,
                                occurrences = ?,
                                resolved = ?,
                                resolution_notes = ?
                            WHERE id = ?
                        """, (m.last_detected, m.occurrences, 1 if m.resolved else 0, m.resolution_notes, row["id"]))
                    else:
                        conn.execute("""
                            INSERT INTO misconceptions (
                                student_id, concept_id, misconception, first_detected,
                                last_detected, occurrences, resolved, resolution_notes
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            student_id, knowledge.concept_id, m.misconception,
                            m.first_detected, m.last_detected, m.occurrences,
                            1 if m.resolved else 0, m.resolution_notes
                        ))

                # Insert latest evidence entries (only append new ones)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) as cnt FROM learner_evidence WHERE student_id = ? AND concept_id = ?",
                            (student_id, knowledge.concept_id))
                cnt = cur.fetchone()["cnt"]
                if len(knowledge.evidence) > cnt:
                    for ev in knowledge.evidence[cnt:]:
                        conn.execute("""
                            INSERT INTO learner_evidence (
                                student_id, concept_id, source, session_id, question_id,
                                result, score, confidence, misconception, details_json, timestamp
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            student_id, knowledge.concept_id, ev.source, ev.session_id,
                            ev.question_id, ev.result, ev.score, ev.confidence,
                            ev.misconception, json.dumps(ev.details), ev.timestamp
                        ))

            return knowledge

    def get_knowledge_state(self, student_id: str, concept_id: Optional[str] = None) -> Dict[str, LearnerKnowledge]:
        with self._lock:
            result: Dict[str, LearnerKnowledge] = {}
            with self._get_connection() as conn:
                cur = conn.cursor()
                if concept_id:
                    cur.execute("SELECT * FROM concept_mastery WHERE student_id = ? AND concept_id = ?",
                                (student_id, concept_id))
                else:
                    cur.execute("SELECT * FROM concept_mastery WHERE student_id = ?", (student_id,))
                rows = cur.fetchall()

                for row in rows:
                    c_id = row["concept_id"]

                    # Load misconceptions
                    cur.execute("SELECT * FROM misconceptions WHERE student_id = ? AND concept_id = ?",
                                (student_id, c_id))
                    m_rows = cur.fetchall()
                    misconceptions = [
                        MisconceptionRecord(
                            concept_id=m["concept_id"],
                            misconception=m["misconception"],
                            first_detected=m["first_detected"],
                            last_detected=m["last_detected"],
                            occurrences=m["occurrences"],
                            resolved=bool(m["resolved"]),
                            resolution_notes=m["resolution_notes"]
                        ) for m in m_rows
                    ]

                    # Load evidence
                    cur.execute("SELECT * FROM learner_evidence WHERE student_id = ? AND concept_id = ? ORDER BY id ASC",
                                (student_id, c_id))
                    e_rows = cur.fetchall()
                    evidence = [
                        LearnerEvidence(
                            source=e["source"],
                            session_id=e["session_id"],
                            question_id=e["question_id"],
                            result=e["result"],
                            score=e["score"],
                            confidence=e["confidence"],
                            misconception=e["misconception"],
                            details=json.loads(e["details_json"]),
                            timestamp=e["timestamp"]
                        ) for e in e_rows
                    ]

                    result[c_id] = LearnerKnowledge(
                        concept_id=c_id,
                        concept_name=row["concept_name"],
                        mastery_score=row["mastery_score"],
                        confidence=row["confidence"],
                        status=row["status"],
                        attempts=row["attempts"],
                        correct_attempts=row["correct_attempts"],
                        incorrect_attempts=row["incorrect_attempts"],
                        last_assessed_at=row["last_assessed_at"],
                        last_taught_at=row["last_taught_at"],
                        misconceptions=misconceptions,
                        evidence=evidence
                    )
            return result

    def add_learning_history(self, student_id: str, entry: LearningHistoryEntry) -> LearningHistoryEntry:
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO learning_history (
                        student_id, session_id, lesson_id, topic, started_at, completed_at,
                        duration_minutes, concepts_covered, concepts_mastered,
                        concepts_struggled, assessment_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_id,
                    entry.session_id,
                    entry.lesson_id,
                    entry.topic,
                    entry.started_at,
                    entry.completed_at,
                    entry.duration_minutes,
                    json.dumps(entry.concepts_covered),
                    json.dumps(entry.concepts_mastered),
                    json.dumps(entry.concepts_struggled),
                    entry.assessment_score
                ))
            return entry

    def get_learning_history(self, student_id: str, limit: int = 10) -> List[LearningHistoryEntry]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT * FROM learning_history
                    WHERE student_id = ?
                    ORDER BY id DESC LIMIT ?
                """, (student_id, limit))
                rows = cur.fetchall()
                return [
                    LearningHistoryEntry(
                        session_id=r["session_id"],
                        lesson_id=r["lesson_id"],
                        topic=r["topic"],
                        started_at=r["started_at"],
                        completed_at=r["completed_at"],
                        duration_minutes=r["duration_minutes"],
                        concepts_covered=json.loads(r["concepts_covered"]),
                        concepts_mastered=json.loads(r["concepts_mastered"]),
                        concepts_struggled=json.loads(r["concepts_struggled"]),
                        assessment_score=r["assessment_score"]
                    ) for r in rows
                ]

    def add_assessment_history(self, student_id: str, entry: AssessmentHistoryEntry) -> AssessmentHistoryEntry:
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO assessment_history (
                        student_id, assessment_id, lesson_id, topic, score,
                        concept_scores_json, weak_concepts_json,
                        strong_concepts_json, misconceptions_json, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_id,
                    entry.assessment_id,
                    entry.lesson_id,
                    entry.topic,
                    entry.score,
                    json.dumps(entry.concept_scores),
                    json.dumps(entry.weak_concepts),
                    json.dumps(entry.strong_concepts),
                    json.dumps(entry.misconceptions),
                    entry.timestamp
                ))
            return entry

    def get_assessment_history(self, student_id: str, limit: int = 10) -> List[AssessmentHistoryEntry]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT * FROM assessment_history
                    WHERE student_id = ?
                    ORDER BY id DESC LIMIT ?
                """, (student_id, limit))
                rows = cur.fetchall()
                return [
                    AssessmentHistoryEntry(
                        assessment_id=r["assessment_id"],
                        lesson_id=r["lesson_id"],
                        topic=r["topic"],
                        score=r["score"],
                        concept_scores=json.loads(r["concept_scores_json"]),
                        weak_concepts=json.loads(r["weak_concepts_json"]),
                        strong_concepts=json.loads(r["strong_concepts_json"]),
                        misconceptions=json.loads(r["misconceptions_json"]),
                        timestamp=r["timestamp"]
                    ) for r in rows
                ]

    def reset_profile(self, student_id: str, reset_type: str) -> bool:
        """
        Section 40 Granular Reset:
        - RESET_PREFERENCES
        - RESET_KNOWLEDGE
        - RESET_HISTORY
        - RESET_ALL
        """
        with self._lock:
            with self._get_connection() as conn:
                if reset_type == "RESET_PREFERENCES":
                    conn.execute("""
                        UPDATE student_preferences SET
                            preferred_language = 'English',
                            preferred_teaching_style = 'analogy_based',
                            preferred_depth = 'standard',
                            interaction_frequency = 'medium',
                            example_preference = 'real_world',
                            explanation_preference = 'mixed',
                            typical_duration = 20,
                            inferred_json = '{}'
                        WHERE student_id = ?
                    """, (student_id,))
                    conn.execute("""
                        UPDATE students SET
                            preferred_language = 'English',
                            preferred_teaching_style = 'analogy_based',
                            preferred_depth = 'standard'
                        WHERE student_id = ?
                    """, (student_id,))
                    return True

                elif reset_type == "RESET_KNOWLEDGE":
                    conn.execute("DELETE FROM concept_mastery WHERE student_id = ?", (student_id,))
                    conn.execute("DELETE FROM misconceptions WHERE student_id = ?", (student_id,))
                    conn.execute("DELETE FROM learner_evidence WHERE student_id = ?", (student_id,))
                    conn.execute("""
                        UPDATE students SET
                            known_concepts = '[]',
                            strong_concepts = '[]',
                            weak_concepts = '[]'
                        WHERE student_id = ?
                    """, (student_id,))
                    return True

                elif reset_type == "RESET_HISTORY":
                    conn.execute("DELETE FROM learning_history WHERE student_id = ?", (student_id,))
                    conn.execute("DELETE FROM assessment_history WHERE student_id = ?", (student_id,))
                    return True

                elif reset_type == "RESET_ALL":
                    conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                    return True

                return False


class InMemoryProfileRepository(StudentProfileRepository):
    """In-memory thread-safe repository for mock runs or rapid unit tests."""

    def __init__(self):
        self._lock = threading.RLock()
        self._profiles: Dict[str, StudentProfile] = {}

    def create_profile(self, profile: StudentProfile) -> StudentProfile:
        with self._lock:
            existing = self._profiles.get(profile.student_id)
            if existing:
                # Update preferences only
                existing.preferred_language = profile.preferred_language
                existing.preferences.preferred_language = profile.preferred_language
                existing.preferred_teaching_style = profile.preferred_teaching_style
                existing.preferences.preferred_teaching_style = profile.preferred_teaching_style
                existing.educational_level = profile.educational_level
                return existing.model_copy(deep=True)

            copy_prof = profile.model_copy(deep=True)
            self._profiles[profile.student_id] = copy_prof
            return copy_prof.model_copy(deep=True)

    def get_profile(self, student_id: str) -> Optional[StudentProfile]:
        with self._lock:
            prof = self._profiles.get(student_id)
            return prof.model_copy(deep=True) if prof else None

    def update_profile(self, student_id: str, updates: Dict[str, Any]) -> Optional[StudentProfile]:
        with self._lock:
            prof = self._profiles.get(student_id)
            if not prof:
                return None

            for k, v in updates.items():
                if k == "preferences" and isinstance(v, dict):
                    for pk, pv in v.items():
                        setattr(prof.preferences, pk, pv)
                elif hasattr(prof, k) and v is not None:
                    setattr(prof, k, v)

            if "preferred_language" in updates and updates["preferred_language"]:
                prof.preferences.preferred_language = updates["preferred_language"]

            return prof.model_copy(deep=True)

    def delete_profile(self, student_id: str) -> bool:
        with self._lock:
            if student_id in self._profiles:
                del self._profiles[student_id]
                return True
            return False

    def save_knowledge_state(self, student_id: str, knowledge: LearnerKnowledge) -> LearnerKnowledge:
        with self._lock:
            prof = self._profiles.get(student_id)
            if not prof:
                prof = StudentProfile(student_id=student_id)
                self._profiles[student_id] = prof

            prof.concept_mastery[knowledge.concept_id] = knowledge.model_copy(deep=True)
            return knowledge.model_copy(deep=True)

    def get_knowledge_state(self, student_id: str, concept_id: Optional[str] = None) -> Dict[str, LearnerKnowledge]:
        with self._lock:
            prof = self._profiles.get(student_id)
            if not prof:
                return {}
            if concept_id:
                return {concept_id: prof.concept_mastery[concept_id]} if concept_id in prof.concept_mastery else {}
            return {k: v.model_copy(deep=True) for k, v in prof.concept_mastery.items()}

    def add_learning_history(self, student_id: str, entry: LearningHistoryEntry) -> LearningHistoryEntry:
        with self._lock:
            prof = self._profiles.get(student_id)
            if not prof:
                prof = StudentProfile(student_id=student_id)
                self._profiles[student_id] = prof
            prof.learning_history.insert(0, entry)
            return entry

    def get_learning_history(self, student_id: str, limit: int = 10) -> List[LearningHistoryEntry]:
        with self._lock:
            prof = self._profiles.get(student_id)
            if not prof:
                return []
            return [e.model_copy(deep=True) for e in prof.learning_history[:limit]]

    def add_assessment_history(self, student_id: str, entry: AssessmentHistoryEntry) -> AssessmentHistoryEntry:
        with self._lock:
            prof = self._profiles.get(student_id)
            if not prof:
                prof = StudentProfile(student_id=student_id)
                self._profiles[student_id] = prof
            prof.assessment_history.insert(0, entry)
            return entry

    def get_assessment_history(self, student_id: str, limit: int = 10) -> List[AssessmentHistoryEntry]:
        with self._lock:
            prof = self._profiles.get(student_id)
            if not prof:
                return []
            return [e.model_copy(deep=True) for e in prof.assessment_history[:limit]]

    def reset_profile(self, student_id: str, reset_type: str) -> bool:
        with self._lock:
            prof = self._profiles.get(student_id)
            if not prof:
                return False
            if reset_type == "RESET_PREFERENCES":
                prof.preferences = StudentPreferences()
                prof.preferred_language = "English"
                return True
            elif reset_type == "RESET_KNOWLEDGE":
                prof.concept_mastery = {}
                prof.known_concepts = []
                prof.weak_concepts = []
                prof.strong_concepts = []
                prof.misconceptions = []
                return True
            elif reset_type == "RESET_HISTORY":
                prof.learning_history = []
                prof.assessment_history = []
                return True
            elif reset_type == "RESET_ALL":
                del self._profiles[student_id]
                return True
            return False


# Global default repository instance
profile_repository: StudentProfileRepository = SQLiteProfileRepository()
