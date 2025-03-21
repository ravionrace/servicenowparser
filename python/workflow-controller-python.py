from flask import Flask, request, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
from servicenow_workflow_parser import ServiceNowWorkflowParser

app = Flask(__name__)

# Configure maximum file size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/api/workflow/parse', methods=['POST'])
def parse_workflow():
    """
    Upload and parse a ServiceNow workflow XML file.
    Returns a summary of the workflow.
    """
    try:
        # Check if file was provided
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            file.save(temp.name)
            temp_path = temp.name
        
        try:
            # Parse the workflow XML
            parser = ServiceNowWorkflowParser()
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
                parser.parse(xml_content)
            
            # Get workflow summary
            summary = parser.get_workflow_summary()
            version = parser.get_workflow_version()
            
            # Prepare response
            response = {
                'success': True,
                'summary': vars(summary),
                'version': vars(version),
                'activityCount': len(parser.get_activities()),
                'stageCount': len(parser.get_stages()),
                'conditionCount': len(parser.get_conditions()),
                'fileName': secure_filename(file.filename)
            }
            
            return jsonify(response), 200
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/workflow/details', methods=['POST'])
def get_workflow_details():
    """
    Get detailed workflow information from an uploaded file.
    Returns all workflow components.
    """
    try:
        # Check if file was provided
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            file.save(temp.name)
            temp_path = temp.name
        
        try:
            # Parse the workflow XML
            parser = ServiceNowWorkflowParser()
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
                parser.parse(xml_content)
            
            # Prepare response with full details
            response = {
                'success': True,
                'version': vars(parser.get_workflow_version()),
                'activities': {k: vars(v) for k, v in parser.get_activities().items()},
                'stages': {k: vars(v) for k, v in parser.get_stages().items()},
                'conditions': {k: vars(v) for k, v in parser.get_conditions().items()},
                'transitions': {
                    k: [vars(t) for t in v] for k, v in parser.get_transitions().items()
                }
            }
            
            return jsonify(response), 200
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/workflow/activities', methods=['POST'])
def get_workflow_activities():
    """
    Get workflow activities from an uploaded file.
    Returns just the activities from the workflow.
    """
    try:
        # Check if file was provided
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            file.save(temp.name)
            temp_path = temp.name
        
        try:
            # Parse the workflow XML
            parser = ServiceNowWorkflowParser()
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
                parser.parse(xml_content)
            
            # Get activities
            activities = parser.get_activities()
            
            # Prepare response
            response = {
                'success': True,
                'activities': {k: vars(v) for k, v in activities.items()},
                'count': len(activities)
            }
            
            return jsonify(response), 200
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Enable CORS for development
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response


if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)
