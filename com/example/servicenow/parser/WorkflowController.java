package com.example.servicenow.controller;

import com.example.servicenow.parser.ServiceNowWorkflowParser;
import com.example.servicenow.parser.ServiceNowWorkflowParser.WorkflowActivity;
import com.example.servicenow.parser.ServiceNowWorkflowParser.WorkflowSummary;
import com.example.servicenow.parser.ServiceNowWorkflowParser.WorkflowVersion;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/workflow")
public class WorkflowController {

    /**
     * Upload and parse a ServiceNow workflow XML file
     */
    @PostMapping("/parse")
    public ResponseEntity<Map<String, Object>> parseWorkflow(@RequestParam("file") MultipartFile file) {
        try {
            // Read file content
            String xmlContent = new String(file.getBytes());
            
            // Parse workflow
            ServiceNowWorkflowParser parser = new ServiceNowWorkflowParser();
            parser.parse(xmlContent);
            
            // Get workflow summary
            WorkflowSummary summary = parser.getWorkflowSummary();
            WorkflowVersion version = parser.getWorkflowVersion();
            
            // Prepare response
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("summary", summary);
            response.put("version", version);
            response.put("activityCount", parser.getActivities().size());
            response.put("stageCount", parser.getStages().size());
            response.put("conditionCount", parser.getConditions().size());
            response.put("fileName", file.getOriginalFilename());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
        }
    }
    
    /**
     * Get detailed workflow information
     */
    @PostMapping("/details")
    public ResponseEntity<Map<String, Object>> getWorkflowDetails(@RequestParam("file") MultipartFile file) {
        try {
            // Read file content
            String xmlContent = new String(file.getBytes());
            
            // Parse workflow
            ServiceNowWorkflowParser parser = new ServiceNowWorkflowParser();
            parser.parse(xmlContent);
            
            // Prepare response with full details
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("version", parser.getWorkflowVersion());
            response.put("activities", parser.getActivities());
            response.put("stages", parser.getStages());
            response.put("conditions", parser.getConditions());
            response.put("transitions", parser.getTransitions());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
        }
    }
    
    /**
     * Get workflow activities
     */
    @PostMapping("/activities")
    public ResponseEntity<Map<String, Object>> getWorkflowActivities(@RequestParam("file") MultipartFile file) {
        try {
            // Read file content
            String xmlContent = new String(file.getBytes());
            
            // Parse workflow
            ServiceNowWorkflowParser parser = new ServiceNowWorkflowParser();
            parser.parse(xmlContent);
            
            // Get activities
            Map<String, WorkflowActivity> activities = parser.getActivities();
            
            // Prepare response
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("activities", activities);
            response.put("count", activities.size());
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
        }
    }
    
    /**
     * Error handler for file upload errors
     */
    @ExceptionHandler(IOException.class)
    public ResponseEntity<Map<String, Object>> handleIOException(IOException e) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("success", false);
        errorResponse.put("error", "Failed to process file: " + e.getMessage());
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
    }
}
