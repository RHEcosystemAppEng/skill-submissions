# TrustyAI Guardrails Configuration Task

You are an OpenShift AI engineer. A team has deployed an LLM InferenceService called `llama-3-chat` in namespace `ml-production` and needs content safety guardrails before exposing it to end users.

## Requirements

1. Verify the GuardrailsOrchestrator CRD is available on the cluster (from `trustyai.opendatahub.io`)
2. Check that the `llama-3-chat` InferenceService exists and is Ready
3. Configure the following detectors:
   - **Content safety**: using `ibm-granite/granite-guardian-3.1-2b` as the detector model
   - **PII detection**: using built-in regex-based patterns
   - **Prompt injection**: using the granite-guardian model
4. Create the detector ConfigMap (`guardrails-config-llama-3-chat`) with detection on both input and output, policy set to "block"
5. Deploy a GuardrailsOrchestrator CR (`guardrails-llama-3-chat`) referencing the ConfigMap
6. Verify the orchestrator pod is running and the guarded endpoint responds
7. Test both a safe request and an unsafe request (prompt injection attempt) against the guarded endpoint

Write your complete analysis in `/solution/report.md`.
