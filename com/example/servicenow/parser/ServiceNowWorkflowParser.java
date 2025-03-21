package com.example.servicenow.parser;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Parser for ServiceNow workflow XML exports
 */
public class ServiceNowWorkflowParser {
    
    private Document document;
    private Map<String, WorkflowActivity> activities = new HashMap<>();
    private Map<String, WorkflowStage> stages = new HashMap<>();
    private Map<String, WorkflowCondition> conditions = new HashMap<>();
    private Map<String, List<WorkflowTransition>> transitions = new HashMap<>();
    private WorkflowVersion workflowVersion;
    
    /**
     * Parse the ServiceNow workflow XML content
     * 
     * @param xmlContent The XML content as a string
     * @throws Exception If parsing fails
     */
    public void parse(String xmlContent) throws Exception {
        // Parse the XML content
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        document = builder.parse(new InputSource(new StringReader(xmlContent)));
        document.getDocumentElement().normalize();
        
        // Parse workflow version
        parseWorkflowVersion();
        
        // Parse stages
        parseStages();
        
        // Parse activities
        parseActivities();
        
        // Parse conditions
        parseConditions();
        
        // Parse transitions
        parseTransitions();
    }
    
    private void parseWorkflowVersion() {
        NodeList nodeList = document.getElementsByTagName("wf_workflow_version");
        if (nodeList.getLength() > 0) {
            Element element = (Element) nodeList.item(0);
            
            workflowVersion = new WorkflowVersion();
            workflowVersion.setId(getElementValue(element, "sys_id"));
            workflowVersion.setName(getElementValue(element, "name"));
            workflowVersion.setTable(getElementValue(element, "table"));
            workflowVersion.setActive("true".equals(getElementValue(element, "active")));
            workflowVersion.setDescription(getElementValue(element, "description"));
            workflowVersion.setStartActivityId(getElementValue(element, "start", "display_value"));
        }
    }
    
    private void parseStages() {
        NodeList nodeList = document.getElementsByTagName("wf_stage");
        for (int i = 0; i < nodeList.getLength(); i++) {
            Element element = (Element) nodeList.item(i);
            
            WorkflowStage stage = new WorkflowStage();
            stage.setId(getElementValue(element, "sys_id"));
            stage.setName(getElementValue(element, "name"));
            stage.setValue(getElementValue(element, "value"));
            stage.setOrder(getElementValue(element, "order"));
            
            stages.put(stage.getId(), stage);
        }
    }
    
    private void parseActivities() {
        NodeList nodeList = document.getElementsByTagName("wf_activity");
        for (int i = 0; i < nodeList.getLength(); i++) {
            Element element = (Element) nodeList.item(i);
            
            WorkflowActivity activity = new WorkflowActivity();
            activity.setId(getElementValue(element, "sys_id"));
            activity.setName(getElementValue(element, "name"));
            activity.setActivityDefinition(getElementValue(element, "activity_definition", "display_value"));
            activity.setStageId(getElementValue(element, "stage", "display_value"));
            activity.setX(getElementValue(element, "x"));
            activity.setY(getElementValue(element, "y"));
            
            activities.put(activity.getId(), activity);
        }
    }
    
    private void parseConditions() {
        NodeList nodeList = document.getElementsByTagName("wf_condition");
        for (int i = 0; i < nodeList.getLength(); i++) {
            Element element = (Element) nodeList.item(i);
            
            WorkflowCondition condition = new WorkflowCondition();
            condition.setId(getElementValue(element, "sys_id"));
            condition.setName(getElementValue(element, "name"));
            condition.setActivityId(getElementValue(element, "activity", "display_value"));
            condition.setCondition(getElementValue(element, "condition"));
            condition.setOrder(getElementValue(element, "order"));
            
            conditions.put(condition.getId(), condition);
        }
    }
    
    private void parseTransitions() {
        NodeList nodeList = document.getElementsByTagName("wf_transition");
        for (int i = 0; i < nodeList.getLength(); i++) {
            Element element = (Element) nodeList.item(i);
            
            WorkflowTransition transition = new WorkflowTransition();
            transition.setId(getElementValue(element, "sys_id"));
            transition.setConditionId(getElementValue(element, "condition", "display_value"));
            transition.setFromActivityId(getElementValue(element, "from", "display_value"));
            transition.setToActivityId(getElementValue(element, "to", "display_value"));
            
            // Store transitions by source activity
            String fromActivityId = transition.getFromActivityId();
            if (!transitions.containsKey(fromActivityId)) {
                transitions.put(fromActivityId, new ArrayList<>());
            }
            transitions.get(fromActivityId).add(transition);
        }
    }
    
    /**
     * Get element text value
     */
    private String getElementValue(Element parent, String tagName) {
        NodeList nodeList = parent.getElementsByTagName(tagName);
        if (nodeList.getLength() > 0) {
            Node node = nodeList.item(0);
            if (node.getFirstChild() != null) {
                return node.getFirstChild().getNodeValue();
            }
        }
        return "";
    }
    
    /**
     * Get element attribute value
     */
    private String getElementValue(Element parent, String tagName, String attributeName) {
        NodeList nodeList = parent.getElementsByTagName(tagName);
        if (nodeList.getLength() > 0) {
            Element element = (Element) nodeList.item(0);
            return element.getAttribute(attributeName);
        }
        return "";
    }
    
    /**
     * Get parsed workflow version
     */
    public WorkflowVersion getWorkflowVersion() {
        return workflowVersion;
    }
    
    /**
     * Get all parsed activities
     */
    public Map<String, WorkflowActivity> getActivities() {
        return activities;
    }
    
    /**
     * Get all parsed stages
     */
    public Map<String, WorkflowStage> getStages() {
        return stages;
    }
    
    /**
     * Get all parsed conditions
     */
    public Map<String, WorkflowCondition> getConditions() {
        return conditions;
    }
    
    /**
     * Get all parsed transitions
     */
    public Map<String, List<WorkflowTransition>> getTransitions() {
        return transitions;
    }
    
    /**
     * Get a simplified view of the workflow
     */
    public WorkflowSummary getWorkflowSummary() {
        WorkflowSummary summary = new WorkflowSummary();
        
        summary.setName(workflowVersion.getName());
        summary.setTable(workflowVersion.getTable());
        summary.setDescription(workflowVersion.getDescription());
        
        // Get the start activity
        WorkflowActivity startActivity = activities.get(workflowVersion.getStartActivityId());
        if (startActivity != null) {
            summary.setStartActivity(startActivity.getName());
        }
        
        // Count stages and activities
        summary.setStageCount(stages.size());
        summary.setActivityCount(activities.size());
        
        // Map activities to stages
        Map<String, List<String>> stageActivities = new HashMap<>();
        for (WorkflowActivity activity : activities.values()) {
            if (activity.getStageId() != null && !activity.getStageId().isEmpty()) {
                String stageId = activity.getStageId();
                if (!stageActivities.containsKey(stageId)) {
                    stageActivities.put(stageId, new ArrayList<>());
                }
                stageActivities.get(stageId).add(activity.getName());
            }
        }
        summary.setStageActivities(stageActivities);
        
        return summary;
    }

    /**
     * ServiceNow workflow model classes
     */
    public static class WorkflowVersion {
        private String id;
        private String name;
        private String table;
        private boolean active;
        private String description;
        private String startActivityId;
        
        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getTable() { return table; }
        public void setTable(String table) { this.table = table; }
        public boolean isActive() { return active; }
        public void setActive(boolean active) { this.active = active; }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        public String getStartActivityId() { return startActivityId; }
        public void setStartActivityId(String startActivityId) { this.startActivityId = startActivityId; }
        
        @Override
        public String toString() {
            return "WorkflowVersion{" +
                    "id='" + id + '\'' +
                    ", name='" + name + '\'' +
                    ", table='" + table + '\'' +
                    ", active=" + active +
                    ", description='" + description + '\'' +
                    ", startActivityId='" + startActivityId + '\'' +
                    '}';
        }
    }
    
    public static class WorkflowStage {
        private String id;
        private String name;
        private String value;
        private String order;
        
        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getValue() { return value; }
        public void setValue(String value) { this.value = value; }
        public String getOrder() { return order; }
        public void setOrder(String order) { this.order = order; }
        
        @Override
        public String toString() {
            return "WorkflowStage{" +
                    "id='" + id + '\'' +
                    ", name='" + name + '\'' +
                    ", value='" + value + '\'' +
                    ", order='" + order + '\'' +
                    '}';
        }
    }
    
    public static class WorkflowActivity {
        private String id;
        private String name;
        private String activityDefinition;
        private String stageId;
        private String x;
        private String y;
        
        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getActivityDefinition() { return activityDefinition; }
        public void setActivityDefinition(String activityDefinition) { this.activityDefinition = activityDefinition; }
        public String getStageId() { return stageId; }
        public void setStageId(String stageId) { this.stageId = stageId; }
        public String getX() { return x; }
        public void setX(String x) { this.x = x; }
        public String getY() { return y; }
        public void setY(String y) { this.y = y; }
        
        @Override
        public String toString() {
            return "WorkflowActivity{" +
                    "id='" + id + '\'' +
                    ", name='" + name + '\'' +
                    ", activityDefinition='" + activityDefinition + '\'' +
                    ", stageId='" + stageId + '\'' +
                    ", x='" + x + '\'' +
                    ", y='" + y + '\'' +
                    '}';
        }
    }
    
    public static class WorkflowCondition {
        private String id;
        private String name;
        private String activityId;
        private String condition;
        private String order;
        
        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getActivityId() { return activityId; }
        public void setActivityId(String activityId) { this.activityId = activityId; }
        public String getCondition() { return condition; }
        public void setCondition(String condition) { this.condition = condition; }
        public String getOrder() { return order; }
        public void setOrder(String order) { this.order = order; }
        
        @Override
        public String toString() {
            return "WorkflowCondition{" +
                    "id='" + id + '\'' +
                    ", name='" + name + '\'' +
                    ", activityId='" + activityId + '\'' +
                    ", condition='" + condition + '\'' +
                    ", order='" + order + '\'' +
                    '}';
        }
    }
    
    public static class WorkflowTransition {
        private String id;
        private String conditionId;
        private String fromActivityId;
        private String toActivityId;
        
        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getConditionId() { return conditionId; }
        public void setConditionId(String conditionId) { this.conditionId = conditionId; }
        public String getFromActivityId() { return fromActivityId; }
        public void setFromActivityId(String fromActivityId) { this.fromActivityId = fromActivityId; }
        public String getToActivityId() { return toActivityId; }
        public void setToActivityId(String toActivityId) { this.toActivityId = toActivityId; }
        
        @Override
        public String toString() {
            return "WorkflowTransition{" +
                    "id='" + id + '\'' +
                    ", conditionId='" + conditionId + '\'' +
                    ", fromActivityId='" + fromActivityId + '\'' +
                    ", toActivityId='" + toActivityId + '\'' +
                    '}';
        }
    }
    
    public static class WorkflowSummary {
        private String name;
        private String table;
        private String description;
        private String startActivity;
        private int stageCount;
        private int activityCount;
        private Map<String, List<String>> stageActivities;
        
        // Getters and setters
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getTable() { return table; }
        public void setTable(String table) { this.table = table; }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        public String getStartActivity() { return startActivity; }
        public void setStartActivity(String startActivity) { this.startActivity = startActivity; }
        public int getStageCount() { return stageCount; }
        public void setStageCount(int stageCount) { this.stageCount = stageCount; }
        public int getActivityCount() { return activityCount; }
        public void setActivityCount(int activityCount) { this.activityCount = activityCount; }
        public Map<String, List<String>> getStageActivities() { return stageActivities; }
        public void setStageActivities(Map<String, List<String>> stageActivities) { this.stageActivities = stageActivities; }
        
        @Override
        public String toString() {
            return "WorkflowSummary{" +
                    "name='" + name + '\'' +
                    ", table='" + table + '\'' +
                    ", description='" + description + '\'' +
                    ", startActivity='" + startActivity + '\'' +
                    ", stageCount=" + stageCount +
                    ", activityCount=" + activityCount +
                    ", stageActivities=" + stageActivities +
                    '}';
        }
    }
}
