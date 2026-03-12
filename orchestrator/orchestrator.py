import asyncio
import json, re, time, subprocess
from pathlib import Path
from orchestrator.token_parser import (
    parse_actions, EditFileAction, ClaimTaskAction, CompleteTaskAction,
    RunTestsAction, AssignTaskAction, BroadcastAction, RequestStatusAction,
    SynthesizeAction
)
from orchestrator.locks import LockManager

class Orchestrator:
    def __init__(self, run_dir, repo_dir, agents, task_list_path):
        self.run_dir = run_dir
        self.repo_dir = repo_dir
        self.agents = agents
        self.task_list_path = task_list_path
        self.lock_mgr = LockManager(run_dir / ".locks")
        self.events_path = run_dir / "events.jsonl"
        self._current_round = None  # set during run(); included in every log entry

    def load_tasks(self):
        return json.loads(self.task_list_path.read_text())

    def save_tasks(self, tasks):
        self.task_list_path.write_text(json.dumps(tasks, indent=2))

    def log(self, event):
        event["ts"] = time.time()
        if self._current_round is not None:
            event.setdefault("round", self._current_round)
        with self.events_path.open("a") as f:
            f.write(json.dumps(event) + "\n")

    def apply_edit(self, agent_name, action):
        rel = action.path
        # Weird agent behavior where sometimes they preface with "repo/" even though repo_dir is already root
        if rel.startswith("repo/"):
            rel = rel[len("repo/"):]
        ok = self.lock_mgr.acquire(rel, owner=agent_name)
        self.log({"type": "lock_attempt", "agent": agent_name, "path": rel, "ok": ok})
        if not ok:
            return False, "LOCK_DENIED"

        abs_path = self.repo_dir / rel
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        content = action.content
        # Strip markdown code fences that some LLMs wrap around file content
        content = re.sub(r'^```[^\n]*\n', '', content)
        content = re.sub(r'\n```\s*$', '', content)
        abs_path.write_text(content)

        self.lock_mgr.release(rel)
        self.log({"type": "edit_file", "agent": agent_name, "path": rel, "n_chars": len(action.content)})
        return True, "OK"

    def run_tests(self):
        t0 = time.time()
        proc = subprocess.run(["pytest", "-q"], cwd=self.repo_dir, capture_output=True, text=True)
        dt = time.time() - t0
        self.log({
            "type": "run_tests",
            "returncode": proc.returncode,
            "seconds": dt,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
        })
        self._last_test_stdout = proc.stdout
        return proc.returncode == 0

    def get_task_summary(self, tasks):
        """Create task summary for agent context."""
        summary = ["=== CURRENT TASKS ===\n"]
        for t in tasks["tasks"]:
            status_icon = {"pending": "⏳", "assigned": "📌", "in_progress": "🔨", "done": "✅"}.get(t["status"], "❓")
            owner_info = f" (Owner: {t['owner']})" if t.get("owner") else " (Unassigned)"
            deps = f" [Requires: {', '.join(t['dependencies'])}]" if t.get("dependencies") else ""
            summary.append(f"{status_icon} {t['id']}: {t['title']}{owner_info}{deps}")
        return "\n".join(summary)

    def get_status_report(self):
        """Generate status report of all agents."""
        report = ["=== AGENT STATUS ===\n"]
        for name, agent in self.agents.items():
            status = agent.get_status()
            task_info = f"Working on: {status['current_task']}" if status['current_task'] else "Idle"
            report.append(f"• {name}: {task_info}")
        return "\n".join(report)

    def broadcast_message(self, sender, message):
        """Send message to all agents except sender."""
        for name, agent in self.agents.items():
            if name != sender:
                agent.receive(message, sender=sender)
        self.log({"type": "broadcast", "sender": sender, "message": message[:500]})

    def assign_task(self, assigner, task_id, assignee):
        """Assign a task to a specific agent."""
        tasks = self.load_tasks()
        for t in tasks["tasks"]:
            if t["id"] == task_id and t["status"] == "pending":
                t["owner"] = assignee
                t["assigned_by"] = assigner
                t["status"] = "assigned"

                # Notify the assignee
                if assignee in self.agents:
                    msg = f"You have been assigned task '{task_id}': {t['title']}\n{t['description']}"
                    self.agents[assignee].receive(msg, sender=assigner)

                self.log({"type": "assign_task", "task": task_id, "assigner": assigner, "assignee": assignee})
                break
        self.save_tasks(tasks)

    def _deps_satisfied(self, task, all_tasks):
        """Return True if all dependencies of task are done."""
        task_status = {t["id"]: t["status"] for t in all_tasks}
        return all(task_status.get(dep) == "done" for dep in task.get("dependencies", []))

    def _process_actions(self, agent_name, actions, tasks):
        """Execute parsed actions, updating tasks in place. Returns updated tasks."""
        agent = self.agents[agent_name]

        for a in actions:
            if isinstance(a, ClaimTaskAction):
                for t in tasks["tasks"]:
                    if t["id"] == a.task_id and (
                        (t.get("owner") is None and t["status"] == "pending") or
                        (t.get("owner") == agent_name and t["status"] == "assigned")
                    ):
                        if not self._deps_satisfied(t, tasks["tasks"]):
                            self.log({"type": "claim_blocked", "agent": agent_name, "task": a.task_id,
                                      "reason": "dependencies_not_done"})
                            break
                        t["owner"] = agent_name
                        t["status"] = "in_progress"
                        agent.claim_task(a.task_id)
                        self.log({"type": "claim_task", "agent": agent_name, "task": a.task_id})

            elif isinstance(a, CompleteTaskAction):
                for t in tasks["tasks"]:
                    if t["id"] == a.task_id and t.get("owner") == agent_name:
                        t["status"] = "done"
                        agent.complete_task()
                        self.log({"type": "complete_task", "agent": agent_name, "task": a.task_id})

            elif isinstance(a, EditFileAction):
                self.apply_edit(agent_name, a)

            elif isinstance(a, RunTestsAction):
                test_passed = self.run_tests()
                result_msg = "✅ Tests passed!" if test_passed else f"❌ Tests failed:\n{self._last_test_stdout[-1500:]}"
                agent.receive(result_msg, sender="System")

            elif isinstance(a, AssignTaskAction):
                self.assign_task(agent_name, a.task_id, a.assignee)

            elif isinstance(a, BroadcastAction):
                self.broadcast_message(agent_name, a.message)

            elif isinstance(a, RequestStatusAction):
                status_report = self.get_status_report()
                agent.receive(status_report, sender="System")

            elif isinstance(a, SynthesizeAction):
                self.log({"type": "synthesize", "agent": agent_name, "summary": a.summary})

        return tasks

    def step_agent(self, agent_name, round_number):
        agent = self.agents[agent_name]

        tasks = self.load_tasks()
        task_summary = self.get_task_summary(tasks)
        agent.receive(task_summary, sender="System")

        reply = agent.reply()
        self.log({"type": "agent_reply", "agent": agent_name, "round": round_number, "text": reply[:2000]})

        actions = parse_actions(reply)
        tasks = self._process_actions(agent_name, actions, tasks)
        self.save_tasks(tasks)

    async def step_agent_async(self, agent_name, round_number):
        agent = self.agents[agent_name]

        tasks = self.load_tasks()
        task_summary = self.get_task_summary(tasks)
        agent.receive(task_summary, sender="System")

        reply = await agent.reply_async()
        self.log({"type": "agent_reply", "agent": agent_name, "round": round_number, "text": reply[:2000]})

        actions = parse_actions(reply)
        tasks = self.load_tasks()  # reload — another agent may have updated tasks during our LLM call
        tasks = self._process_actions(agent_name, actions, tasks)
        self.save_tasks(tasks)

    def initialize_agents(self, lead_agent_name=None):
        """Send initial context to all agents."""
        tasks = self.load_tasks()
        project_intro = f"""
=== PROJECT: {tasks['project']} ===
{tasks['description']}

Success Criteria: {tasks['success_criteria']}

Repository: {tasks['repository']}
"""
        for agent in self.agents.values():
            agent.receive(project_intro, sender="System")
        teammate_names = [n for n in self.agents if n != lead_agent_name]
        self.log({
            "type": "initialize",
            "project": tasks["project"],
            "agents": list(self.agents.keys()),
            "num_teammates": len(teammate_names),
        })

    def run(self, max_rounds=20, lead_agent_name=None):
        """Sequential run (kept for compatibility and debugging)."""
        self.log({"type": "run_start"})
        self.initialize_agents(lead_agent_name=lead_agent_name)

        for r in range(1, max_rounds + 1):
            self._current_round = r
            self.log({"type": "round_start", "round": r})

            if lead_agent_name and lead_agent_name in self.agents:
                self.step_agent(lead_agent_name, round_number=r)

            for name in self.agents.keys():
                if name != lead_agent_name:
                    self.step_agent(name, round_number=r)

            tasks = self.load_tasks()
            if all(t["status"] == "done" for t in tasks["tasks"]):
                self.log({"type": "run_end", "reason": "all_tasks_done", "round": r})
                self._save_final_state()
                return True

        self.log({"type": "run_end", "reason": "max_rounds"})
        self._save_final_state()
        return False

    async def _close_async_clients(self):
        """Close all agents' async HTTP clients before the event loop shuts down."""
        for agent in self.agents.values():
            client = getattr(agent, "llm_client", None)
            async_client = getattr(client, "async_client", None)
            if async_client is not None:
                close = getattr(async_client, "close", None)
                if close is not None:
                    result = close()
                    if asyncio.iscoroutine(result):
                        await result

    async def run_async(self, max_rounds=20, lead_agent_name=None):
        """
        Async run: lead executes first each round, then all teammates run in parallel.
        Wall-clock time reflects true parallel speedup on the LLM API calls.
        """
        try:
            self.log({"type": "run_start"})
            self.initialize_agents(lead_agent_name=lead_agent_name)

            teammate_names = [n for n in self.agents if n != lead_agent_name]

            for r in range(1, max_rounds + 1):
                self._current_round = r
                self.log({"type": "round_start", "round": r})

                # Lead goes first (sequential) so assignments are visible to teammates
                if lead_agent_name and lead_agent_name in self.agents:
                    await self.step_agent_async(lead_agent_name, round_number=r)

                # All teammates call the LLM in parallel
                await asyncio.gather(*[
                    self.step_agent_async(name, round_number=r)
                    for name in teammate_names
                ])

                tasks = self.load_tasks()
                if all(t["status"] == "done" for t in tasks["tasks"]):
                    self.log({"type": "run_end", "reason": "all_tasks_done", "round": r})
                    self._save_final_state()
                    return True

            self.log({"type": "run_end", "reason": "max_rounds"})
            self._save_final_state()
            return False
        finally:
            await self._close_async_clients()

    def _save_final_state(self):
        """Save final task state to run directory for reference."""
        tasks = self.load_tasks()
        final_tasks_path = self.run_dir / "final_tasks.json"
        final_tasks_path.write_text(json.dumps(tasks, indent=2))
