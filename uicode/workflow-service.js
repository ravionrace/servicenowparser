// src/services/workflowService.js
import axios from 'axios';

// Base URL for API requests - change to your Spring Boot backend URL
const API_BASE_URL = 'http://localhost:8080/api/workflow';

// Service for handling workflow API calls
const workflowService = {
  // Upload and parse workflow XML
  parseWorkflow: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/parse`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error parsing workflow:', error);
      throw error;
    }
  },
  
  // Get detailed workflow information
  getWorkflowDetails: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/details`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting workflow details:', error);
      throw error;
    }
  }
};

export default workflowService;

// src/utils/workflowParser.js
// Client-side parser for local XML parsing (fallback if backend is not available)
export const parseWorkflowXml = (xmlString) => {
  const parser = new DOMParser();
  const xmlDoc = parser.parseFromString(xmlString, "text/xml");
  
  // Parse workflow version
  const workflowVersion = parseWorkflowVersion(xmlDoc);
  
  // Parse stages
  const stages = parseStages(xmlDoc);
  
  // Parse activities
  const activities = parseActivities(xmlDoc);
  
  // Parse conditions
  const conditions = parseConditions(xmlDoc);
  
  // Parse transitions
  const transitions = parseTransitions(xmlDoc);
  
  return {
    workflowVersion,
    stages,
    activities,
    conditions,
    transitions
  };
};

const parseWorkflowVersion = (xmlDoc) => {
  const versionNode = xmlDoc.querySelector("wf_workflow_version");
  if (!versionNode) return null;
  
  return {
    id: getElementValue(versionNode, "sys_id"),
    name: getElementValue(versionNode, "name"),
    table: getElementValue(versionNode, "table"),
    active: getElementValue(versionNode, "active") === "true",
    description: getElementValue(versionNode, "description"),
    startActivityId: getAttributeValue(versionNode.querySelector("start"), "display_value")
  };
};

const parseStages = (xmlDoc) => {
  const stages = {};
  const stageNodes = xmlDoc.querySelectorAll("wf_stage");
  
  stageNodes.forEach(node => {
    const id = getElementValue(node, "sys_id");
    stages[id] = {
      id,
      name: getElementValue(node, "name"),
      value: getElementValue(node, "value"),
      order: getElementValue(node, "order")
    };
  });
  
  return stages;
};

const parseActivities = (xmlDoc) => {
  const activities = {};
  const activityNodes = xmlDoc.querySelectorAll("wf_activity");
  
  activityNodes.forEach(node => {
    const id = getElementValue(node, "sys_id");
    activities[id] = {
      id,
      name: getElementValue(node, "name"),
      activityDefinition: getAttributeValue(node.querySelector("activity_definition"), "display_value"),
      stageId: getAttributeValue(node.querySelector("stage"), "display_value"),
      x: getElementValue(node, "x"),
      y: getElementValue(node, "y")
    };
  });
  
  return activities;
};

const parseConditions = (xmlDoc) => {
  const conditions = {};
  const conditionNodes = xmlDoc.querySelectorAll("wf_condition");
  
  conditionNodes.forEach(node => {
    const id = getElementValue(node, "sys_id");
    conditions[id] = {
      id,
      name: getElementValue(node, "name"),
      activityId: getAttributeValue(node.querySelector("activity"), "display_value"),
      condition: getElementValue(node, "condition"),
      order: getElementValue(node, "order")
    };
  });
  
  return conditions;
};

const parseTransitions = (xmlDoc) => {
  const transitions = {};
  const transitionNodes = xmlDoc.querySelectorAll("wf_transition");
  
  transitionNodes.forEach(node => {
    const id = getElementValue(node, "sys_id");
    const fromActivityId = getAttributeValue(node.querySelector("from"), "display_value");
    
    if (!transitions[fromActivityId]) {
      transitions[fromActivityId] = [];
    }
    
    transitions[fromActivityId].push({
      id,
      conditionId: getAttributeValue(node.querySelector("condition"), "display_value"),
      fromActivityId,
      toActivityId: getAttributeValue(node.querySelector("to"), "display_value")
    });
  });
  
  return transitions;
};

// Helper function to get element text content
const getElementValue = (parent, tagName) => {
  const element = parent.querySelector(tagName);
  return element ? element.textContent : '';
};

// Helper function to get element attribute value
const getAttributeValue = (element, attributeName) => {
  return element ? element.getAttribute(attributeName) : '';
};
