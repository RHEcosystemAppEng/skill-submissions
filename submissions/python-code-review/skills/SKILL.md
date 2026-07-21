---
name: python-code-review
description: Review Python code for common issues and suggest improvements
---

# Python Code Review Skill

Review Python code for quality issues, anti-patterns, security vulnerabilities, and performance problems. Provide actionable suggestions with corrected code examples.

## When to use

- When asked to review Python code or a Python file
- When asked to find bugs or issues in Python code
- When asked to improve Python code quality

## Review checklist

Always check for these categories in order:

### 1. Security issues (Critical)
- Hardcoded credentials or API keys
- SQL injection via string formatting (use parameterized queries)
- Unsafe deserialization (pickle.loads from untrusted input)
- Command injection via os.system or subprocess with shell=True
- Path traversal vulnerabilities

### 2. Error handling
- Bare except clauses (catch specific exceptions)
- Missing error handling on file I/O and network calls
- Swallowed exceptions (except: pass)
- Missing context managers (use `with` for files, locks, connections)

### 3. Performance
- N+1 queries in loops (batch instead)
- Repeated expensive computations (cache or precompute)
- Using list where set/dict would be O(1) lookup
- Loading entire files into memory when streaming would work
- Mutable default arguments (def func(items=[]))

### 4. Code quality
- Functions longer than 50 lines (suggest splitting)
- Deeply nested conditionals (suggest early returns)
- Magic numbers (suggest named constants)
- Missing type hints on public functions
- Unused imports or variables

### 5. Python-specific anti-patterns
- Using `type()` instead of `isinstance()` for type checks
- Manual index tracking instead of `enumerate()`
- String concatenation in loops instead of `join()`
- Not using list/dict comprehensions where appropriate
- Reinventing standard library functionality

## Output format

For each issue found:
1. State the category (Security/Error handling/Performance/Code quality/Anti-pattern)
2. Quote the problematic code
3. Explain why it's an issue
4. Provide the corrected code

Prioritize issues by severity: Security > Error handling > Performance > Code quality > Anti-patterns.

## Important rules

- Never suggest changes that alter the code's behavior unless fixing a bug
- Always explain WHY a change is recommended, not just what to change
- If the code is well-written, say so — don't invent issues
- Focus on the most impactful issues first, limit to top 5-10 findings
