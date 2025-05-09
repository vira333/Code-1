from flask import Flask, request, make_response
from main import extract_text_from_pdf, generate_jira_epic, generate_jira_stories
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Flask API endpoint to upload document, accept user requirements, and generate Epic
@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return make_response("Error: No file provided\n", 400)
        file = request.files['file']
        if file.filename == '':
            return make_response("Error: No file selected\n", 400)

        # Get user requirements from form data
        user_requirements = request.form.get('user_requirements')
        if not user_requirements:
            return make_response("Error: User requirements are required\n", 400)

        # Save uploaded file
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        # Extract text
        text = extract_text_from_pdf(file_path)

        # Generate Jira Epic with user requirements
        epic_data = generate_jira_epic(text, user_requirements)

        # Format response as plain text
        response_text = (
            "Epic Generated Successfully\n"
            "====================\n"
            f"Epic Key: {epic_data['key']}\n"
            f"Title: {epic_data['title']}\n"
            f"Description: {epic_data['description']}\n"
            "====================\n"
        )
        return make_response(response_text, 200)
    except Exception as e:
        logger.error(f"Error in upload_document: {e}")
        return make_response(f"Error: {str(e)}\n", 500)

# Flask API endpoint to generate Stories from Epic
@app.route('/api/generate-stories', methods=['POST'])
def generate_stories():
    try:
        data = request.get_json()
        epic_key = data.get("epic_key")
        epic_description = data.get("epic_description")

        if not all([epic_key, epic_description]):
            return make_response("Error: Missing required fields (epic_key, epic_description)\n", 400)

        # Generate Jira Stories
        stories_data = generate_jira_stories(epic_description)

        # Format response as plain text
        response_text = (
            "Stories Generated Successfully\n"
            "====================\n"
            f"Epic Key: {epic_key}\n"
            "Stories:\n"
        )
        for i, story in enumerate(stories_data, 1):
            response_text += (
                f"\nStory {i}:\n"
                f"  Key: {story['key']}\n"
                f"  Title: {story['title']}\n"
                f"  Description: {story['description']}\n"
            )
        response_text += "====================\n"
        return make_response(response_text, 200)
    except Exception as e:
        logger.error(f"Error in generate_stories: {e}")
        return make_response(f"Error: {str(e)}\n", 500)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
