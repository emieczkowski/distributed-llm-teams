"""
Lead Agent - Coordinates team, assigns tasks, and synthesizes results.

The lead agent has special responsibilities:
1. Reviewing and understanding the overall task
2. Breaking down work and assigning to teammates
3. Monitoring progress and status
4. Synthesizing results from team
5. Making high-level decisions
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from agents.base_agent import BaseAgent


@dataclass
class LeadAgent(BaseAgent):
    """
    Lead agent coordinates the team and synthesizes results.
    """

    # Track team members
    team_members: List[str] = field(default_factory=list)

    def __init__(self, name, system_prompt, model=None, team_members=None):
        super().__init__(name, system_prompt, model)
        self.team_members = team_members or []

        # Enhance system prompt with lead-specific instructions
        self.system_prompt = self._build_lead_prompt(system_prompt)

    def _build_lead_prompt(self, base_prompt: str) -> str:
        """Augment prompt with lead-specific instructions."""
        lead_instructions = f"""
{base_prompt}

=== LEAD AGENT RESPONSIBILITIES ===

You are the LEAD AGENT coordinating a team of {len(self.team_members)} developers: {', '.join(self.team_members)}

Your responsibilities:
1. **Task Assignment**: Assign tasks to teammates based on their status
2. **Coordination**: Monitor progress and help unblock teammates
3. **Quality Control**: Review work and ensure consistency
4. **Synthesis**: Combine results into coherent final output

=== AVAILABLE ACTIONS ===

**Assign a task to a teammate:**
<assign_task id="task-1" to="AgentName" />

**Broadcast message to all teammates:**
<broadcast>
Your message here
</broadcast>

**Request status from all agents:**
<request_status />

**Claim a task yourself (if needed):**
<claim_task id="task-1" />

**Complete a task:**
<complete_task id="task-1" />

**Edit a file:**
<edit_file path="relative/path.py">
file content here
</edit_file>

**Run tests:**
<run_tests />

**Synthesize final results:**
<synthesize>
Summary of team's work and final status
</synthesize>

=== STRATEGY ===

1. **First round**: Review tasks, create plan, assign work
2. **Middle rounds**: Monitor status, provide guidance, handle blockers
3. **Final rounds**: Review results, synthesize output, ensure completion

Keep coordination messages concise and actionable.
"""
        return lead_instructions

    def _idle_response(self):
        """Lead agent checks on team status when idle."""
        # Lead can proactively check status or provide guidance
        return "<request_status />"
