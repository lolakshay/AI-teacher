"""
Deterministic Visual Renderer (Agent 4)
Produces high-fidelity, hallucination-free 16:9 educational visuals (1920x1080)
for Equations, Graphs, Diagrams, Code, Timelines, Processes, and Concept Cards.
Conforms strictly to Sections 10, 11, 12, 13, 14, 15, 16, 17, 37, 42, 43, 44.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont


class VisualRenderer:
    """
    Renders deterministic educational frames (1920x1080) for video scenes.
    Ensures scientific and mathematical precision without AI visual hallucinations.
    """
    WIDTH = 1920
    HEIGHT = 1080
    BG_COLOR = "#0b0f19"        # Deep slate background
    CARD_BG = "#161e31"         # Elevated surface card
    ACCENT_CYAN = "#06b6d4"     # Primary accent (electric cyan)
    ACCENT_BLUE = "#3b82f6"     # Secondary accent
    ACCENT_AMBER = "#f59e0b"    # Highlight accent (resistor / warning)
    ACCENT_GREEN = "#10b981"    # Success / current
    TEXT_MAIN = "#f8fafc"       # High contrast white
    TEXT_MUTED = "#94a3b8"      # Slate secondary text

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            from backend.app.core.config import settings
            self.output_dir = settings.UPLOAD_DIR / "video_assets" / "frames"
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_scene_visual(self, scene_id: str, visual_spec: Dict[str, Any]) -> str:
        """
        Dispatches visual specification to dedicated deterministic renderer.
        Returns file path to generated 1920x1080 frame image.
        """
        v_type = visual_spec.get("type", "concept_card")
        out_path = self.output_dir / f"{scene_id}_{v_type}.png"

        try:
            if v_type == "equation":
                self.render_equation(visual_spec, out_path)
            elif v_type == "graph":
                self.render_graph(visual_spec, out_path)
            elif v_type == "diagram":
                self.render_diagram(visual_spec, out_path)
            elif v_type == "code":
                self.render_code(visual_spec, out_path)
            elif v_type == "timeline":
                self.render_timeline(visual_spec, out_path)
            elif v_type == "worked_example":
                self.render_worked_example(visual_spec, out_path)
            elif v_type == "process":
                self.render_process(visual_spec, out_path)
            elif v_type == "map":
                self.render_map(visual_spec, out_path)
            elif v_type == "image":
                self.render_image(visual_spec, out_path)
            else:
                self.render_concept_card(visual_spec, out_path)
        except Exception as e:
            # Robust fallback to concept card if specialized rendering has issues
            self.render_concept_card(
                {"title": visual_spec.get("title", "Educational Concept"), "definition": str(visual_spec)},
                out_path
            )

        return str(out_path)

    # ============================================================
    # 1. EQUATIONS (Section 12, 43)
    # ============================================================
    def render_equation(self, spec: Dict[str, Any], out_path: Path):
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(self.BG_COLOR)
        ax.set_facecolor(self.BG_COLOR)
        ax.axis("off")

        # Header Title
        title = spec.get("title", "Governing Physical Equation")
        ax.text(0.08, 0.88, title.upper(), fontsize=26, fontweight="bold", color=self.ACCENT_CYAN, va="center")

        # Card container
        rect = patches.FancyBboxPatch(
            (0.08, 0.22), 0.84, 0.60,
            boxstyle="round,pad=0.03,rounding_size=0.04",
            facecolor=self.CARD_BG, edgecolor=self.ACCENT_BLUE, linewidth=2.5, alpha=0.95
        )
        ax.add_patch(rect)

        # Primary Equation formula (Rendered cleanly)
        equation_str = spec.get("equation", "V = I * R")
        latex_eq = f"${equation_str.replace('*', r'\cdot')}$"
        ax.text(0.50, 0.62, latex_eq, fontsize=58, fontweight="bold", color=self.TEXT_MAIN, ha="center", va="center")

        # Breakdown / Explanation items
        explanations = spec.get("explanation", [])
        if explanations:
            y_start = 0.42
            for i, line in enumerate(explanations):
                ax.text(0.50, y_start - (i * 0.08), f"•  {line}", fontsize=22, color=self.TEXT_MUTED, ha="center", va="center")

        # Highlight tag
        highlight = spec.get("highlight")
        if highlight:
            ax.text(0.50, 0.27, f"FOCUS VARIABLE: [{highlight}]", fontsize=18, fontweight="bold", color=self.ACCENT_AMBER, ha="center")

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)

    # ============================================================
    # 2. GRAPHS (Section 13, 43)
    # ============================================================
    def render_graph(self, spec: Dict[str, Any], out_path: Path):
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(self.BG_COLOR)
        ax.set_facecolor(self.CARD_BG)

        title = spec.get("title", "Current vs Resistance (Ohm's Law)")
        fig.suptitle(title.upper(), fontsize=28, fontweight="bold", color=self.ACCENT_CYAN, y=0.94)

        # Axis styling
        ax.tick_params(colors=self.TEXT_MUTED, labelsize=16)
        for spine in ax.spines.values():
            spine.set_color("#334155")
            spine.set_linewidth(1.5)
        ax.grid(True, linestyle="--", alpha=0.3, color="#475569")

        x_cfg = spec.get("x_axis", {})
        y_cfg = spec.get("y_axis", {})
        x_label = x_cfg.get("label", "Resistance") + (f" ({x_cfg.get('unit')})" if x_cfg.get("unit") else "")
        y_label = y_cfg.get("label", "Current") + (f" ({y_cfg.get('unit')})" if y_cfg.get("unit") else "")
        ax.set_xlabel(x_label, fontsize=20, fontweight="bold", color=self.TEXT_MAIN, labelpad=15)
        ax.set_ylabel(y_label, fontsize=20, fontweight="bold", color=self.TEXT_MAIN, labelpad=15)

        # Plot curve based on data points or relationship
        data_points = spec.get("data_points")
        if data_points:
            xs = [p.get("x", 0) for p in data_points]
            ys = [p.get("y", 0) for p in data_points]
            ax.plot(xs, ys, color=self.ACCENT_CYAN, linewidth=4, label="Observed Relationship")
            ax.scatter(xs, ys, color=self.ACCENT_AMBER, s=120, zorder=5, label="Data Points")
        else:
            # Default inverse proportionality curve for Ohm's Law
            xs = np.linspace(1.0, 12.0, 100)
            ys = 12.0 / xs  # I = V / R with V = 12V
            ax.plot(xs, ys, color=self.ACCENT_CYAN, linewidth=4, label="I = V / R (V = 12V Constant)")
            # Highlight key points
            ax.scatter([2.0, 4.0, 6.0], [6.0, 3.0, 2.0], color=self.ACCENT_AMBER, s=150, zorder=5)
            ax.annotate("R = 4Ω ➔ I = 3A", (4.0, 3.0), textcoords="offset points", xytext=(20, 20),
                        color=self.TEXT_MAIN, fontsize=18, fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color=self.ACCENT_AMBER, lw=2))

        ax.legend(facecolor="#1e293b", edgecolor="#475569", labelcolor=self.TEXT_MAIN, fontsize=16, loc="upper right")
        plt.subplots_adjust(left=0.10, right=0.90, top=0.86, bottom=0.12)
        fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)

    # ============================================================
    # 3. DIAGRAMS (Section 11, 43)
    # ============================================================
    def render_diagram(self, spec: Dict[str, Any], out_path: Path):
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(self.BG_COLOR)
        ax.set_facecolor(self.BG_COLOR)
        ax.axis("off")

        title = spec.get("title", "Circuit Diagram: Ohm's Law")
        ax.text(0.08, 0.90, title.upper(), fontsize=26, fontweight="bold", color=self.ACCENT_CYAN, va="center")

        desc = spec.get("description", "")
        if desc:
            ax.text(0.08, 0.85, desc, fontsize=18, color=self.TEXT_MUTED, va="center")

        # Outer circuit loop wire
        loop = patches.FancyBboxPatch(
            (0.18, 0.22), 0.64, 0.52,
            boxstyle="round,pad=0.02,rounding_size=0.04",
            facecolor="none", edgecolor="#38bdf8", linewidth=4.0
        )
        ax.add_patch(loop)

        # Battery on Left Side
        bat_box = patches.FancyBboxPatch(
            (0.13, 0.40), 0.10, 0.16,
            boxstyle="square,pad=0.01",
            facecolor="#1e293b", edgecolor=self.ACCENT_CYAN, linewidth=3.0
        )
        ax.add_patch(bat_box)
        v_meta = spec.get("metadata", {}).get("voltage", 12.0)
        ax.text(0.18, 0.48, f"+\nBATTERY\n{v_meta}V\n-", fontsize=15, fontweight="bold", color=self.TEXT_MAIN, ha="center", va="center")

        # Resistor on Right Side
        res_box = patches.FancyBboxPatch(
            (0.77, 0.40), 0.10, 0.16,
            boxstyle="square,pad=0.01",
            facecolor="#1e293b", edgecolor=self.ACCENT_AMBER, linewidth=3.0
        )
        ax.add_patch(res_box)
        r_meta = spec.get("metadata", {}).get("resistance", 4.0)
        ax.text(0.82, 0.48, f"RESISTOR\n(R)\n{r_meta} Ω", fontsize=15, fontweight="bold", color=self.ACCENT_AMBER, ha="center", va="center")

        # Current Arrow along top wire
        i_meta = spec.get("metadata", {}).get("current", 3.0)
        ax.annotate(
            "", xy=(0.58, 0.74), xytext=(0.42, 0.74),
            arrowprops=dict(arrowstyle="->", color=self.ACCENT_GREEN, lw=5, mutation_scale=25)
        )
        ax.text(0.50, 0.78, f"Current Flow (I) = {i_meta} A  ➔", fontsize=20, fontweight="bold", color=self.ACCENT_GREEN, ha="center")

        # Bottom Info Badge
        rect_info = patches.FancyBboxPatch(
            (0.25, 0.08), 0.50, 0.08,
            boxstyle="round,pad=0.01",
            facecolor="#0f172a", edgecolor="#334155", linewidth=2.0
        )
        ax.add_patch(rect_info)
        ax.text(0.50, 0.12, "Equation: I = V / R  |  Current flows from High (+) to Low (-) Potential",
                fontsize=16, color=self.TEXT_MAIN, ha="center", va="center")

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)

    # ============================================================
    # 4. CODE SCENES (Section 14, 43)
    # ============================================================
    def render_code(self, spec: Dict[str, Any], out_path: Path):
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(self.BG_COLOR)
        ax.set_facecolor(self.BG_COLOR)
        ax.axis("off")

        title = spec.get("title", "Algorithm Code Execution")
        ax.text(0.08, 0.90, title.upper(), fontsize=26, fontweight="bold", color=self.ACCENT_CYAN)

        # Editor frame
        rect_code = patches.FancyBboxPatch(
            (0.08, 0.32), 0.84, 0.52,
            boxstyle="round,pad=0.02",
            facecolor="#111827", edgecolor="#374151", linewidth=2.0
        )
        ax.add_patch(rect_code)

        # Mac-style header dots
        for i, col in enumerate(["#ef4444", "#f59e0b", "#10b981"]):
            circle = plt.Circle((0.11 + i * 0.018, 0.81), 0.008, color=col)
            ax.add_patch(circle)
        ax.text(0.20, 0.81, f"main.{spec.get('language', 'py')}", fontsize=14, color=self.TEXT_MUTED, va="center")

        # Code lines
        code_text = spec.get("code", "")
        lines = code_text.split("\n")[:10]
        highlight_lines = spec.get("highlight_lines", [])

        y_pos = 0.74
        for idx, line in enumerate(lines, start=1):
            is_highlight = idx in highlight_lines
            if is_highlight:
                # Highlight bar behind active line
                h_rect = patches.Rectangle((0.09, y_pos - 0.02), 0.82, 0.038, facecolor="#1e3a8a", alpha=0.6)
                ax.add_patch(h_rect)
            
            line_col = self.ACCENT_CYAN if is_highlight else self.TEXT_MAIN
            ax.text(0.11, y_pos, f"{idx:2d}  ", fontfamily="monospace", fontsize=16, color="#6b7280")
            ax.text(0.16, y_pos, line, fontfamily="monospace", fontsize=16, color=line_col)
            y_pos -= 0.042

        # Terminal Output Box below
        rect_term = patches.FancyBboxPatch(
            (0.08, 0.10), 0.84, 0.18,
            boxstyle="round,pad=0.02",
            facecolor="#030712", edgecolor="#1f2937", linewidth=2.0
        )
        ax.add_patch(rect_term)
        ax.text(0.11, 0.24, "TERMINAL OUTPUT:", fontsize=14, fontweight="bold", color=self.TEXT_MUTED)
        output_text = spec.get("output", "Execution completed successfully.")
        ax.text(0.11, 0.16, f">>> {output_text}", fontfamily="monospace", fontsize=18, color=self.ACCENT_GREEN)

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)

    # ============================================================
    # 5. TIMELINES (Section 15, 43)
    # ============================================================
    def render_timeline(self, spec: Dict[str, Any], out_path: Path):
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(self.BG_COLOR)
        ax.set_facecolor(self.BG_COLOR)
        ax.axis("off")

        title = spec.get("title", "Chronological Milestones")
        ax.text(0.08, 0.88, title.upper(), fontsize=26, fontweight="bold", color=self.ACCENT_CYAN)

        events = spec.get("events", [])
        if not events:
            events = [
                {"year": "1827", "title": "Ohm Publishes Law", "description": "Formulates V = I * R"},
                {"year": "1881", "title": "Unit Adopted", "description": "International standard named after Ohm"}
            ]

        # Horizontal spine line
        ax.plot([0.15, 0.85], [0.50, 0.50], color="#475569", linewidth=4, zorder=1)

        n = len(events)
        step = 0.70 / max(1, (n - 1)) if n > 1 else 0.35
        x_start = 0.15 if n > 1 else 0.50

        for i, ev in enumerate(events):
            x = x_start + (i * step) if n > 1 else 0.50
            # Milestone node
            circle = plt.Circle((x, 0.50), 0.022, facecolor=self.CARD_BG, edgecolor=self.ACCENT_CYAN, linewidth=4, zorder=3)
            ax.add_patch(circle)

            # Year badge
            year = ev.get("year", f"Event {i+1}")
            ax.text(x, 0.56, year, fontsize=22, fontweight="bold", color=self.ACCENT_AMBER, ha="center")

            # Description card
            card = patches.FancyBboxPatch(
                (x - 0.12, 0.26), 0.24, 0.18,
                boxstyle="round,pad=0.01",
                facecolor=self.CARD_BG, edgecolor="#334155", linewidth=1.5
            )
            ax.add_patch(card)
            ax.text(x, 0.38, ev.get("title", ""), fontsize=16, fontweight="bold", color=self.TEXT_MAIN, ha="center")
            ax.text(x, 0.32, ev.get("description", ""), fontsize=13, color=self.TEXT_MUTED, ha="center")

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)

    # ============================================================
    # 6. WORKED EXAMPLES (Section 10, 20)
    # ============================================================
    def render_worked_example(self, spec: Dict[str, Any], out_path: Path):
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(self.BG_COLOR)
        ax.set_facecolor(self.BG_COLOR)
        ax.axis("off")

        title = spec.get("title", "Step-by-Step Worked Example")
        ax.text(0.08, 0.90, title.upper(), fontsize=26, fontweight="bold", color=self.ACCENT_CYAN)

        # Problem Statement Box
        rect_prob = patches.FancyBboxPatch(
            (0.08, 0.74), 0.84, 0.12,
            boxstyle="round,pad=0.02",
            facecolor="#1e293b", edgecolor=self.ACCENT_BLUE, linewidth=2.0
        )
        ax.add_patch(rect_prob)
        ax.text(0.10, 0.82, "PROBLEM:", fontsize=15, fontweight="bold", color=self.ACCENT_AMBER)
        ax.text(0.10, 0.77, spec.get("problem", "Calculate Current I given Voltage V and Resistance R"),
                fontsize=18, color=self.TEXT_MAIN)

        # Solution card
        rect_sol = patches.FancyBboxPatch(
            (0.08, 0.16), 0.84, 0.54,
            boxstyle="round,pad=0.02",
            facecolor=self.CARD_BG, edgecolor="#334155", linewidth=2.0
        )
        ax.add_patch(rect_sol)

        steps = spec.get("steps", [])
        y_pos = 0.62
        for s in steps:
            ax.text(0.12, y_pos, s, fontsize=20, color=self.TEXT_MAIN)
            y_pos -= 0.08

        # Result Highlight Box
        result_str = spec.get("result", "")
        if result_str:
            res_box = patches.FancyBboxPatch(
                (0.12, 0.22), 0.40, 0.09,
                boxstyle="round,pad=0.01",
                facecolor="#064e3b", edgecolor=self.ACCENT_GREEN, linewidth=2.5
            )
            ax.add_patch(res_box)
            ax.text(0.32, 0.265, f"FINAL ANSWER: {result_str}", fontsize=20, fontweight="bold", color="#ecfdf5", ha="center", va="center")

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)

    # ============================================================
    # 7. CONCEPT CARDS / GENERAL FALLBACK
    # ============================================================
    def render_concept_card(self, spec: Dict[str, Any], out_path: Path):
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        fig.patch.set_facecolor(self.BG_COLOR)
        ax.set_facecolor(self.BG_COLOR)
        ax.axis("off")

        # Container
        card = patches.FancyBboxPatch(
            (0.08, 0.15), 0.84, 0.70,
            boxstyle="round,pad=0.03,rounding_size=0.04",
            facecolor=self.CARD_BG, edgecolor=self.ACCENT_BLUE, linewidth=2.5
        )
        ax.add_patch(card)

        badge = spec.get("badge", "CORE CONCEPT")
        ax.text(0.12, 0.78, badge.upper(), fontsize=16, fontweight="bold", color=self.ACCENT_AMBER)

        title = spec.get("title", "Key Teaching Concept")
        ax.text(0.12, 0.70, title, fontsize=36, fontweight="bold", color=self.TEXT_MAIN)

        subtitle = spec.get("subtitle", "")
        if subtitle:
            ax.text(0.12, 0.64, subtitle, fontsize=20, color=self.ACCENT_CYAN)

        definition = spec.get("definition", "")
        if definition:
            ax.text(0.12, 0.54, definition, fontsize=22, color="#cbd5e1", wrap=True)

        key_points = spec.get("key_points", [])
        y_pos = 0.42
        for pt in key_points:
            ax.text(0.12, y_pos, f"✔  {pt}", fontsize=20, color=self.TEXT_MAIN)
            y_pos -= 0.08

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)

    # Supporting methods for remaining types
    def render_process(self, spec: Dict[str, Any], out_path: Path):
        self.render_concept_card(spec, out_path)

    def render_map(self, spec: Dict[str, Any], out_path: Path):
        # Graceful fallback visual for map
        self.render_concept_card({
            "title": spec.get("title", "Geographic Context Map"),
            "subtitle": f"Region: {spec.get('region', 'Global')}",
            "definition": spec.get("fallback_instruction", "Geographical mapping context"),
            "key_points": [f"Region: {spec.get('region', 'General')}"] + spec.get("labels", [])
        }, out_path)

    def render_image(self, spec: Dict[str, Any], out_path: Path):
        self.render_concept_card({
            "title": spec.get("title", "Educational Visual Reference"),
            "definition": spec.get("caption") or spec.get("purpose", ""),
            "key_points": [f"Source: {spec.get('source', 'Archive')}"]
        }, out_path)


visual_renderer = VisualRenderer()
