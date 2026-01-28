import pypdf
from fastapi import UploadFile

async def extract_topics_from_pdf(file: UploadFile) -> str:
    """
    Extracts text from an uploaded PDF file.
    Returns a simple comma-separated string of detected detected lines (heuristic).
    """
    try:
        # pypdf requires a file-like object. UploadFile.file IS one (SpooledTemporaryFile).
        reader = pypdf.PdfReader(file.file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        # Enhanced Extraction Logic
        import re
        
        # 1. Break into lines, respecting layout
        raw_lines = full_text.split('\n')
        
        candidates = []
        seen = set()
        
        # Regex for valid topic starters: Bullets, Numbering (1., 1.1), "Unit", "Chapter"
        bullet_pattern = r'^(\d+(\.\d+)*\.?|•|-|\*|[A-Z]\.)\s+'
        structural_keywords = ["unit", "chapter", "module", "part", "topic"]
        
        skip_keywords = ["page", "syllabus", "course code", "semester", "credit", "total hours", "books", "reference"]

        for line in raw_lines:
            line = line.strip()
            
            # Skip empty or very short
            if len(line) < 4:
                continue
                
            # Skip junk metadata lines
            lower_line = line.lower()
            if any(k in lower_line for k in skip_keywords):
                continue
            
            # Check for structural headers OR bullet points
            is_structure = any(lower_line.startswith(k) for k in structural_keywords)
            has_bullet = re.match(bullet_pattern, line)
            
            # Heuristic: If it has a bullet/number OR represents a structural block -> It's likely a topic
            # Also include lines that are reasonably long (but not paragraphs) and start with capital letters
            is_likely_topic = (is_structure or has_bullet)
            
            # Fallback: If it's a short, specific line (e.g. "Linear Algebra") without a bullet, we still want it.
            # But avoid long paragraphs (descriptions)
            if not is_likely_topic and len(line) < 80 and line[0].isupper():
                is_likely_topic = True
                
            if is_likely_topic:
                # Cleaning: Remove the bullet/number itself for cleaner list
                clean_line = re.sub(bullet_pattern, '', line).strip()
                # Remove trailing dots/punctuation
                clean_line = clean_line.strip('.:;,')
                
                if len(clean_line) > 3 and clean_line not in seen:
                    candidates.append(clean_line)
                    seen.add(clean_line)
        
        # Return significantly more topics
        return ", ".join(candidates[:100])
        
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"
