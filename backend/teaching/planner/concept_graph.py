"""
Concept Graph Manager conforming to Section 11.
Manages Directed Acyclic Graph (DAG) of concepts, resolves prerequisites,
and computes topologically ordered learning paths.
"""

from typing import List, Dict, Set, Optional
from backend.teaching.schemas.concept_node import ConceptNode
import logging

logger = logging.getLogger(__name__)

class ConceptGraphManager:
    def __init__(self):
        self.nodes: Dict[str, ConceptNode] = {}
        self.adj_list: Dict[str, List[str]] = {}  # prerequisite -> list of dependent concepts
        self.dependencies: Dict[str, List[str]] = {}  # concept -> list of prerequisites

    def add_concept(self, node: ConceptNode):
        self.nodes[node.concept_id] = node
        if node.concept_id not in self.dependencies:
            self.dependencies[node.concept_id] = []
        if node.concept_id not in self.adj_list:
            self.adj_list[node.concept_id] = []

        for prereq in node.prerequisites:
            self.dependencies[node.concept_id].append(prereq)
            if prereq not in self.adj_list:
                self.adj_list[prereq] = []
            self.adj_list[prereq].append(node.concept_id)

    def get_concept(self, concept_id: str) -> Optional[ConceptNode]:
        return self.nodes.get(concept_id)

    def topological_sort(self) -> List[str]:
        """
        Kahn's algorithm for topological sorting of the concept DAG.
        Ensures prerequisites are taught before dependent concepts.
        """
        in_degree: Dict[str, int] = {}
        for cid in self.nodes:
            # Only count dependencies that are inside our node set
            valid_prereqs = [p for p in self.dependencies.get(cid, []) if p in self.nodes]
            in_degree[cid] = len(valid_prereqs)

        queue = [cid for cid, deg in in_degree.items() if deg == 0]
        # Sort queue deterministically by importance descending
        queue.sort(key=lambda c: self.nodes[c].importance, reverse=True)

        ordered = []
        while queue:
            curr = queue.pop(0)
            ordered.append(curr)

            for neighbor in self.adj_list.get(curr, []):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
                        queue.sort(key=lambda c: self.nodes[c].importance, reverse=True)

        if len(ordered) != len(self.nodes):
            logger.warning("Cycle detected or disconnected DAG in concept graph. Falling back to key-order.")
            for cid in self.nodes:
                if cid not in ordered:
                    ordered.append(cid)

        return ordered

    def filter_by_time_and_importance(
        self,
        available_minutes: float,
        known_concepts: List[str]
    ) -> List[ConceptNode]:
        """
        Selects an optimal subset of concepts fitting within available time,
        guaranteeing all prerequisites for must-teach concepts are satisfied.
        """
        all_ordered_ids = self.topological_sort()
        known_lower = {k.lower() for k in known_concepts}

        # 1. Identify must_teach concepts
        must_teach_ids = {
            cid for cid, node in self.nodes.items()
            if node.must_teach and node.name.lower() not in known_lower
        }

        # 2. Gather all transitive prerequisites for must_teach concepts
        selected_ids: Set[str] = set()
        def add_with_prereqs(cid: str):
            if cid in selected_ids or cid not in self.nodes:
                return
            for prereq in self.dependencies.get(cid, []):
                if prereq in self.nodes and self.nodes[prereq].name.lower() not in known_lower:
                    add_with_prereqs(prereq)
            selected_ids.add(cid)

        for cid in must_teach_ids:
            add_with_prereqs(cid)

        # 3. If there is remaining time, add optional concepts sorted by importance
        current_time = sum(self.nodes[cid].estimated_minutes for cid in selected_ids)
        if current_time < available_minutes:
            remaining_nodes = [
                self.nodes[cid] for cid in all_ordered_ids
                if cid not in selected_ids and self.nodes[cid].name.lower() not in known_lower
            ]
            remaining_nodes.sort(key=lambda n: n.importance, reverse=True)

            for node in remaining_nodes:
                if current_time + node.estimated_minutes <= available_minutes:
                    # check if its prerequisites are in selected_ids
                    prereqs_met = all(p in selected_ids or p not in self.nodes for p in node.prerequisites)
                    if prereqs_met:
                        selected_ids.add(node.concept_id)
                        current_time += node.estimated_minutes

        # Return in topological order
        return [self.nodes[cid] for cid in all_ordered_ids if cid in selected_ids]

    @classmethod
    def build_ohms_law_graph(cls) -> "ConceptGraphManager":
        manager = cls()
        c1 = ConceptNode(
            concept_id="c_charge_voltage",
            name="Voltage (Electric Potential) & Current (Charge Flow)",
            description="Voltage provides electrical pressure that pushes electrons; Current is the rate of flow.",
            importance=0.9,
            difficulty=0.3,
            prerequisites=[],
            estimated_minutes=4.0,
            learning_objective="Understand physical intuition of Voltage and Current",
            must_teach=True
        )
        c2 = ConceptNode(
            concept_id="c_resistance",
            name="Resistance & Opposition to Flow",
            description="Resistance opposes electron flow, converting electrical energy into heat.",
            importance=0.9,
            difficulty=0.4,
            prerequisites=["c_charge_voltage"],
            estimated_minutes=4.0,
            learning_objective="Understand Resistance and how materials oppose charge flow",
            must_teach=True
        )
        c3 = ConceptNode(
            concept_id="c_ohms_governing_law",
            name="Ohm's Law: V = I * R and I = V / R",
            description="The governing mathematical relationship uniting Voltage, Current, and Resistance.",
            importance=1.0,
            difficulty=0.5,
            prerequisites=["c_resistance"],
            estimated_minutes=6.0,
            learning_objective="Master direct and inverse proportionalities in Ohm's Law",
            must_teach=True
        )
        c4 = ConceptNode(
            concept_id="c_circuit_calculations",
            name="Circuit Analysis & Practical Calculations",
            description="Applying I = V / R to calculate parameters in working DC circuits.",
            importance=0.8,
            difficulty=0.6,
            prerequisites=["c_ohms_governing_law"],
            estimated_minutes=6.0,
            learning_objective="Calculate circuit values and predict component behavior",
            must_teach=False
        )

        for c in [c1, c2, c3, c4]:
            manager.add_concept(c)
        return manager

    @classmethod
    def build_binary_search_graph(cls) -> "ConceptGraphManager":
        manager = cls()
        c1 = ConceptNode(
            concept_id="c_bs_prereq",
            name="Sorted Order & Linear vs Divide-and-Conquer",
            description="Why sorted order enables logarithmic halving of search space.",
            importance=0.9,
            difficulty=0.3,
            prerequisites=[],
            estimated_minutes=4.0,
            learning_objective="Explain why arrays must be sorted for binary search",
            must_teach=True
        )
        c2 = ConceptNode(
            concept_id="c_bs_pointers",
            name="Three Pointers: Low, Mid, High",
            description="Calculating mid and maintaining invariants across iterations.",
            importance=1.0,
            difficulty=0.5,
            prerequisites=["c_bs_prereq"],
            estimated_minutes=6.0,
            learning_objective="Demonstrate pointer calculations without overflow",
            must_teach=True
        )
        c3 = ConceptNode(
            concept_id="c_bs_halving",
            name="Halving Search Space & Boundary Updates",
            description="Adjusting low = mid + 1 or high = mid - 1 based on target comparison.",
            importance=1.0,
            difficulty=0.6,
            prerequisites=["c_bs_pointers"],
            estimated_minutes=6.0,
            learning_objective="Update search boundaries correctly without off-by-one errors",
            must_teach=True
        )
        for c in [c1, c2, c3]:
            manager.add_concept(c)
        return manager

    @classmethod
    def build_generic_graph(cls, topic: str, count: int = 3) -> "ConceptGraphManager":
        manager = cls()
        prev_id = None
        for i in range(1, count + 1):
            cid = f"c_{i}_{topic.lower().replace(' ', '_')[:10]}"
            node = ConceptNode(
                concept_id=cid,
                name=f"{topic}: Phase {i}",
                description=f"Core conceptual foundations and mechanisms of {topic} (Part {i}).",
                importance=1.0 - (i - 1) * 0.1,
                difficulty=0.3 + (i - 1) * 0.2,
                prerequisites=[prev_id] if prev_id else [],
                estimated_minutes=5.0,
                learning_objective=f"Master key insights of {topic} part {i}",
                must_teach=(i <= 2)
            )
            manager.add_concept(node)
            prev_id = cid
        return manager
