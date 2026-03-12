import re
from dataclasses import dataclass
from typing import List, Optional

# Basic Actions (all agents)
@dataclass
class EditFileAction:
    path: str
    content: str

@dataclass
class ClaimTaskAction:
    task_id: str

@dataclass
class CompleteTaskAction:
    task_id: str

@dataclass
class RunTestsAction:
    pass

# Lead Agent Actions
@dataclass
class AssignTaskAction:
    task_id: str
    assignee: str

@dataclass
class BroadcastAction:
    message: str

@dataclass
class RequestStatusAction:
    pass

@dataclass
class SynthesizeAction:
    summary: str

# Regular expressions for parsing
EDIT_FILE_RE = re.compile(r'<edit_file\s+path="([^"]+)">\s*(.*?)\s*</edit_file>', re.DOTALL)
CLAIM_TASK_RE = re.compile(r'<claim_task\s+id="([^"]+)"\s*/>')
COMPLETE_TASK_RE = re.compile(r'<complete_task\s+id="([^"]+)"\s*/>')
RUN_TESTS_RE = re.compile(r'<run_tests\s*/>')

# Lead agent patterns
ASSIGN_TASK_RE = re.compile(r'<assign_task\s+id="([^"]+)"\s+to="([^"]+)"\s*/>')
BROADCAST_RE = re.compile(r'<broadcast>\s*(.*?)\s*</broadcast>', re.DOTALL)
REQUEST_STATUS_RE = re.compile(r'<request_status\s*/>')
SYNTHESIZE_RE = re.compile(r'<synthesize>\s*(.*?)\s*</synthesize>', re.DOTALL)

def parse_actions(text):
    """Parse all action tags from agent response."""
    actions = []

    # Basic actions
    for m in EDIT_FILE_RE.finditer(text):
        actions.append(EditFileAction(path=m.group(1), content=m.group(2)))

    for m in CLAIM_TASK_RE.finditer(text):
        actions.append(ClaimTaskAction(task_id=m.group(1)))

    for m in COMPLETE_TASK_RE.finditer(text):
        actions.append(CompleteTaskAction(task_id=m.group(1)))

    if RUN_TESTS_RE.search(text):
        actions.append(RunTestsAction())

    # Lead agent actions
    for m in ASSIGN_TASK_RE.finditer(text):
        actions.append(AssignTaskAction(task_id=m.group(1), assignee=m.group(2)))

    for m in BROADCAST_RE.finditer(text):
        actions.append(BroadcastAction(message=m.group(1)))

    if REQUEST_STATUS_RE.search(text):
        actions.append(RequestStatusAction())

    for m in SYNTHESIZE_RE.finditer(text):
        actions.append(SynthesizeAction(summary=m.group(1)))

    return actions
