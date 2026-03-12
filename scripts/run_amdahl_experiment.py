"""
Amdahl's Law scaling experiment for LLM teams.

Three tasks, four team sizes, multiple repetitions per condition.

  p values: parallelizability fraction for Amdahl's Law
  team sizes: number of teammates plus 1 lead coordinator in every run)
  repetitions: N_REPS runs of the same task file 

  python scripts/run_amdahl_experiment.py
  python scripts/run_amdahl_experiment.py --p 0.5 --n 3 --reps 5
  python scripts/run_amdahl_experiment.py --dry-run
  python scripts/run_amdahl_experiment.py --analyze runs/amdahl_20260219_120000/results.json
  python scripts/run_amdahl_experiment.py --lead-assign   # lead LLM assigns all tasks in round 1
"""
import asyncio
import os
import sys
import json
import shutil
import time
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv(override=True)
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.lead_agent import LeadAgent
from agents.teammate_agent import TeammateAgent
from orchestrator.orchestrator import Orchestrator
from orchestrator.metrics import analyze_run, ParallelizationMetrics

P_CONDITIONS = {
    "p09": (0.9, 1),
    "p05": (0.5, 5),
    "p02": (0.2, 8),
}

N_VALUES = [1, 2, 3, 4, 5]
N_REPS   = 5
MAX_ROUNDS = 60

_PROVIDER_DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-5.2",
    "google": "gemini-3-flash-preview",
}


def _load_prompts():
    prompts_dir = Path("agents/prompts")
    lead_prompt = (prompts_dir / "lead_prompt.txt").read_text() if (prompts_dir / "lead_prompt.txt").exists() \
        else "You are a senior software engineer leading a development team."
    teammate_prompt = (prompts_dir / "teammate_prompt.txt").read_text() if (prompts_dir / "teammate_prompt.txt").exists() \
        else "You are a skilled software engineer working on a team."
    return lead_prompt, teammate_prompt


def create_team(num_teammates, model_config=None, include_lead=True):
    lead_prompt, teammate_prompt = _load_prompts()
    teammate_names = [f"Dev{i+1}" for i in range(num_teammates)]
    agents = {}
    if include_lead:
        agents["Lead"] = LeadAgent(name="Lead", system_prompt=lead_prompt,
                                   team_members=teammate_names, model=model_config)
    for name in teammate_names:
        agents[name] = TeammateAgent(name=name, system_prompt=teammate_prompt, model=model_config)
    return agents


def _pre_assign_tasks(task_path, teammate_names):
    """
    Assign all tasks to agents before the run, respecting dependency chains.

    Strategy: topological sort, then assign tasks round-robin.  If a task
    depends on another task, it goes to the same agent as that dependency so
    serial chains stay on one agent and don't cross agent boundaries.

    Returns a dict mapping task_id -> agent_name.
    """
    tasks_data = json.loads(task_path.read_text())
    tasks = tasks_data["tasks"]
    task_map = {t["id"]: t for t in tasks}

    # Topological sort (dependencies before dependents)
    order, visited = [], set()
    def visit(tid):
        if tid in visited:
            return
        visited.add(tid)
        for dep in task_map[tid].get("dependencies", []):
            visit(dep)
        order.append(tid)
    for t in tasks:
        visit(t["id"])

    # Assign: keep dependency chains on one agent, distribute free tasks round-robin
    assignment = {}
    rr = 0
    for tid in order:
        deps = task_map[tid].get("dependencies", [])
        if deps and deps[-1] in assignment:
            # Continue the chain on the same agent
            assignment[tid] = assignment[deps[-1]]
        else:
            assignment[tid] = teammate_names[rr % len(teammate_names)]
            rr += 1

    # Write assignments into the task file
    for t in tasks:
        t["owner"] = assignment[t["id"]]
        t["status"] = "assigned"
        t["assigned_by"] = "System"
    task_path.write_text(json.dumps(tasks_data, indent=2))
    return assignment


def run_single(task_file, n_teammates, max_rounds, run_dir, pre_assign=False, lead_assign=False, no_lead=False, verbose=True, model_config=None):
    """
    Copy of task file is made inside run_dir so the orchestrator's
    saves don't mutate the original task file between reps.

    pre_assign=True: tasks are distributed to agents programmatically before
    the run starts.  Each agent is notified of its assignments; the lead acts
    as a monitor only.  This removes self-claiming contention and gives a
    cleaner test of Amdahl's Law.

    lead_assign=True: the lead LLM is instructed to assign all tasks to
    teammates in round 1 (no self-claiming).  Tests whether the lead can
    discover an efficient assignment strategy on its own.

    no_lead=True (requires pre_assign=True): omits the Lead agent entirely.
    All Dev agents run in parallel every round with no sequential Lead turn.
    Eliminates the fixed per-round Lead overhead to give a cleaner Amdahl measurement.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / ".locks").mkdir(exist_ok=True)
    repo_dir = run_dir / "repo"
    repo_dir.mkdir(parents=True, exist_ok=True)

    # Copy task file
    task_copy = run_dir / "tasks.json"
    shutil.copy(task_file, task_copy)

    # Copy pre-written test suite and conftest into repo_dir so agents get
    # real test feedback when they run <run_tests />.
    test_src = task_file.parent / f"test_{task_file.stem}.py"
    conftest_src = task_file.parent / "conftest.py"
    if test_src.exists():
        shutil.copy(test_src, repo_dir / "test_suite.py")
    if conftest_src.exists():
        shutil.copy(conftest_src, repo_dir / "conftest.py")

    if no_lead and pre_assign:
        mode_tag = " [pre-assigned, no-lead]"
    elif no_lead:
        mode_tag = " [decentralized]"
    elif pre_assign:
        mode_tag = " [pre-assigned]"
    elif lead_assign:
        mode_tag = " [lead-assign]"
    else:
        mode_tag = ""
    if verbose:
        print(f"  -> {run_dir.name}  (n={n_teammates}, task={task_file.stem}){mode_tag}")

    teammate_names = [f"Dev{i+1}" for i in range(n_teammates)]
    agents = create_team(n_teammates, model_config=model_config, include_lead=not no_lead)

    if lead_assign:
        # Tell the lead its job: use assign_task to assign every task in round 1, then monitor
        agents["Lead"].receive(
            "[System] You are the team lead. Your ONLY job is to assign tasks to teammates — "
            "you are NOT permitted to write code, edit files, or claim tasks yourself.\n\n"
            f"Your team: {', '.join(teammate_names)}\n\n"
            "=== HOW TO ASSIGN ===\n"
            "Use one XML tag per task: <assign_task task_id=\"TASK_ID\" assignee=\"DevN\"/>\n"
            "Each tag sends a direct notification to that teammate and registers their ownership.\n\n"
            "=== ASSIGNMENT RULES ===\n"
            "1. Keep dependency chains on ONE agent: if task B depends on task A, assign both "
            "to the same person so the serial chain stays on one agent.\n"
            "2. Distribute independent tasks as evenly as possible across teammates.\n"
            "3. Assign ALL tasks in round 1.\n\n"
            "=== WHAT HAPPENS AFTER YOU ASSIGN ===\n"
            "The task list uses status icons:\n"
            "  ⏳ pending   — not yet assigned\n"
            "  📌 assigned  — assignment SUCCEEDED; owner will claim it next round\n"
            "  🔨 in_progress — owner is coding\n"
            "  ✅ done      — complete\n\n"
            "When you see 📌 assigned, do NOT re-assign. Teammates saying 'I'll wait' in "
            "round 1 is NORMAL — they will act in round 2.\n\n"
            "=== LATER ROUNDS ===\n"
            "From round 2 onwards, respond 'Monitoring...' and do nothing. "
            "Only speak up if a teammate explicitly reports being BLOCKED.",
            sender="System",
        )
        # Tell teammates: look for tasks assigned to YOUR name and claim them
        for name in teammate_names:
            agents[name].receive(
                f"[System] Your name is {name}. Do NOT self-claim any tasks.\n"
                "Wait for the Lead to assign tasks to you directly. You will receive a "
                f"direct assignment message from Lead, AND the task list will show "
                f"📌 assigned tasks with Owner: {name}. "
                f"Once you see tasks owned by {name}, immediately claim each one "
                "(using <claim_task>) and implement it. "
                "Do not claim tasks owned by other agents.",
                sender="System",
            )

    if pre_assign:
        assignment = _pre_assign_tasks(task_copy, teammate_names)

        # Invert: agent_name -> [task_ids]
        agent_tasks: dict[str, list[str]] = {}
        for tid, aname in assignment.items():
            agent_tasks.setdefault(aname, []).append(tid)

        # Notify each teammate of exactly which tasks are theirs
        for aname, tids in agent_tasks.items():
            if aname in agents:
                agents[aname].receive(
                    f"[System Pre-Assignment] Your tasks for this run: {', '.join(tids)}.\n"
                    "Claim and complete ONLY your assigned tasks in order. "
                    "Do NOT claim tasks belonging to other agents.",
                    sender="System",
                )

        if not no_lead:
            # Tell the lead it is a monitor, not an assigner
            agents["Lead"].receive(
                "[System] All tasks have been pre-assigned to teammates by the system. "
                "Do NOT assign or claim tasks yourself. "
                "Your role this run: broadcast a start signal in round 1, then monitor "
                "progress and help teammates who are blocked.",
                sender="System",
            )

    orchestrator = Orchestrator(
        run_dir=run_dir,
        repo_dir=repo_dir,
        agents=agents,
        task_list_path=task_copy,
    )

    lead_agent_name = None if no_lead else "Lead"
    t0 = time.time()
    success = asyncio.run(orchestrator.run_async(max_rounds=max_rounds, lead_agent_name=lead_agent_name))
    wall_clock_seconds = time.time() - t0

    # Sum token usage across all agents
    total_input_tokens, total_output_tokens = 0, 0
    for agent in agents.values():
        client = getattr(agent, "llm_client", None)
        if client is not None:
            total_input_tokens += client.total_input_tokens
            total_output_tokens += client.total_output_tokens

    # Collect metrics from the completed run
    metrics = analyze_run(run_dir)
    score = metrics.get_parallelization_score()

    tasks = metrics.tasks.get("tasks", [])
    tasks_done = sum(1 for t in tasks if t.get("status") == "done")

    return {
        "success": success,
        "tasks_done": tasks_done,
        "total_tasks": score["num_tasks"],
        "wall_clock_seconds": wall_clock_seconds,
        "total_rounds": score["total_rounds"],
        "critical_path": score["critical_path"],
        "p_parallelizable": score["p_parallelizable"],
        "n_teammates": n_teammates,
        "theoretical_min_rounds": score["theoretical_min_rounds"],
        "predicted_amdahl_speedup": score["predicted_amdahl_speedup"],
        "lock_conflicts": score["lock_conflicts"],
        "run_dir": str(run_dir),
        "pre_assign": pre_assign,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
    }


def run_sweep(p_filter, n_filter, n_reps, max_rounds, base_dir, pre_assign=False, lead_assign=False, no_lead=False, verbose=True, model_config=None, tasks_dir=None):
    tasks_dir = Path(tasks_dir) if tasks_dir else Path("tasks/amdahl_mathutilities20")
    results_path = base_dir / "results.json"
    all_results = []

    for label, (p_true, _) in P_CONDITIONS.items():
        if p_filter is not None and abs(p_true - p_filter) > 1e-9:
            continue

        task_file = tasks_dir / f"{label}.json"
        p_dir = base_dir / label
        print(f"\n=== p={p_true} ({label}) ===")

        for n in N_VALUES:
            if n_filter is not None and n != n_filter:
                continue

            print(f"  n={n} teammates:")
            for rep in range(n_reps):
                ts = datetime.now().strftime("%H%M%S_%f")
                run_dir = p_dir / f"n{n}_rep{rep}_{ts}"

                result = run_single(task_file, n, max_rounds, run_dir, pre_assign=pre_assign, lead_assign=lead_assign, no_lead=no_lead, verbose=verbose, model_config=model_config)
                result["p_label"] = label
                result["p_true"] = p_true
                result["rep"] = rep

                status = "OK" if result["success"] else f"TIMEOUT ({result['tasks_done']}/{result['total_tasks']} done)"
                print(f"     rep {rep}: {result['wall_clock_seconds']:.1f}s — {status}")

                all_results.append(result)
                # Flush after every rep so the notebook can plot partial results
                results_path.write_text(json.dumps(all_results, indent=2))

    return all_results


def compute_summary(results):
    groups = defaultdict(list)
    for r in results:
        groups[(r["p_label"], r["n_teammates"])].append(r)

    mean_wall_clock = {}
    for (p_label, n), runs in groups.items():
        completed = [r for r in runs if r["success"]]
        use = completed if completed else runs
        mean_wall_clock[(p_label, n)] = sum(r["wall_clock_seconds"] for r in use) / len(use)

    # Build summary with speedup relative to n=1 baseline
    summary = defaultdict(dict)
    for label, (p_true, critical_path) in P_CONDITIONS.items():
        baseline = mean_wall_clock.get((label, 1))
        for n in N_VALUES:
            mwc = mean_wall_clock.get((label, n))
            if baseline is not None and mwc is not None and mwc > 0:
                observed_speedup = baseline / mwc
            else:
                observed_speedup = float("nan")
            amdahl = ParallelizationMetrics.amdahl_speedup(p_true, n)
            summary[label][n] = {
                "p_true": p_true,
                "critical_path": critical_path,
                "n_teammates": n,
                "mean_wall_clock_seconds": mwc,
                "observed_speedup": observed_speedup,
                "amdahl_speedup": amdahl,
                "speedup_ratio": observed_speedup / amdahl if amdahl > 0 else float("nan"),
            }

    return dict(summary)


def _fmt(val, fmt=".2f", suffix=""):
    if val is None or val != val:  # None or NaN
        return "N/A"
    return f"{val:{fmt}}{suffix}"


def print_amdahl_table(summary):
    W = 82
    print()
    print("=" * W)
    print("AMDAHL SCALING EXPERIMENT — RESULTS")
    print("=" * W)
    print(f"{'Condition':<20} {'n':>3}  {'Mean time (s)':>13}  {'Obs speedup':>12}  {'Amdahl pred':>12}  {'Ratio':>7}")
    print("-" * W)

    for label in ["p09", "p05", "p02"]:
        p_true, critical_path = P_CONDITIONS[label]
        cond_name = f"p={p_true} (C={critical_path})"
        first = True
        for n in N_VALUES:
            if n not in summary.get(label, {}):
                continue
            row = summary[label][n]
            name_col = cond_name if first else ""
            first = False
            wc  = _fmt(row["mean_wall_clock_seconds"], ".1f", "s")
            obs = _fmt(row["observed_speedup"],        ".2f", "x")
            amd = _fmt(row["amdahl_speedup"],          ".2f", "x")
            rat = _fmt(row["speedup_ratio"],           ".2f")
            print(f"  {name_col:<18} {n:>3}  {wc:>13}  {obs:>12}  {amd:>12}  {rat:>7}")
        print()

    print("=" * W)
    print()
    print("Ratio < 1.0 → coordination overhead limits scaling below Amdahl's prediction.")
    print("Ratio > 1.0 → observed speedup exceeds prediction.")
    print()


def analyze_results_file(results_path):
    results = json.loads(results_path.read_text())
    summary = compute_summary(results)
    print_amdahl_table(summary)


def main():
    parser = argparse.ArgumentParser(description="Run Amdahl scaling experiment for LLM teams")
    parser.add_argument("--p", type=float, default=None)
    parser.add_argument("--n", type=int, default=None)
    parser.add_argument("--reps", type=int, default=N_REPS)
    parser.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--analyze", type=str, default=None)
    parser.add_argument("--pre-assign", action="store_true",
                        help="Distribute tasks to agents programmatically before the run "
                             "(removes self-claiming contention for a cleaner Amdahl test).")
    parser.add_argument("--lead-assign", action="store_true",
                        help="Lead LLM assigns all tasks to teammates in round 1 "
                             "(no self-claiming; tests whether the lead discovers an efficient strategy).")
    parser.add_argument("--no-lead", action="store_true",
                        help="Omit the Lead agent entirely. "
                             "All Dev agents run in parallel each round with no sequential Lead turn. "
                             "Combine with --pre-assign to eliminate both Lead overhead and self-claiming contention, "
                             "or use alone for a fully decentralized autonomous sweep.")
    parser.add_argument("--tasks", type=str, default="tasks/amdahl_mathutilities20",
                        help="Path to tasks directory (e.g. tasks/amdahl_dataanalysis). "
                             "The directory name is included in the run folder.")
    parser.add_argument("--provider", type=str, default=None,
                        help="LLM provider to use (anthropic, openai, google). "
                             "Defaults to LLM_PROVIDER env var.")
    parser.add_argument("--model", type=str, default=None,
                        help="Model name to use (e.g. gemini-3-flash, gpt-4o). "
                             "Defaults to provider default.")
    args = parser.parse_args()

    if args.analyze:
        analyze_results_file(Path(args.analyze))
        return 0

    if args.dry_run:
        mode = ("preassign_nolead" if (args.pre_assign and args.no_lead)
                else "decentralized" if args.no_lead
                else "pre-assign" if args.pre_assign
                else "lead-assign" if args.lead_assign
                else "autonomous")
        print(f"Planned conditions (dry run — nothing will execute) [mode: {mode}, tasks: {args.tasks}]:\n")
        total = 0
        for label, (p_true, cp) in P_CONDITIONS.items():
            if args.p is not None and abs(p_true - args.p) > 1e-9:
                continue
            for n in N_VALUES:
                if args.n is not None and n != args.n:
                    continue
                count = args.reps
                total += count
                print(f"  {label}  p={p_true}  C={cp}  n={n}  x{count} reps")
        print(f"\nTotal runs: {total}  (max {args.max_rounds} rounds each)")
        return 0

    model_config = {}
    if args.provider:
        model_config["provider"] = args.provider
    if args.model:
        model_config["model"] = args.model
    model_config = model_config or None

    effective_provider = args.provider or os.getenv("LLM_PROVIDER", "anthropic")
    effective_model = args.model or os.getenv("LLM_MODEL") or _PROVIDER_DEFAULT_MODELS.get(effective_provider, effective_provider)
    mode = ("preassign_nolead" if (args.pre_assign and args.no_lead)
            else "decentralized" if args.no_lead
            else "preassign" if args.pre_assign
            else "leadassign" if args.lead_assign
            else "autonomous")
    task_type = Path(args.tasks).name  # e.g. "amdahl_20" or "amdahl_dataanalysis"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path("runs") / f"{effective_provider}_{effective_model}" / f"{task_type}_{mode}_{ts}"
    base_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nAmdahl experiment — output: {base_dir}\n")

    all_results = run_sweep(
        p_filter=args.p,
        n_filter=args.n,
        n_reps=args.reps,
        max_rounds=args.max_rounds,
        base_dir=base_dir,
        pre_assign=args.pre_assign,
        lead_assign=args.lead_assign,
        no_lead=args.no_lead,
        model_config=model_config,
        tasks_dir=args.tasks,
    )

    results_path = base_dir / "results.json"
    results_path.write_text(json.dumps(all_results, indent=2))
    print(f"\nRaw results saved to: {results_path}")

    summary = compute_summary(all_results)
    print_amdahl_table(summary)

    summary_path = base_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Summary saved to: {summary_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
