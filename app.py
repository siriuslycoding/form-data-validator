import os
from flask import Flask, request, jsonify
from validator import process_document # Import your function from the other file

app = Flask(__name__)

# Create a folder to temporarily store uploads
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/validate', methods=['POST'])
def validate_document_endpoint():
    
    # --- 1. Get File and Form Data ---
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request.'}), 400
    
    file = request.files['file']
    
    # Get the rest of the form data
    form_data = request.form.to_dict()

    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if file:
        # --- 2. Save File Temporarily ---
        temp_filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(temp_filepath)

        # --- 3. Call Your "Brain" ---
        try:
            # Pass the file path and the form data to your validator
            validation_result = process_document(temp_filepath, form_data)
        except Exception as e:
            # Clean up file even if validation fails
            os.remove(temp_filepath)
            return jsonify({'error': f"An error occurred during processing: {e}"}), 500

        # --- 4. Clean Up and Send Response ---
        os.remove(temp_filepath) # Delete the temp file
        
        # Send the result dictionary back to Google Apps Script
        return jsonify(validation_result)

    return jsonify({'error': 'Something went wrong.'}), 500


if __name__ == '__main__':
    # Run the server. 
    # 'debug=True' reloads the server when you save changes.
    # 'host='0.0.0.0'' makes it accessible on your network (optional).
    # app.run(host='0.0.0.0', port=5000, debug=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
