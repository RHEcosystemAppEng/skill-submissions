# Incident Triage Task

You are a Red Hat OpenShift engineer. An alert `PodCrashLooping` has fired in namespace `ecommerce-prod` for the `checkout-api` Deployment. The on-call team reports that checkout transactions are failing intermittently since approximately 08:30 UTC.

## Requirements

1. Use the `openshift` MCP tools (`resources_get`, `resources_list`, `pod_list`, `pod_logs`, `events_list`) to gather the current state of the `checkout-api` Deployment, its ReplicaSets, Pods, and Events.
2. Apply the **Five Whys** methodology to trace from the alert symptom to the root cause.
3. Apply the **investigation guardrails** from the incident-triage skill: Exhaustive Verification, Contradicting Evidence Search, Causal Depth, Evidence-Based Claims Only, and Investigation Error Separation.
4. Perform an **Adversarial Due Diligence** review with confidence scoring across the 8 dimensions: Causal Completeness, Target Accuracy, Evidence Sufficiency, Alternative Hypotheses, Scope Completeness, Proportionality, Regression Awareness, and Confidence Calibration.
5. Present a structured **Root Cause Analysis** with a causal chain, remediation target (the misconfigured resource, NOT the symptom reporter), and signal classification.

Write your complete investigation report in `/solution/report.md`.
