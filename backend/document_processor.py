
from pypdf import PdfReader


def extract_text_from_pdf(file_path):
    """
    Extract text from an uploaded PDF document.
    """

    reader = PdfReader(file_path)

    extracted_pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text:
            extracted_pages.append({
                "page": page_number,
                "text": text
            })

    return extracted_pages
