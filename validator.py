import re
from pdf2image import convert_from_path
import pytesseract

# --- Optional: If Tesseract isn't in your system's PATH ---
# On Windows, you might need this:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def process_document(pdf_path, form_data):
    """
    Validates a PDF document against data from a form.

    :param pdf_path: The file path to the uploaded PDF.
    :param form_data: A dictionary of data from the Google Form.
                      (e.g., {'name': 'John Doe', 'id_number': '12345678', 'doc_type': 'Aadhaar Card'})
    :return: A dictionary with the validation status and result.
    """
    
    print(f"Processing document for: {form_data.get('name')}")

    try:
        # 1. Convert PDF to a list of images
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return {'status': f"Error: Could not read PDF file. {e}", 'validation_passed': False}

    full_text = ""
    for img in images:
        # 2. Use Tesseract to get text from each image
        # full_text += pytesseract.image_to_string(img)
        
        # Tell Tesseract to look for BOTH English ('eng') and Hindi ('hin')
        full_text += pytesseract.image_to_string(img, lang='eng+hin')
    
    # Normalize text for easier matching (all lowercase)
    full_text = full_text.lower()
    print("--- TESSERACT'S OUTPUT ---")
    print(full_text)
    print("----------------------------")

    # --- 3. PERFORM VALIDATION LOGIC ---
    
    # Get form data, using .get() to avoid errors if a field is missing
    name_from_form = form_data.get('name', '').lower()
    id_from_form = form_data.get('id_number', '').lower()
    expected_doc_type = form_data.get('doc_type', '').lower() # e.g., "aadhar card"

    # Validation 1: Check if the document type keyword exists
    # if expected_doc_type and expected_doc_type not in full_text:
    #     print(f"Validation FAILED: Document type '{expected_doc_type}' not found.")
    #     return {
    #         'status': f"Mismatch ❌: Document does not seem to be an '{expected_doc_type}'.",
    #         'validation_passed': False
    #     }

    # Validation 1: Check if the document type keyword exists
    if expected_doc_type == 'aadhaar card':
        # Look for EITHER the English word OR the Hindi word
        if 'aadhaar' not in full_text and 'आधार' not in full_text:
            print(f"Validation FAILED: Keyword 'aadhaar' or 'आधार' not found.")
            return {
                'status': f"Mismatch ❌: Document does not seem to be an '{expected_doc_type}'.",
                'validation_passed': False
            }
    # (Optional) You can add 'else if' blocks here for 'pan card', etc.

    # Validation 2: Check if the Name from the form is in the document
    # Note: This is a simple check. Regex is better for specific fields.
    if name_from_form and name_from_form not in full_text:
        print(f"Validation FAILED: Name '{name_from_form}' not found.")
        return {
            'status': f"Mismatch ❌: Name '{name_from_form}' not found in the document.",
            'validation_passed': False
        }

    # Validation 3: Check if the ID Number from the form is in the document
    # Validation 3: Check if the ID Number from the form is in the document
    if id_from_form:
        # Remove all spaces from both strings before comparing
        id_from_form_clean = id_from_form.replace(' ', '')
        full_text_clean = full_text.replace(' ', '')
        
        if id_from_form_clean not in full_text_clean:
            print(f"Validation FAILED: ID Number '{id_from_form_clean}' not found.")
            return {
                'status': f"Mismatch ❌: ID Number '{id_from_form_clean}' not found in the document.",
                'validation_passed': False
            }

    # --- 4. If all checks pass ---
    print("Validation SUCCESSFUL")
    return {
        'status': 'Valid ✅: All data matches the document.',
        'validation_passed': True
    }


# --- Use this block to test your function locally ---
if __name__ == '__main__':
    
    # Create a test PDF named 'test.pdf' with some text
    # For example: "This is an Aadhaar Card. Name: John Doe. ID: 12345678"
    
    sample_pdf = 'aadhaar.pdf' 
    sample_form_data = {
        'name': 'Anushree Kamath',
        'id_number': '973590859427',
        'doc_type': 'Aadhaar Card'
    }
    
    result = process_document(sample_pdf, sample_form_data)
    print("\n--- Test Result ---")
    print(result)