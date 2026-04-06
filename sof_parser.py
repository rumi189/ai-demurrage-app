import fitz  # PyMuPDF

def extract_text(uploaded_file):
    """
    Extract text from uploaded PDF
    """
    text = ""

    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:
            text += page.get_text()

        return text

    except Exception as e:
        return f"ERROR READING PDF: {str(e)}"