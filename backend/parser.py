import pypdf
from fastapi import UploadFile

async def extract_topics_from_pdf(file: UploadFile) -> str:
    """
    Extracts text from an uploaded PDF file.
    Returns a simple comma-separated string of detected detected lines (heuristic).
    """
    try:
        reader = pypdf.PdfReader(file.file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        if not full_text.strip():
            return "Error: No text found in PDF (Is it scanned?)"

        # --- STRATEGY 1: Structured Extraction ---
        import re
        raw_lines = full_text.split('\n')
        candidates = []
        seen = set()
        
        bullet_pattern = r'^(\d+(\.\d+)*\.?|•|-|\*|[A-Z]\.)\s+'
        structural_keywords = ["unit", "chapter", "module", "part", "topic"]
        skip_keywords = ["page", "syllabus", "course code", "semester", "credit", "total hours", "books", "reference"]

        for line in raw_lines:
            line = line.strip()
            if len(line) < 4: continue
                
            lower_line = line.lower()
            if any(k in lower_line for k in skip_keywords): continue
            
            is_structure = any(lower_line.startswith(k) for k in structural_keywords)
            has_bullet = re.match(bullet_pattern, line)
            
            is_likely_topic = (is_structure or has_bullet)
            
            # Fallback for structured: accept Title Case lines if not too long
            if not is_likely_topic and len(line) < 80 and line[0].isupper() and " " in line:
                is_likely_topic = True
                
            if is_likely_topic:
                clean_line = re.sub(bullet_pattern, '', line).strip()
                clean_line = clean_line.strip('.:;,')
                if len(clean_line) > 3 and clean_line not in seen:
                    candidates.append(clean_line)
                    seen.add(clean_line)
        
        # --- STRATEGY 2: Fallback (Simple Split) ---
        # If Strategy 1 failed (e.g. < 3 topics found), try a looser heuristic
        if len(candidates) < 3:
            candidates = []
            seen = set()
            for line in raw_lines:
                line = line.strip()
                if len(line) > 5 and len(line) < 100:
                    # Just take anything that looks like a sentence/phrase
                    if line not in seen:
                        candidates.append(line)
                        seen.add(line)
        
        # Limit to 100
        result = ", ".join(candidates[:100])
        return result if result else "No topics found (Check PDF format)"
        
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"
