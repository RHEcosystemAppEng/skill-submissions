#!/usr/bin/env python3
"""Create skill submission directories for rh-sre and rh-virt tasks.

Reads tasks from skillsbench, updates skills from agentic-collections,
generates metadata.yaml and .mcp.json, fixes all paths, and commits
on per-task branches. Does NOT push.
"""

import json
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

SKILLSBENCH = Path("/Users/gziv/Dev/skillsbench/tasks/per_skill_eval")
AGENTIC = Path("/Users/gziv/Dev/agentic-collections")
SUBMISSIONS_REPO = Path("/Users/gziv/Dev/skill-submissions")
SUBMISSIONS_DIR = SUBMISSIONS_REPO / "submissions"

TASKS: dict[str, list[str]] = {
    "rh-sre": [
        "cve-impact", "cve-validation", "execution-summary", "fleet-inventory",
        "job-template-creator", "job-template-remediation-validator",
        "mcp-aap-validator", "mcp-lightspeed-validator", "playbook-executor",
        "playbook-generator", "remediation", "remediation-verifier",
        "system-context",
    ],
    "rh-virt": [
        "vm-clone", "vm-create", "vm-delete", "vm-inventory",
        "vm-lifecycle-manager", "vm-rebalance", "vm-snapshot-create",
        "vm-snapshot-delete", "vm-snapshot-list", "vm-snapshot-restore",
    ],
}

RH_SRE_AAP_TASKS = {
    "job-template-creator", "job-template-remediation-validator",
    "mcp-aap-validator", "playbook-executor",
}

SECONDARY_SKILLS: dict[str, list[str]] = {
    "rh-sre__cve-impact": ["mcp-lightspeed-validator"],
    "rh-sre__cve-validation": ["mcp-lightspeed-validator"],
    "rh-sre__fleet-inventory": ["mcp-lightspeed-validator"],
    "rh-sre__job-template-creator": ["mcp-aap-validator", "playbook-executor"],
    "rh-sre__job-template-remediation-validator": [
        "job-template-creator", "mcp-aap-validator", "playbook-executor",
    ],
    "rh-sre__playbook-executor": ["mcp-aap-validator"],
    "rh-sre__remediation": ["cve-validation"],
}


def git(args: list[str], cwd: Path = SUBMISSIONS_REPO) -> str:
    result = subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def read_task_description(task_dir: Path) -> str:
    toml_path = task_dir / "task.toml"
    if toml_path.exists():
        data = tomllib.loads(toml_path.read_text())
        name = data.get("metadata", {}).get("name", "")
        if name:
            return name
    instruction = task_dir / "instruction.md"
    if instruction.exists():
        first_line = instruction.read_text().strip().split("\n")[0]
        return first_line.lstrip("#").strip()[:120]
    return ""


def generate_mcp_json(persona: str, skill: str) -> dict:
    if persona == "rh-virt":
        return {
            "mcpServers": {
                "openshift-virtualization": {
                    "command": "python3",
                    "args": ["/workspace/supportive/mcp-servers/mock-virt-mcp.py"],
                }
            }
        }
    servers: dict = {
        "lightspeed-mcp": {
            "command": "python3",
            "args": ["/workspace/supportive/mcp-servers/mock-lightspeed-mcp.py"],
        }
    }
    if skill in RH_SRE_AAP_TASKS:
        servers["aap-mcp-job-management"] = {
            "command": "python3",
            "args": ["/workspace/supportive/mcp-servers/mock-aap-mcp.py"],
        }
    return {"mcpServers": servers}


def generate_metadata(persona: str, skill: str, description: str) -> str:
    name = f"{persona}-{skill}"
    tags_str = "\n".join(f"  - {t}" for t in [persona, skill])
    return (
        f"name: {name}\n"
        f'description: "{description}"\n'
        f"persona: {persona}\n"
        f'version: "1.0.0"\n'
        f"generation_mode: manual\n"
        f"tags:\n{tags_str}\n"
        f"cpus: 2\n"
        f"memory_mb: 2048\n"
        f"storage_mb: 10240\n"
        f"experiment:\n"
        f"  n_trials: 1\n"
    )


def rewrite_paths(text: str, persona: str, primary_skill: str) -> str:
    """Rewrite relative and /root paths to absolute container paths."""
    # ../../docs/... -> /workspace/supportive/docs/...
    text = re.sub(
        r'\.\./\.\./docs/',
        '/workspace/supportive/docs/',
        text,
    )
    # ../docs/... (one level up)
    text = re.sub(
        r'\.\./docs/',
        '/workspace/supportive/docs/',
        text,
    )
    # ../<skill>/SKILL.md or ../<skill>/... (cross-skill references)
    # Match ../some-skill-name/ but not ../docs/ (already handled)
    text = re.sub(
        r'\.\./([a-z][a-z0-9-]+)/(SKILL\.md)',
        r'/skills/\1/\2',
        text,
    )
    text = re.sub(
        r'\.\./([a-z][a-z0-9-]+)/(references/)',
        r'/skills/\1/\2',
        text,
    )
    # /root/report.md -> /solution/report.md
    text = text.replace('/root/report.md', '/solution/report.md')
    # /root/.mcp-servers/ -> /workspace/supportive/mcp-servers/
    text = text.replace('/root/.mcp-servers/', '/workspace/supportive/mcp-servers/')
    # python3 <persona>/skills/<skill>/references/... -> python3 /skills/<skill>/references/...
    text = re.sub(
        rf'python3\s+{re.escape(persona)}/skills/([a-z][a-z0-9-]+)/references/',
        r'python3 /skills/\1/references/',
        text,
    )
    # Bare rh-sre/skills/... or rh-virt/skills/... path references
    text = re.sub(
        rf'(?<![/a-zA-Z]){re.escape(persona)}/skills/([a-z][a-z0-9-]+)/',
        r'/skills/\1/',
        text,
    )

    return text


def copytree_no_pycache(src: Path, dst: Path) -> None:
    shutil.copytree(
        src, dst, dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )


def create_submission(persona: str, skill: str) -> None:
    task_key = f"{persona}__{skill}"
    sub_name = f"{persona}-{skill}"
    branch_name = f"eval/{sub_name}"

    bench_dir = SKILLSBENCH / task_key
    agentic_persona_dir = AGENTIC / persona
    sub_dir = SUBMISSIONS_DIR / sub_name

    if not bench_dir.is_dir():
        print(f"  SKIP: {bench_dir} not found")
        return

    # Switch to main and create branch
    git(["checkout", "main"])
    try:
        git(["branch", "-D", branch_name])
    except subprocess.CalledProcessError:
        pass
    git(["checkout", "-b", branch_name])

    # Clean any previous submission
    if sub_dir.exists():
        shutil.rmtree(sub_dir)
    sub_dir.mkdir(parents=True)

    # --- Copy instruction.md from skillsbench ---
    src_instruction = bench_dir / "instruction.md"
    if src_instruction.exists():
        shutil.copy2(src_instruction, sub_dir / "instruction.md")

    # --- Copy tests from skillsbench ---
    bench_tests = bench_dir / "tests"
    if bench_tests.is_dir():
        tests_dir = sub_dir / "tests"
        tests_dir.mkdir()
        for f in ["test_outputs.py", "llm_judge.py"]:
            src = bench_tests / f
            if src.exists():
                shutil.copy2(src, tests_dir / f)

    # --- Build skills directory ---
    skills_dir = sub_dir / "skills"
    skills_dir.mkdir()

    # Primary skill from agentic-collections
    ac_primary = agentic_persona_dir / "skills" / skill
    if ac_primary.is_dir():
        # Copy SKILL.md to skills/SKILL.md
        skill_md = ac_primary / "SKILL.md"
        if skill_md.exists():
            shutil.copy2(skill_md, skills_dir / "SKILL.md")
        # Copy references/, flows/, and extra .md files
        for item in ac_primary.iterdir():
            if item.name == "SKILL.md":
                continue
            if item.is_dir():
                copytree_no_pycache(item, skills_dir / item.name)
            elif item.is_file() and item.suffix == ".md":
                shutil.copy2(item, skills_dir / item.name)
    else:
        # Fallback to skillsbench
        bench_primary = bench_dir / "environment" / "skills" / skill
        if bench_primary.is_dir():
            skill_md = bench_primary / "SKILL.md"
            if skill_md.exists():
                shutil.copy2(skill_md, skills_dir / "SKILL.md")
            for item in bench_primary.iterdir():
                if item.name == "SKILL.md":
                    continue
                if item.is_dir():
                    copytree_no_pycache(item, skills_dir / item.name)
                elif item.is_file() and item.suffix in (".md", ".py"):
                    shutil.copy2(item, skills_dir / item.name)

    # Secondary skills
    secondaries = SECONDARY_SKILLS.get(task_key, [])
    for sec_skill in secondaries:
        sec_dir = skills_dir / sec_skill
        sec_dir.mkdir(exist_ok=True)
        ac_sec = agentic_persona_dir / "skills" / sec_skill
        if ac_sec.is_dir():
            copytree_no_pycache(ac_sec, sec_dir)
        else:
            bench_sec = bench_dir / "environment" / "skills" / sec_skill
            if bench_sec.is_dir():
                copytree_no_pycache(bench_sec, sec_dir)

    # --- Build supportive directory ---
    supportive_dir = sub_dir / "supportive"
    supportive_dir.mkdir()

    # Docs from agentic-collections
    ac_docs = agentic_persona_dir / "docs"
    if ac_docs.is_dir():
        copytree_no_pycache(ac_docs, supportive_dir / "docs")

    # MCP mock servers from skillsbench
    bench_mcp = bench_dir / "environment" / "mcp-servers"
    if bench_mcp.is_dir():
        mcp_dst = supportive_dir / "mcp-servers"
        mcp_dst.mkdir()
        for f in bench_mcp.iterdir():
            if f.is_file() and f.suffix == ".py":
                shutil.copy2(f, mcp_dst / f.name)

    # Generate .mcp.json
    mcp_config = generate_mcp_json(persona, skill)
    (supportive_dir / ".mcp.json").write_text(
        json.dumps(mcp_config, indent=2) + "\n"
    )

    # --- Scripts from agentic-collections (ocp-admin only, but check) ---
    ac_scripts = agentic_persona_dir / "scripts"
    if ac_scripts.is_dir():
        copytree_no_pycache(ac_scripts, sub_dir / "scripts")

    # --- Generate metadata.yaml ---
    description = read_task_description(bench_dir)
    metadata = generate_metadata(persona, skill, description)
    (sub_dir / "metadata.yaml").write_text(metadata)

    # --- Rewrite paths in all text files ---
    for path in sub_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in (".md", ".py", ".json"):
            continue
        if path.name == "metadata.yaml":
            continue
        try:
            content = path.read_text()
            rewritten = rewrite_paths(content, persona, skill)
            if rewritten != content:
                path.write_text(rewritten)
        except UnicodeDecodeError:
            pass

    # --- Commit ---
    git(["add", f"submissions/{sub_name}"])
    git(["commit", "-m", f"eval: add {sub_name} v1.0.0 submission"])

    print(f"  OK: {sub_name} committed on {branch_name}")


def main() -> int:
    personas = sys.argv[1:] if len(sys.argv) > 1 else list(TASKS.keys())
    for persona in personas:
        skills = TASKS.get(persona, [])
        print(f"\n=== {persona} ({len(skills)} tasks) ===")
        for skill in skills:
            print(f"\nCreating {persona}-{skill}...")
            try:
                create_submission(persona, skill)
            except Exception as e:
                print(f"  ERROR: {e}")
    git(["checkout", "main"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
