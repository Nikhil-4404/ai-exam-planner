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
        
        # Heuristic: Split by newlines, filter short lines, take top 20
        lines = [line.strip() for line in full_text.split('\n') if len(line.strip()) > 5]
        
        # Deduplication and cleanup
        unique_lines = list(set(lines))
        # Return top 20 for MVP
        data = ", ".join(unique_lines[:20])
        return data
        
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"
