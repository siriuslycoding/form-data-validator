import os
import sys
import logging
from flask import Flask, request, jsonify
from validator import validate_multiple_documents, process_document
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- TEMP FILE DIRECTORY (IMPORTANT for Render) ---
UPLOAD_FOLDER = '/tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# make logs appear reliably in Render
logging.basicConfig(level=logging.INFO, force=True)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Validator API is live"}), 200

# @app.route('/validate', methods=['POST'])
# def validate_document_endpoint():
    
#     # --- 1. Get File and Form Data ---
    
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part in the request.'}), 400
    
#     file = request.files['file']
    
#     # Get the rest of the form data
#     form_data = request.form.to_dict()

#     if file.filename == '':
#         return jsonify({'error': 'No file selected.'}), 400

#     if file:
#         # --- 2. Save File Temporarily ---
#         temp_filepath = os.path.join(UPLOAD_FOLDER, file.filename)
#         file.save(temp_filepath)

#         # --- 3. Call Your "Brain" ---
#         try:
#             # Pass the file path and the form data to your validator
#             validation_result = process_document(temp_filepath, form_data)
#         except Exception as e:
#             # Clean up file even if validation fails
#             os.remove(temp_filepath)
#             return jsonify({'error': f"An error occurred during processing: {e}"}), 500

#         # --- 4. Clean Up and Send Response ---
#         os.remove(temp_filepath) # Delete the temp file
        
#         # Send the result dictionary back to Google Apps Script
#         return jsonify(validation_result)

#     return jsonify({'error': 'Something went wrong.'}), 500


@app.route('/validate', methods=['POST'])
def validate_document_endpoint():
    app.logger.info("=== /validate hit ===")
    app.logger.info("Request form keys: %s", list(request.form.keys()))
    app.logger.info("Request files keys: %s", list(request.files.keys()))
    sys.stdout.flush()

    # --- 1. Get File and Form Data ---
    if 'file' not in request.files:
        app.logger.warning("No 'file' in request.files")
        sys.stdout.flush()
        return jsonify({'error': 'No file part in the request.'}), 400

    file = request.files['file']
    form_data = request.form.to_dict()

    if file.filename == '':
        app.logger.warning("Empty filename")
        sys.stdout.flush()
        return jsonify({'error': 'No file selected.'}), 400

    # --- 2. Save File Temporarily ---
    temp_filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(temp_filepath)
        app.logger.info("Saved temp file: %s", temp_filepath)
        sys.stdout.flush()

        # --- 3. Call your validator logic ---
        try:
            validation_result = process_document(temp_filepath, form_data)
        except Exception as e:
            app.logger.exception("Error during processing")
            sys.stdout.flush()
            return jsonify({'error': f"An error occurred during processing: {str(e)}"}), 500

        # --- 4. Clean up and return ---
        return jsonify(validation_result)

    finally:
        # Always try to remove the temp file if it exists
        try:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
                app.logger.info("Deleted temp file: %s", temp_filepath)
                sys.stdout.flush()
        except Exception:
            app.logger.exception("Failed to delete temp file")
            sys.stdout.flush()


if __name__ == '__main__':
    # Run the server. 
    # 'debug=True' reloads the server when you save changes.
    # 'host='0.0.0.0'' makes it accessible on your network (optional).
    # app.run(host='0.0.0.0', port=5000, debug=True)

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
