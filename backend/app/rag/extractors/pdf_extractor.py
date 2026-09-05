"""
PDF Document Extractor
Supports PyMuPDF (fitz) and pypdf fallback.
Preserves:
- Page numbers
- Block ordering and types
- Tables as structured markdown
- Equations and formulas
- Scanned page detection (requires_ocr flag)
"""

import re
from pathlib import Path
from typing import List, Tuple
from backend.app.rag.extractors.base import DocumentExtractor
from backend.app.rag.models import ExtractedBlock


class PDFExtractor(DocumentExtractor):
    def can_handle(self, file_path: Path, mime_type: str = "") -> bool:
        return file_path.suffix.lower() == ".pdf" or mime_type == "application/pdf"

    def extract(self, file_path: Path) -> Tuple[List[ExtractedBlock], bool]:
        blocks: List[ExtractedBlock] = []
        requires_ocr = False

        # Try PyMuPDF (fitz) first
        try:
            import fitz
            doc = fitz.open(str(file_path))
            total_pages = len(doc)

            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_num = page_idx + 1

                # Check for tables first
                table_rects = []
                try:
                    tables = page.find_tables()
                    for t in tables:
                        df_rows = t.extract()
                        if df_rows and len(df_rows) > 1:
                            # Format as markdown table
                            header = " | ".join([str(c or "").strip() for c in df_rows[0]])
                            separator = " | ".join(["---"] * len(df_rows[0]))
                            body_lines = [
                                " | ".join([str(c or "").strip() for c in row])
                                for row in df_rows[1:]
                            ]
                            table_text = f"| {header} |\n| {separator} |\n" + "\n".join(
                                [f"| {b} |" for b in body_lines]
                            )
                            blocks.append(
                                ExtractedBlock(
                                    text=table_text,
                                    block_type="table",
                                    page_number=page_num,
                                    confidence=0.95
                                )
                            )
                            table_rects.append(t.bbox)
                except Exception:
                    pass

                # Extract text blocks
                raw_blocks = page.get_text("blocks")
                page_char_count = 0

                for b in raw_blocks:
                    # b: (x0, y0, x1, y1, text, block_no, block_type)
                    if len(b) >= 5:
                        b_text = b[4].strip()
                        if not b_text:
                            continue

                        page_char_count += len(b_text)

                        # Determine block type
                        block_type = "paragraph"
                        heading_level = None

                        # Check heading patterns
                        is_heading = False
                        if len(b_text.splitlines()) <= 2 and len(b_text) < 120:
                            if re.match(r"^(chapter\s+\d+|unit\s+[ivxlcdm\d]+|\d+(\.\d+)*\s+[a-z])", b_text, re.IGNORECASE):
                                is_heading = True
                                heading_level = 2 if "." in b_text.split()[0] else 1
                            elif b_text.isupper() and len(b_text) > 4:
                                is_heading = True
                                heading_level = 1

                        if is_heading:
                            block_type = "heading"
                        elif re.search(r"[=\+\-\*/∫∑√π].*[=\+\-\*/∫∑√π]", b_text) and len(b_text) < 80:
                            block_type = "equation"
                        elif b_text.startswith(("- ", "• ", "* ", "1. ", "2. ", "3. ")):
                            block_type = "list"

                        blocks.append(
                            ExtractedBlock(
                                text=b_text,
                                block_type=block_type,
                                page_number=page_num,
                                heading_level=heading_level,
                                confidence=0.92
                            )
                        )

                # Check if page is image-only or scanned
                image_list = page.get_images()
                if page_char_count < 30 and len(image_list) > 0:
                    requires_ocr = True

            doc.close()
            return blocks, requires_ocr

        except Exception as fitz_err:
            # Fallback to pypdf if fitz fails
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                text = page.extract_text() or ""
                clean_text = text.strip()
                if not clean_text:
                    requires_ocr = True
                    continue

                for paragraph in clean_text.split("\n\n"):
                    p = paragraph.strip()
                    if p:
                        blocks.append(
                            ExtractedBlock(
                                text=p,
                                block_type="paragraph",
                                page_number=page_num,
                                confidence=0.85
                            )
                        )

            return blocks, requires_ocr
