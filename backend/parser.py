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
        
        # Heuristic Cleaning
        # 1. Split by common list delimiters
        import re
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', full_text)
        
        # Try to split by common syllabus patterns (Chapter X, Unit Y, bullets)
        # This is a basic regex approach.
        # Split by bullet points or numbering 1. 2. etc
        split_pattern = r'(?:\r\n|\r|\n|•|- |\d+\.\s)'
        lines = re.split(split_pattern, full_text)
        
        cleaned_topics = []
        for line in lines:
            line = line.strip()
            # Filter garbage
            if len(line) > 4 and len(line) < 100 and not line.lower().startswith('page'):
                 # Remove non-alphanumeric start
                line = re.sub(r'^[^a-zA-Z0-9]+', '', line)
                if line and line not in cleaned_topics:
                    cleaned_topics.append(line)

        # Return reasonable amount
        return ", ".join(cleaned_topics[:25])
        
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"
