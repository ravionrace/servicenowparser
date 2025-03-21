#!/usr/bin/env python3
"""
ServiceNow Workflow Parser Application

A command-line application to parse and visualize ServiceNow workflow XML files.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple

from servicenow_workflow_parser import (
    ServiceNowWorkflowParser, 
    WorkflowActivity, 
    WorkflowCondition,
    parse_workflow_file
)


def generate_path(
    activity_id: str,
    activities: Dict[str, WorkflowActivity],
    transitions: Dict[str, List[Any]],
    conditions: Dict[str, WorkflowCondition],
    indent: str = "",
    visited: Optional[List[str]] = None
) -> None:
    """
    Generate workflow path recursively.
    
    Args:
        activity_id: Current activity ID
        activities: Dictionary of activities
        transitions: Dictionary of transitions
        conditions: Dictionary of conditions
        indent: String indentation for current level
        visited: List of already visited activity IDs to prevent cycles
    """
    if visited is None:
        visited = []
    
    # Prevent infinite loops
    if activity_id in visited:
        print(f"{indent}... (cycle detected, already visited {activity_id})")
        return
    
    visited.append(activity_id)
    
    # Get activity
    activity = activities.get(activity_id)
    if not activity:
        print(f"{indent}Unknown Activity: {activity_id}")
        return
    
    # Print current activity
    print(f"{indent}Activity: {activity.name}")
    
    # Get transitions from this activity
    activity_transitions = transitions.get(activity_id, [])
    if not activity_transitions:
        print(f"{indent}  (End of path)")
        return
    
    # Follow each transition
    for transition in activity_transitions:
        condition = conditions.get(transition.condition_id)
        condition_name = condition.name if condition else "Unknown"
        
        print(f"{indent}  → [{condition_name}]")
        
        # Follow the path recursively (avoiding infinite loops)
        if len(indent) < 40:  # Simple depth limitation for readability
            generate_path(
                transition.to_activity_id,
                activities,
                transitions,
                conditions,
                indent + "    ",
                visited.copy()  # Create a copy to avoid modifying parent's visited list
            )
        else:
            print(f"{indent}    ... (path continues, max depth reached)")


def visualize_workflow(parser: ServiceNowWorkflowParser) -> None:
    """
    Create a simple ASCII visualization of the workflow.
    
    Args:
        parser: Initialized workflow parser with data
    """
    workflow = parser.get_workflow_version()
    activities = parser.get_activities()
    transitions = parser.get_transitions()
    
    # Get the start activity
    start_id = workflow.start_activity_id
    start_activity = activities.get(start_id)
    
    if not start_activity:
        print("Could not find start activity")
        return
    
    print(f"\nWorkflow: {workflow.name}\n")
    print("Start")
    print("  ↓")
    
    # Track visited activities to prevent cycles
    visited = set()
    
    # Recursively print the workflow path
    def print_path(activity_id: str, depth: int = 0) -> None:
        if activity_id in visited:
            print("  " * depth + "↓")
            print("  " * depth + "(cycle detected)")
            return
        
        visited.add(activity_id)
        
        activity = activities.get(activity_id)
        if not activity:
            return
        
        print("  " * depth + "↓")
        print("  " * depth + f"[{activity.name}]")
        
        activity_transitions = transitions.get(activity_id, [])
        if not activity_transitions:
            return
        
        # More than one outgoing transition creates branches
        if len(activity_transitions) > 1:
            for i, transition in enumerate(activity_transitions):
                to_id = transition.to_activity_id
                to_activity = activities.get(to_id)
                if not to_activity:
                    continue
                
                print("  " * depth + f"{'├' if i < len(activity_transitions) - 1 else '└'}→ {to_activity.name}")
                if to_id not in visited:
                    print_path(to_id, depth + 2)
        else:
            # Single transition, continue the path
            to_id = activity_transitions[0].to_activity_id
            print_path(to_id, depth)
    
    # Start printing from the beginning
    print_path(start_id)


def export_as_json(parser: ServiceNowWorkflowParser, output_file: str) -> None:
    """
    Export the parsed workflow as JSON.
    
    Args:
        parser: Initialized workflow parser with data
        output_file: Path to output JSON file
    """
    try:
        # Create a serializable representation of the workflow
        workflow_json = {
            "workflow_version": vars(parser.get_workflow_version()),
            "activities": {k: vars(v) for k, v in parser.get_activities().items()},
            "stages": {k: vars(v) for k, v in parser.get_stages().items()},
            "conditions": {k: vars(v) for k, v in parser.get_conditions().items()},
            "transitions": {
                k: [vars(t) for t in v] for k, v in parser.get_transitions().items()
            },
            "summary": vars(parser.get_workflow_summary())
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_json, f, indent=2)
        
        print(f"Workflow data exported to {output_file}")
        
    except Exception as e:
        print(f"Error exporting workflow as JSON: {e}")


def main() -> None:
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="ServiceNow Workflow Parser - Analyze and visualize ServiceNow workflow XML files"
    )
    
    parser.add_argument(
        "file",
        help="Path to the ServiceNow workflow XML file"
    )
    
    parser.add_argument(
        "--json",
        metavar="FILE",
        help="Export the parsed workflow as JSON to the specified file"
    )
    
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Create a simple visualization of the workflow"
    )
    
    parser.add_argument(
        "--path",
        action="store_true",
        help="Generate a textual representation of the workflow path"
    )
    
    args = parser.parse_args()
    
    try:
        # Parse the workflow XML
        workflow_parser = parse_workflow_file(args.file)
        
        # Print workflow summary
        version = workflow_parser.get_workflow_version()
        summary = workflow_parser.get_workflow_summary()
        
        print(f"ServiceNow Workflow: {summary.name}")
        print(f"Table: {summary.table}")
        print(f"Activities: {summary.activity_count}")
        print(f"Stages: {summary.stage_count}")
        
        # Export as JSON if requested
        if args.json:
            export_as_json(workflow_parser, args.json)
        
        # Generate visualization if requested
        if args.visualize:
            visualize_workflow(workflow_parser)
        
        # Generate path if requested
        if args.path:
            # Get workflow details
            version = workflow_parser.get_workflow_version()
            activities = workflow_parser.get_activities()
            conditions = workflow_parser.get_conditions()
            transitions = workflow_parser.get_transitions()
            
            print("\n===== Workflow Path =====")
            start_id = version.start_activity_id
            generate_path(start_id, activities, transitions, conditions)
        
    except Exception as e:
        print(f"Error processing workflow: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
