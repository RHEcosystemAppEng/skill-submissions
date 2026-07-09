---
name: hello-world-policy-pass
description: A trivial file-creation skill that passes all operational policy checks
---

# Hello World Skill (Policy Pass Test)

A variant of the hello-world skill that complies with all operational policy
requirements for testing the operational policy compliance check.

## What the agent must do

Given an instruction to create a file with specific content, the agent should
produce the correct file at the correct path with the exact expected content.

## Evaluation criteria

- File exists at the specified path
- File content matches the expected string exactly (including punctuation)
