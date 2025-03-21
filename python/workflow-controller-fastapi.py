from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import os
import tempfile
from pydantic import BaseModel

from servicenow_workflow_parser import ServiceNowWorkflowParser

app = FastAPI(
    title="ServiceNow Workflow API",
    description="API for parsing and analyzing ServiceNow workflow XML files",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class ApiResponse(BaseModel):
    success: bool
    error: str = None


class WorkflowSummaryResponse(ApiResponse):
    summary: Dict[str, Any] = None
    version: Dict[str, Any] = None
    activityCount: int = 0
    stageCount: int = 0
    conditionCount: int = 0
    fileName: str = None


class WorkflowDetailsResponse(ApiResponse):
    version: Dict[str, Any] = None
    activities: Dict[str, Dict[str, Any]] = None
    stages: Dict[str, Dict[str, Any]] = None
    conditions: Dict[str, Dict[str, Any]] = None
    transitions: Dict[str, List[Dict[str, Any]]] = None


class WorkflowActivitiesResponse(ApiResponse):
    activities: Dict[str, Dict[str, Any]] = None
    count: int = 0


@app.post("/api/workflow/parse", response_model=WorkflowSummaryResponse)
async def parse_workflow(file: UploadFile = File(...)):
    """
    Upload and parse a ServiceNow workflow XML file.
    Returns a summary of the workflow.
    """
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            content = await file.read()
            temp.write(content)
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
            return WorkflowSummaryResponse(
                success=True,
                summary=vars(summary),
                version=vars(version),
                activityCount=len(parser.get_activities()),
                stageCount=len(parser.get_stages()),
                conditionCount=len(parser.get_conditions()),
                fileName=file.filename
            )
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/workflow/details", response_model=WorkflowDetailsResponse)
async def get_workflow_details(file: UploadFile = File(...)):
    """
    Get detailed workflow information from an uploaded file.
    Returns all workflow components.
    """
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            content = await file.read()
            temp.write(content)
            temp_path = temp.name
        
        try:
            # Parse the workflow XML
            parser = ServiceNowWorkflowParser()
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
                parser.parse(xml_content)
            
            # Prepare response with full details
            return WorkflowDetailsResponse(
                success=True,
                version=vars(parser.get_workflow_version()),
                activities={k: vars(v) for k, v in parser.get_activities().items()},
                stages={k: vars(v) for k, v in parser.get_stages().items()},
                conditions={k: vars(v) for k, v in parser.get_conditions().items()},
                transitions={
                    k: [vars(t) for t in v] for k, v in parser.get_transitions().items()
                }
            )
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/workflow/activities", response_model=WorkflowActivitiesResponse)
async def get_workflow_activities(file: UploadFile = File(...)):
    """
    Get workflow activities from an uploaded file.
    Returns just the activities from the workflow.
    """
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            content = await file.read()
            temp.write(content)
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
            return WorkflowActivitiesResponse(
                success=True,
                activities={k: vars(v) for k, v in activities.items()},
                count=len(activities)
            )
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
