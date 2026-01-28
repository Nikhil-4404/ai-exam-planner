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

        import re
        
        # --- STRATEGY: Block-Based Extraction ---
        # 1. Identify "Units" or "Modules".
        # 2. Extract text ONLY between these blocks.
        # 3. Stop when hitting "Text Books" or "References".
        
        raw_lines = full_text.split('\n')
        extracted_topics = []
        seen = set()
        
        # Regex to detect "UNIT I", "Module 1", "Chapter 5", etc.
        unit_pattern = re.compile(r'^(?:UNIT|MODULE|CHAPTER)\s*(?:[-:]?)\s*(\d+|[IVX]+)', re.IGNORECASE)
        
        # Terms that signal the END of a syllabus block
        stop_markers = ["text books", "references", "reference books", "course outcomes", "outcomes", "question paper pattern", "credits", "total hours"]
        
        is_parsing_block = False
        
        for line in raw_lines:
            line = line.strip()
            if len(line) < 3: continue
            
            lower_line = line.lower()
            
            # Check if entering a new Unit/Module
            # We strictly only turn ON parsing when we see a Unit header
            if unit_pattern.match(line):
                is_parsing_block = True
                continue 
                
            # Check if hitting a stop section
            if any(lower_line.startswith(marker) for marker in stop_markers):
                is_parsing_block = False 
                continue

            # Capture Content
            if is_parsing_block:
                # Filter garbage (Page numbers, codes, university headers)
                if lower_line.startswith("page") or re.match(r'^\d+$', line):
                    continue
                
                # Handling Comma-Separated Topics (common in syllabi: "Topic A, Topic B...")
                if ',' in line:
                    parts = line.split(',')
                    for p in parts:
                        p = p.strip()
                        # Remove leading bullets/numbers
                        p = re.sub(r'^(\d+(\.\d+)*\.?|•|-|\*|[A-Z]\.)\s+', '', p)
                        # Remove trailing periods
                        p = p.strip('.')
                        
                        if len(p) > 3 and p not in seen:
                            extracted_topics.append(p)
                            seen.add(p)
                else:
                    # Single line topic
                    clean_line = re.sub(r'^(\d+(\.\d+)*\.?|•|-|\*|[A-Z]\.)\s+', '', line)
                    clean_line = clean_line.strip('.')
                    if len(clean_line) > 3 and clean_line not in seen:
                         extracted_topics.append(clean_line)
                         seen.add(clean_line)

        # --- FALLBACK ---
        # If strict block parsing found nothing (maybe format is different), 
        # let's try a simpler approach: Just grab everything between bullet points
        if len(extracted_topics) < 5:
             # Try simple bullet scan if Unit mode failed
             for line in raw_lines:
                 line = line.strip()
                 # If line starts with bullet or number
                 if re.match(r'^(\d+\.|•|-)\s+', line):
                      clean = re.sub(r'^(\d+\.|•|-)\s+', '', line).strip('.')
                      if len(clean) > 4 and clean not in seen:
                          extracted_topics.append(clean)
                          seen.add(clean)

        return ", ".join(extracted_topics) if extracted_topics else "Parsing Failed: Try copying topics manually."
        
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"
