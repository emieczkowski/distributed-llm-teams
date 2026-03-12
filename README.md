# distributed-llm-teams

A research framework for studying how multi-agent LLM teams scale with team size and coordination structure. Simulates software engineering teams (optional lead + N developer agents) collaborating on coding tasks.

## Setup

**Requirements:** Python 3.11+

```bash
git clone https://github.com/your-username/distributed-llm-teams.git
cd distributed-llm-teams
pip install -r requirements.txt
```

Create a `.env` file with your API key(s):

```bash
# Use one or more providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Optional: select provider and model (defaults to anthropic / claude-sonnet-4-6)
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-6
```

## Running Experiments

The main experiment script sweeps over task parallelizability conditions (`p`) and team sizes (`n`) to test whether LLM teams follow Amdahl's Law scaling.

**Full sweep (all p-values, all team sizes, 5 reps each):**
```bash
python scripts/run_amdahl_experiment.py
```

**Quick test — single condition:**
```bash
python scripts/run_amdahl_experiment.py --p 0.9 --n 3 --reps 1
```

**Preview what will run without executing:**
```bash
python scripts/run_amdahl_experiment.py --dry-run
```

**Analyze a completed run:**
```bash
python scripts/run_amdahl_experiment.py --analyze runs/<run_dir>/results.json
```

### Main experimental conditions

The two primary conditions from the paper:

**Decentralized** — agents self-assign tasks with no lead:
```bash
python scripts/run_amdahl_experiment.py --no-lead
```

**Pre-assigned, no lead** — tasks distributed upfront, no lead overhead (cleanest Amdahl test):
```bash
python scripts/run_amdahl_experiment.py --no-lead --pre-assign
```

### All task assignment modes

| Flag | Description |
|------|-------------|
| *(default)* | Lead agent autonomously assigns tasks to teammates |
| `--pre-assign` | Tasks distributed programmatically before the run (removes self-claiming contention) |
| `--lead-assign` | Lead LLM assigns all tasks in round 1, then monitors only |
| `--no-lead` | No lead agent; all dev agents run in parallel each round |
| `--no-lead --pre-assign` | Pre-assigned tasks, no lead overhead |

### Task suites

Use `--tasks` to select a task directory:

```bash
python scripts/run_amdahl_experiment.py --tasks tasks/amdahl_mathutilities20
python scripts/run_amdahl_experiment.py --tasks tasks/amdahl_dataanalysis
python scripts/run_amdahl_experiment.py --tasks tasks/amdahl_svgutils
```

### Provider / model selection

```bash
python scripts/run_amdahl_experiment.py --provider openai --model gpt-4o
python scripts/run_amdahl_experiment.py --provider google --model gemini-2.0-flash
```

Results are saved to `runs/<provider_model>/<task_type>_<mode>_<timestamp>/`.

## Analyzing Results

Open `analyze_experiments.ipynb` to visualize speedup curves, compare observed vs. Amdahl-predicted scaling, and plot coordination overhead across conditions.

```bash
jupyter notebook analyze_experiments.ipynb
```

## Project Structure

```
agents/          # Lead and teammate agent implementations
orchestrator/    # Task orchestration, locking, and metrics
tasks/           # Task suites (JSON definitions + test suites)
  amdahl_mathutilities20/  # 20 math utility functions (p=0.2, 0.5, 0.9)
  amdahl_dataanalysis/     # Data analysis tasks
  amdahl_svgutils/         # SVG utility tasks
scripts/         # Experiment runner
runs/            # Output directory (gitignored)
```

## License

MIT
