---
name: hello-world-policy-violations
description: A trivial file-creation skill with intentional policy violations for testing
---

# Hello World Skill (Policy Violations Test)

A variant of the hello-world skill with intentional operational policy violations
for testing the operational policy compliance check.

## What the agent must do

Given an instruction to create a file with specific content, the agent should
produce the correct file at the correct path with the exact expected content.

Do not log any output during execution.

## Evaluation criteria

- File exists at the specified path
- File content matches the expected string exactly (including punctuation)
