---
name: detect-project
description: |
  Analyze a project folder to detect programming language, framework, and version requirements.
  Use this skill when containerizing an application, selecting an S2I builder image, deploying
  to OpenShift or RHEL, or determining a project's tech stack. Supports Node.js, Python, Java,
  Go, Ruby, .NET, PHP, Perl, and Rust.
---

# /detect-project Skill

Analyze a local project directory to detect language/framework and recommend a build strategy.

## When to Use This Skill

- User wants to containerize or deploy an application and needs language/framework detection
- User asks what tech stack a project uses or needs a build strategy recommendation
- Run before selecting an S2I builder image or deploying to OpenShift/RHEL

## Workflow

### Step 1: Scan Project Files

Look for these indicator files in the project root:

| File | Language | Framework Hint |
|------|----------|----------------|
| `Chart.yaml` | Helm Chart | Existing Helm deployment available |
| `package.json` | Node.js | Check for next, angular, vue, react |
| `pom.xml` | Java | Check for spring-boot, quarkus deps |
| `build.gradle` / `build.gradle.kts` | Java | Check for spring, quarkus plugins |
| `requirements.txt` | Python | - |
| `Pipfile` | Python | Pipenv |
| `pyproject.toml` | Python | Poetry or modern Python |
| `go.mod` | Go | - |
| `Gemfile` | Ruby | Check for rails |
| `composer.json` | PHP | Check for laravel, symfony |
| `*.csproj` / `*.sln` | .NET | - |
| `Cargo.toml` | Rust | No official S2I |
| `Dockerfile` / `Containerfile` | Pre-containerized | May not need S2I |

### Helm Chart Detection

Check for Helm charts in these locations (in priority order):

| Priority | Path | Description |
|----------|------|-------------|
| 1 | `./Chart.yaml` | Root directory |
| 2 | `./chart/Chart.yaml` | Chart subdirectory |
| 3 | `./charts/*/Chart.yaml` | Charts directory |
| 4 | `./helm/Chart.yaml` | Helm subdirectory |
| 5 | `./deploy/helm/Chart.yaml` | Deploy directory |

If Chart.yaml is found, parse it to extract:
- `name`: Chart name
- `version`: Chart version (SemVer)
- `appVersion`: Application version
- `description`: Chart description

Also check for:
- `values.yaml`: Default configuration
- `templates/`: Template files

### Step 2: Detect Version Requirements

For each detected language, extract version info:

**Node.js:**
- Check `engines.node` in package.json
- Example: `"engines": { "node": ">=18" }`

**Python:**
- Check `python_requires` in pyproject.toml
- Check `runtime.txt` for version
- Check `.python-version` file

**Java:**
- Check `<java.version>` or `<maven.compiler.source>` in pom.xml
- Check `sourceCompatibility` in build.gradle

**Go:**
- Check `go` directive in go.mod
- Example: `go 1.21`

### Step 3: Detect Framework

Look for framework-specific indicators:

**Node.js frameworks:**
- `next.config.js` or `next.config.mjs` → Next.js
- `angular.json` → Angular
- `vue.config.js` or `vite.config.ts` with vue → Vue.js
- `remix.config.js` → Remix

**Java frameworks:**
- `quarkus` in dependencies → Quarkus
- `spring-boot` in dependencies → Spring Boot
- `micronaut` in dependencies → Micronaut

**Python frameworks:**
- `django` in requirements → Django
- `flask` in requirements → Flask
- `fastapi` in requirements → FastAPI

### Step 4: Detect Python Entry Point (Python projects only)

For Python projects, detect the application entry point to ensure proper S2I configuration:

**Check for entry point files (in S2I preference order):**
1. `app.py` - Default S2I Python entry point (no config needed)
2. `application.py` - Alternative default
3. `wsgi.py` - WSGI module
4. `main.py` - Common alternative (requires APP_MODULE config)
5. Any file with `if __name__ == "__main__"` and Flask/FastAPI app

**Check requirements.txt/Pipfile/pyproject.toml for WSGI server:**
- `gunicorn` - Required for APP_MODULE to work with S2I Python
- `uwsgi` - Alternative WSGI server

**Important:** If the entry point is NOT `app.py` and gunicorn IS present, the S2I build
requires setting `APP_MODULE` (e.g., `APP_MODULE=main:app`). Without gunicorn, S2I falls
back to running the file directly.

### Step 5: Present Findings

Format your response as a structured report:

**Detected Language:** [Language]
**Framework:** [Framework or "None detected"]
**Version:** [Version or "Not specified"]

**Detection Confidence:** [High/Medium/Low]
- High: Clear indicator file with version info
- Medium: Indicator file found but no version specified
- Low: Multiple conflicting indicators or unusual setup

**Indicator Files Found:**
- [list of files]

**Recommended S2I Builder Image:**
`registry.access.redhat.com/ubi9/[image-name]`

**Why this image:**
- [Brief explanation]

**Alternative Options:**
1. `[alternative-1]` - [when to choose]
2. `[alternative-2]` - [when to choose]

**Build Strategy:** `Source` (S2I) or `Docker` (Containerfile present)

## Output Variables

After successful detection, these values should be reported:

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_NAME` | Application name | `my-nodejs-app` |
| `LANGUAGE` | Detected language | `nodejs` |
| `FRAMEWORK` | Detected framework | `express` |
| `VERSION` | Language version | `20` |
| `BUILDER_IMAGE` | Full S2I image reference | `registry.access.redhat.com/ubi9/nodejs-20` |
| `BUILD_STRATEGY` | Build strategy | `Source` (S2I) or `Docker` |
| `CONTAINER_PORT` | Application listen port | `8080` |
| `HELM_CHART_PATH` | Path to Helm chart (if found) | `./chart` |
| `PYTHON_ENTRY_POINT` | Python entry point file (if Python) | `app.py` |
| `APP_MODULE` | Python APP_MODULE config (if needed) | `main:app` |

## S2I Builder Image Mapping

| Language | Version | S2I Image |
|----------|---------|-----------|
| Node.js | 18 | `registry.access.redhat.com/ubi9/nodejs-18` |
| Node.js | 20 | `registry.access.redhat.com/ubi9/nodejs-20` |
| Python | 3.9 | `registry.access.redhat.com/ubi9/python-39` |
| Python | 3.11 | `registry.access.redhat.com/ubi9/python-311` |
| Python | 3.12 | `registry.access.redhat.com/ubi9/python-312` |
| Java | 11 | `registry.access.redhat.com/ubi9/openjdk-11` |
| Java | 17 | `registry.access.redhat.com/ubi9/openjdk-17` |
| Java | 21 | `registry.access.redhat.com/ubi9/openjdk-21` |
| Go | 1.21+ | `registry.access.redhat.com/ubi9/go-toolset` |
| Ruby | 3.1 | `registry.access.redhat.com/ubi9/ruby-31` |
| .NET | 8.0 | `registry.access.redhat.com/ubi9/dotnet-80` |
| PHP | 8.1 | `registry.access.redhat.com/ubi9/php-81` |
| Perl | 5.32 | `registry.access.redhat.com/ubi9/perl-532` |

## Edge Cases

- **Multiple languages detected:** Report all, recommend primary based on entry point
- **Containerfile present:** Recommend Docker strategy but still detect language for metadata
- **No indicator files:** Report "Unknown" with Low confidence
- **Monorepo:** Check subdirectories for indicator files, report each component
