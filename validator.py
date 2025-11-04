import re
from pdf2image import convert_from_path
import pytesseract

# Optional if Tesseract is not in PATH:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def process_document(pdf_path, form_data):
    """
    Validates a single PDF document against its expected form data.
    """
    print(f"\n📄 Processing {form_data.get('doc_type')} for {form_data.get('name')}")

    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300, grayscale=True)
    except Exception as e:
        return {'doc_type': form_data.get('doc_type'),
                'status': f"Error: Could not read PDF file. {e}",
                'validation_passed': False}

    full_text = ""
    for img in images:
        full_text += pytesseract.image_to_string(img, lang='eng+hin')

    full_text = full_text.lower()
    name_from_form = form_data.get('name', '').lower()

    # Flexible identifier field names
    id_field = form_data.get('id_number') or form_data.get('roll_number') or form_data.get('registration_number')
    id_field = (id_field or '').lower().replace(' ', '')
    expected_doc_type = form_data.get('doc_type', '').lower()

    # --- Document-specific validation rules ---
    doc_rules = {
        'aadhaar card': ['aadhaar', 'आधार'],
        'pan card': ['income tax department', 'permanent account number', 'pan'],
        'marksheet': ['marksheet', 'grade', 'university', 'board'],
        'birth certificate': ['birth certificate', 'date of birth', 'dob']
    }

    # Check document keyword
    keywords = doc_rules.get(expected_doc_type, [])
    if not any(k in full_text for k in keywords):
        return {'doc_type': expected_doc_type,
                'status': f"Mismatch: '{expected_doc_type}' keywords not found.",
                'validation_passed': False}

    # Check name
    if name_from_form and name_from_form not in full_text:
        return {'doc_type': expected_doc_type,
                'status': f"Mismatch: Name '{name_from_form}' not found.",
                'validation_passed': False}

    # Check ID number or Roll number
    if id_field and id_field not in full_text.replace(' ', ''):
        return {'doc_type': expected_doc_type,
                'status': f"Mismatch: ID '{id_field}' not found.",
                'validation_passed': False}

    # Passed
    return {'doc_type': expected_doc_type,
            'status': f"Valid: {expected_doc_type} matches the form data.",
            'validation_passed': True}


def validate_multiple_documents(form_data):
    """
    Takes multiple document entries and validates each.
    """
    results = []
    documents = form_data.get("documents", [])

    for doc in documents:
        pdf_path = doc.get("pdf_path")
        if not pdf_path:
            results.append({'doc_type': doc.get("doc_type"), 'status': "No file path provided.", 'validation_passed': False})
            continue
        result = process_document(pdf_path, doc)
        results.append(result)

    return results


# --- Example usage ---
if __name__ == '__main__':
    form_data = {
        "documents": [
            {
                "doc_type": "Aadhaar Card",
                "pdf_path": "aadhaar.pdf",
                "name": "Anushree Kamath",
                "id_number": "973590859427"
            },
            {
                "doc_type": "PAN Card",
                "pdf_path": "pan.pdf",
                "name": "Anushree Kamath",
                "id_number": "MVKPK5101M"
            },
            {
                "doc_type": "Marksheet",
                "pdf_path": "marksheet.pdf",
                "name": "Anushree Kamath",
                "roll_number": "15160071"
            }
        ]
    }

    all_results = validate_multiple_documents(form_data)
    print("\n--- Final Validation Report ---")
    for r in all_results:
        print(f"{r['doc_type']}: {r['status']}")