import os
from flask import Flask, request, jsonify
from validator import validate_multiple_documents
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
def validate_multiple():
    results = []
    
    # Iterate over all uploaded files
    for key, file in request.files.items():
        if not file:
            continue
        
        # Each file will have a corresponding metadata key
        meta_key = f"meta_{key}"
        form_meta = request.form.get(meta_key)
        
        # Convert JSON string to Python dict
        import json
        meta = json.loads(form_meta)
        
        temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(temp_path)
        
        result = process_document(temp_path, meta)
        os.remove(temp_path)
        results.append(result)
    
    return jsonify({"documents": results})

if __name__ == '__main__':
    # Run the server. 
    # 'debug=True' reloads the server when you save changes.
    # 'host='0.0.0.0'' makes it accessible on your network (optional).
    # app.run(host='0.0.0.0', port=5000, debug=True)

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
