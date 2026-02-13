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

        # --- ADVANCED PARSER: Structure + Semantic Filtering ---
        
        # 1. Clean & Normalization
        # Remove multiple newlines which might break flow
        text_content = re.sub(r'\n+', '\n', full_text)
        raw_lines = text_content.split('\n')
        
        extracted_topics = []
        seen = set()
        
        # Structure Markers
        unit_pattern = re.compile(r'^(?:UNIT|MODULE|CHAPTER|SECTION)\s*(?:[-:]?)\s*(\d+|[IVX]+)', re.IGNORECASE)
        
        # Stop Markers (End of Syllabus)
        stop_markers = [
            "text books", "references", "reference books", "course outcomes", 
            "program outcomes", "question paper", "credits", "evaluation",
            "grading", "books recommended"
        ]
        
        # Noise Filters (Lines to ignore even inside valid units)
        noise_starts = [
            "to understand", "to study", "students will", "objective", 
            "outcome", "learn", "study", "introduction", "unit", "module"
        ]
        
        # Academic filler removal regex (remove "Introduction to...", "Basics of...")
        filler_pattern = re.compile(r'^(introduction to|basics of|concept of|overview of|principles of)\s+', re.IGNORECASE)

        is_parsing_block = False
        
        for line in raw_lines:
            line = line.strip()
            if len(line) < 4: continue
            
            lower_line = line.lower()
            
            # --- PHASE 1: Structure Detection ---
            # Start Block?
            if unit_pattern.match(line):
                is_parsing_block = True
                continue 
            
            # Stop Block?
            if any(lower_line.startswith(m) for m in stop_markers):
                is_parsing_block = False
                continue

            # --- PHASE 2: Intelligent Content Filtering ---
            if is_parsing_block:
                # 1. Skip garbage metadata
                if lower_line.startswith("page") or re.match(r'^\d+$', line):
                    continue
                
                # 2. Skip "Descriptive" sentences (Objectives/Outcomes often look like this)
                # Heuristic: Topics are usually Title Case or fragments. Sentences start with lower case verbs often.
                if any(lower_line.startswith(n) for n in noise_starts):
                    continue
                    
                # 3. Clean "Bullet" styles
                clean_line = re.sub(r'^(\d+(\.\d+)*\.?|•|-|\*|[A-Z]\.)\s+', '', line)
                
                # 4. Remove "Filler" prefixes ("Introduction to AI" -> "AI")
                clean_line = filler_pattern.sub('', clean_line)
                
                # 5. Split Multi-topic lines (comma or semi-colon separated)
                # Syllabus often lists: "Arrays, Linked Lists, Stacks, Queues"
                delimiters = r'[,;]'
                parts = re.split(delimiters, clean_line)
                
                for p in parts:
                    p = p.strip()
                    p = p.strip('.') # Remove trailing dots
                    
                    # FINAL QUALITY CHECK
                    # Topics are usually Noun Phrases, typically 1-5 words.
                    # If it's too long (> 60 chars), it's likely a description, not a topic.
                    if 3 < len(p) < 60:
                        # Capitalization check: Real topics usually have at least one capital letter 
                        # (unless the whole PDF is lowercase, which is rare)
                        if any(c.isupper() for c in p) or p.istitle():
                            if p not in seen:
                                extracted_topics.append(p)
                                seen.add(p)

        # --- FALLBACK ---
        if len(extracted_topics) < 5:
             return "AI Parsed: Minimal topics found. Please ensure Units are clearly labeled (e.g. 'Unit 1')."

        # Return unique, clean topics
        return ", ".join(extracted_topics)
        
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"
