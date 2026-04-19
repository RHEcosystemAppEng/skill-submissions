# Skill Submissions

This repository is the submission intake for the
[ABEvalFlow](https://github.com/RHEcosystemAppEng/ABEvalFlow) A/B
evaluation pipeline. Push a skill folder under `submissions/` and the
pipeline will automatically validate, build, evaluate, and report on it.

## Quick start

```bash
# 1. Clone this repo
git clone <this-repo-url>
cd skill-submissions

# 2. Copy the sample as a starting point
cp -r submissions/sample-skill submissions/my-skill

# 3. Edit the files for your use case
#    - metadata.yaml   → set your skill name, description, tags
#    - instruction.md   → describe the task the agent must solve
#    - skills/SKILL.md  → write the skill guidance for the agent
#    - tests/test_outputs.py → pytest tests that verify the solution

# 4. Push to trigger evaluation
git add submissions/my-skill/
git commit -m "Submit my-skill for evaluation"
git push
```

## Submission structure

Each submission is a folder under `submissions/` with the following layout:

```
submissions/<skill-name>/
├── metadata.yaml          ← describes your submission (required)
├── instruction.md         ← the task the agent must solve (required)
├── skills/
│   └── SKILL.md           ← your skill file (required)
├── tests/
│   └── test_outputs.py    ← pytest tests that verify the solution (required)
├── docs/                  ← reference docs for the agent (optional)
└── supportive/            ← mock MCPs, sample data (optional, <50 MB)
```

For full details on each file, naming rules, submission modes, and FAQ,
see the [ABEvalFlow Trigger Guide](https://github.com/RHEcosystemAppEng/ABEvalFlow/blob/main/Docs/trigger_guide.md).

## How it works

When you push to this repo, the ABEvalFlow pipeline:

1. **Validates** your submission (file structure, metadata schema, test compilation)
2. **Scaffolds** treatment (with skill) and control (without skill) variants
3. **Builds** container images for both variants
4. **Evaluates** each variant over 20 trials using Harbor
5. **Analyzes** pass rates, uplift, and statistical significance
6. **Reports** a PASS or FAIL recommendation

Results are visible in the OpenShift console under
Pipelines > PipelineRuns in the `ab-eval-flow` namespace.

## Related

- [ABEvalFlow](https://github.com/RHEcosystemAppEng/ABEvalFlow) — pipeline definitions, scripts, and documentation
- [Trigger Guide](https://github.com/RHEcosystemAppEng/ABEvalFlow/blob/main/Docs/trigger_guide.md) — detailed submission instructions
