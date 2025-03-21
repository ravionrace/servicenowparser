import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class WorkflowVersion:
    """ServiceNow workflow version model."""
    id: str = ""
    name: str = ""
    table: str = ""
    active: bool = False
    description: str = ""
    start_activity_id: str = ""
    
    def __str__(self) -> str:
        return (f"WorkflowVersion(id='{self.id}', name='{self.name}', table='{self.table}', "
                f"active={self.active}, description='{self.description}', "
                f"start_activity_id='{self.start_activity_id}')")


@dataclass
class WorkflowStage:
    """ServiceNow workflow stage model."""
    id: str = ""
    name: str = ""
    value: str = ""
    order: str = ""
    
    def __str__(self) -> str:
        return (f"WorkflowStage(id='{self.id}', name='{self.name}', value='{self.value}', "
                f"order='{self.order}')")


@dataclass
class WorkflowActivity:
    """ServiceNow workflow activity model."""
    id: str = ""
    name: str = ""
    activity_definition: str = ""
    stage_id: str = ""
    x: str = ""
    y: str = ""
    
    def __str__(self) -> str:
        return (f"WorkflowActivity(id='{self.id}', name='{self.name}', "
                f"activity_definition='{self.activity_definition}', stage_id='{self.stage_id}', "
                f"x='{self.x}', y='{self.y}')")


@dataclass
class WorkflowCondition:
    """ServiceNow workflow condition model."""
    id: str = ""
    name: str = ""
    activity_id: str = ""
    condition: str = ""
    order: str = ""
    
    def __str__(self) -> str:
        return (f"WorkflowCondition(id='{self.id}', name='{self.name}', "
                f"activity_id='{self.activity_id}', condition='{self.condition}', "
                f"order='{self.order}')")


@dataclass
class WorkflowTransition:
    """ServiceNow workflow transition model."""
    id: str = ""
    condition_id: str = ""
    from_activity_id: str = ""
    to_activity_id: str = ""
    
    def __str__(self) -> str:
        return (f"WorkflowTransition(id='{self.id}', condition_id='{self.condition_id}', "
                f"from_activity_id='{self.from_activity_id}', to_activity_id='{self.to_activity_id}')")


@dataclass
class WorkflowSummary:
    """ServiceNow workflow summary model."""
    name: str = ""
    table: str = ""
    description: str = ""
    start_activity: str = ""
    stage_count: int = 0
    activity_count: int = 0
    stage_activities: Dict[str, List[str]] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return (f"WorkflowSummary(name='{self.name}', table='{self.table}', "
                f"description='{self.description}', start_activity='{self.start_activity}', "
                f"stage_count={self.stage_count}, activity_count={self.activity_count}, "
                f"stage_activities={self.stage_activities})")


class ServiceNowWorkflowParser:
    """Parser for ServiceNow workflow XML exports."""
    
    def __init__(self):
        self.document = None
        self.activities = {}
        self.stages = {}
        self.conditions = {}
        self.transitions = {}
        self.workflow_version = None
    
    def parse(self, xml_content: str) -> None:
        """
        Parse the ServiceNow workflow XML content.
        
        Args:
            xml_content: The XML content as a string
        """
        # Parse the XML content
        self.document = ET.fromstring(xml_content)
        
        # Parse workflow version
        self._parse_workflow_version()
        
        # Parse stages
        self._parse_stages()
        
        # Parse activities
        self._parse_activities()
        
        # Parse conditions
        self._parse_conditions()
        
        # Parse transitions
        self._parse_transitions()
    
    def _parse_workflow_version(self) -> None:
        """Parse workflow version information."""
        version_elements = self.document.findall(".//wf_workflow_version")
        if version_elements:
            element = version_elements[0]
            
            self.workflow_version = WorkflowVersion(
                id=self._get_element_value(element, "sys_id"),
                name=self._get_element_value(element, "name"),
                table=self._get_element_value(element, "table"),
                active=self._get_element_value(element, "active") == "true",
                description=self._get_element_value(element, "description"),
                start_activity_id=self._get_element_attribute(element, "start", "display_value")
            )
    
    def _parse_stages(self) -> None:
        """Parse workflow stages."""
        stage_elements = self.document.findall(".//wf_stage")
        for element in stage_elements:
            stage_id = self._get_element_value(element, "sys_id")
            
            stage = WorkflowStage(
                id=stage_id,
                name=self._get_element_value(element, "name"),
                value=self._get_element_value(element, "value"),
                order=self._get_element_value(element, "order")
            )
            
            self.stages[stage_id] = stage
    
    def _parse_activities(self) -> None:
        """Parse workflow activities."""
        activity_elements = self.document.findall(".//wf_activity")
        for element in activity_elements:
            activity_id = self._get_element_value(element, "sys_id")
            
            activity = WorkflowActivity(
                id=activity_id,
                name=self._get_element_value(element, "name"),
                activity_definition=self._get_element_attribute(element, "activity_definition", "display_value"),
                stage_id=self._get_element_attribute(element, "stage", "display_value"),
                x=self._get_element_value(element, "x"),
                y=self._get_element_value(element, "y")
            )
            
            self.activities[activity_id] = activity
    
    def _parse_conditions(self) -> None:
        """Parse workflow conditions."""
        condition_elements = self.document.findall(".//wf_condition")
        for element in condition_elements:
            condition_id = self._get_element_value(element, "sys_id")
            
            condition = WorkflowCondition(
                id=condition_id,
                name=self._get_element_value(element, "name"),
                activity_id=self._get_element_attribute(element, "activity", "display_value"),
                condition=self._get_element_value(element, "condition"),
                order=self._get_element_value(element, "order")
            )
            
            self.conditions[condition_id] = condition
    
    def _parse_transitions(self) -> None:
        """Parse workflow transitions."""
        transition_elements = self.document.findall(".//wf_transition")
        for element in transition_elements:
            transition_id = self._get_element_value(element, "sys_id")
            from_activity_id = self._get_element_attribute(element, "from", "display_value")
            
            transition = WorkflowTransition(
                id=transition_id,
                condition_id=self._get_element_attribute(element, "condition", "display_value"),
                from_activity_id=from_activity_id,
                to_activity_id=self._get_element_attribute(element, "to", "display_value")
            )
            
            # Store transitions by source activity
            if from_activity_id not in self.transitions:
                self.transitions[from_activity_id] = []
            
            self.transitions[from_activity_id].append(transition)
    
    def _get_element_value(self, parent: ET.Element, tag_name: str) -> str:
        """
        Get element text value.
        
        Args:
            parent: Parent element
            tag_name: Tag name to find
            
        Returns:
            Text content of the element or empty string
        """
        element = parent.find(f".//{tag_name}")
        if element is not None and element.text is not None:
            return element.text.strip()
        return ""
    
    def _get_element_attribute(self, parent: ET.Element, tag_name: str, attribute_name: str) -> str:
        """
        Get element attribute value.
        
        Args:
            parent: Parent element
            tag_name: Tag name to find
            attribute_name: Attribute name to get
            
        Returns:
            Attribute value of the element or empty string
        """
        element = parent.find(f".//{tag_name}")
        if element is not None and attribute_name in element.attrib:
            return element.attrib[attribute_name]
        return ""
    
    def get_workflow_version(self) -> WorkflowVersion:
        """Get parsed workflow version."""
        return self.workflow_version
    
    def get_activities(self) -> Dict[str, WorkflowActivity]:
        """Get all parsed activities."""
        return self.activities
    
    def get_stages(self) -> Dict[str, WorkflowStage]:
        """Get all parsed stages."""
        return self.stages
    
    def get_conditions(self) -> Dict[str, WorkflowCondition]:
        """Get all parsed conditions."""
        return self.conditions
    
    def get_transitions(self) -> Dict[str, List[WorkflowTransition]]:
        """Get all parsed transitions."""
        return self.transitions
    
    def get_workflow_summary(self) -> WorkflowSummary:
        """Get a simplified view of the workflow."""
        summary = WorkflowSummary()
        
        if self.workflow_version:
            summary.name = self.workflow_version.name
            summary.table = self.workflow_version.table
            summary.description = self.workflow_version.description
            
            # Get the start activity
            start_activity = self.activities.get(self.workflow_version.start_activity_id)
            if start_activity:
                summary.start_activity = start_activity.name
            
            # Count stages and activities
            summary.stage_count = len(self.stages)
            summary.activity_count = len(self.activities)
            
            # Map activities to stages
            stage_activities = {}
            for activity in self.activities.values():
                if activity.stage_id and activity.stage_id != "":
                    if activity.stage_id not in stage_activities:
                        stage_activities[activity.stage_id] = []
                    stage_activities[activity.stage_id].append(activity.name)
            
            summary.stage_activities = stage_activities
        
        return summary


def parse_workflow_file(file_path: str) -> ServiceNowWorkflowParser:
    """
    Parse a ServiceNow workflow XML file.
    
    Args:
        file_path: Path to the XML file
        
    Returns:
        Initialized parser with parsed workflow data
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    
    parser = ServiceNowWorkflowParser()
    parser.parse(xml_content)
    return parser


if __name__ == "__main__":
    import sys
    import json
    
    # Check if file path is provided
    if len(sys.argv) < 2:
        print("Please provide the path to the ServiceNow workflow XML file")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Parse the workflow XML
        parser = parse_workflow_file(file_path)
        
        # Get workflow details
        version = parser.get_workflow_version()
        activities = parser.get_activities()
        stages = parser.get_stages()
        conditions = parser.get_conditions()
        transitions = parser.get_transitions()
        summary = parser.get_workflow_summary()
        
        # Print workflow summary
        print("===== Workflow Summary =====")
        print(f"Name: {summary.name}")
        print(f"Table: {summary.table}")
        print(f"Description: {summary.description if summary.description else 'N/A'}")
        print(f"Start Activity: {summary.start_activity}")
        print(f"Stages: {summary.stage_count}")
        print(f"Activities: {summary.activity_count}")
        
        # Print workflow version details
        print("\n===== Workflow Version =====")
        print(version)
        
        # Print activities
        print("\n===== Activities =====")
        for activity in activities.values():
            print(activity)
        
        # Print stages
        print("\n===== Stages =====")
        for stage in stages.values():
            print(stage)
        
        # Print conditions
        print("\n===== Conditions =====")
        for condition in conditions.values():
            print(condition)
        
        # Print transitions
        print("\n===== Transitions =====")
        for from_activity_id, transition_list in transitions.items():
            from_activity = activities.get(from_activity_id)
            print(f"From: {from_activity.name if from_activity else from_activity_id}")
            
            for transition in transition_list:
                to_activity = activities.get(transition.to_activity_id)
                condition = conditions.get(transition.condition_id)
                
                print(f"  To: {to_activity.name if to_activity else transition.to_activity_id} | "
                      f"Condition: {condition.name if condition else transition.condition_id}")
        
    except Exception as e:
        print(f"Error parsing workflow XML: {e}")
        import traceback
        traceback.print_exc()
