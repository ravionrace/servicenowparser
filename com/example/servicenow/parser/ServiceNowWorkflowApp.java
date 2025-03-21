package com.example.servicenow;

import com.example.servicenow.parser.ServiceNowWorkflowParser;
import com.example.servicenow.parser.ServiceNowWorkflowParser.WorkflowActivity;
import com.example.servicenow.parser.ServiceNowWorkflowParser.WorkflowCondition;
import com.example.servicenow.parser.ServiceNowWorkflowParser.WorkflowStage;
import com.example.servicenow.parser.ServiceNowWorkflowParser.WorkflowSummary;
import com.example.servicenow.parser.ServiceNowWorkflowParser.WorkflowTransition;
import com.example.servicenow.parser.ServiceNowWorkflowParser.WorkflowVersion;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;

public class ServiceNowWorkflowApp {

    public static void main(String[] args) {
        try {
            // Check if file path is provided
            if (args.length < 1) {
                System.out.println("Please provide the path to the ServiceNow workflow XML file");
                return;
            }
            
            String filePath = args[0];
            String xmlContent = readFile(filePath);
            
            // Parse the workflow XML
            ServiceNowWorkflowParser parser = new ServiceNowWorkflowParser();
            parser.parse(xmlContent);
            
            // Get workflow details
            WorkflowVersion version = parser.getWorkflowVersion();
            Map<String, WorkflowActivity> activities = parser.getActivities();
            Map<String, WorkflowStage> stages = parser.getStages();
            Map<String, WorkflowCondition> conditions = parser.getConditions();
            Map<String, List<WorkflowTransition>> transitions = parser.getTransitions();
            WorkflowSummary summary = parser.getWorkflowSummary();
            
            // Print workflow summary
            System.out.println("===== Workflow Summary =====");
            System.out.println("Name: " + summary.getName());
            System.out.println("Table: " + summary.getTable());
            System.out.println("Description: " + (summary.getDescription() != null && !summary.getDescription().isEmpty() ? summary.getDescription() : "N/A"));
            System.out.println("Start Activity: " + summary.getStartActivity());
            System.out.println("Stages: " + summary.getStageCount());
            System.out.println("Activities: " + summary.getActivityCount());
            
            // Print workflow version details
            System.out.println("\n===== Workflow Version =====");
            System.out.println(version);
            
            // Print activities
            System.out.println("\n===== Activities =====");
            for (WorkflowActivity activity : activities.values()) {
                System.out.println(activity);
            }
            
            // Print stages
            System.out.println("\n===== Stages =====");
            for (WorkflowStage stage : stages.values()) {
                System.out.println(stage);
            }
            
            // Print conditions
            System.out.println("\n===== Conditions =====");
            for (WorkflowCondition condition : conditions.values()) {
                System.out.println(condition);
            }
            
            // Print transitions
            System.out.println("\n===== Transitions =====");
            for (Map.Entry<String, List<WorkflowTransition>> entry : transitions.entrySet()) {
                String fromActivityId = entry.getKey();
                WorkflowActivity fromActivity = activities.get(fromActivityId);
                System.out.println("From: " + (fromActivity != null ? fromActivity.getName() : fromActivityId));
                
                for (WorkflowTransition transition : entry.getValue()) {
                    WorkflowActivity toActivity = activities.get(transition.getToActivityId());
                    WorkflowCondition condition = conditions.get(transition.getConditionId());
                    
                    System.out.println("  To: " + (toActivity != null ? toActivity.getName() : transition.getToActivityId()) +
                            " | Condition: " + (condition != null ? condition.getName() : transition.getConditionId()));
                }
            }
            
            // Generate workflow path
            System.out.println("\n===== Workflow Path =====");
            String startActivityId = version.getStartActivityId();
            generatePath(startActivityId, activities, transitions, conditions, "");
            
        } catch (Exception e) {
            System.err.println("Error parsing workflow XML: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Read file content to string
     */
    private static String readFile(String filePath) throws IOException {
        return new String(Files.readAllBytes(Paths.get(filePath)));
    }
    
    /**
     * Generate workflow path recursively
     */
    private static void generatePath(String activityId, 
                                    Map<String, WorkflowActivity> activities,
                                    Map<String, List<WorkflowTransition>> transitions,
                                    Map<String, WorkflowCondition> conditions,
                                    String indent) {
        
        // Get activity
        WorkflowActivity activity = activities.get(activityId);
        if (activity == null) {
            System.out.println(indent + "Unknown Activity: " + activityId);
            return;
        }
        
        // Print current activity
        System.out.println(indent + "Activity: " + activity.getName());
        
        // Get transitions from this activity
        List<WorkflowTransition> activityTransitions = transitions.get(activityId);
        if (activityTransitions == null || activityTransitions.isEmpty()) {
            System.out.println(indent + "  (End of path)");
            return;
        }
        
        // Follow each transition
        for (WorkflowTransition transition : activityTransitions) {
            WorkflowCondition condition = conditions.get(transition.getConditionId());
            String conditionName = condition != null ? condition.getName() : "Unknown";
            
            System.out.println(indent + "  → [" + conditionName + "]");
            
            // Follow the path recursively (avoiding infinite loops by limiting depth)
            if (indent.length() < 20) {  // Simple cycle prevention
                generatePath(transition.getToActivityId(), activities, transitions, conditions, indent + "    ");
            } else {
                System.out.println(indent + "    ... (path continues)");
            }
        }
    }
}
