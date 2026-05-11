# TrustyAI Model Monitoring Task

You are an OpenShift AI engineer. A credit scoring model `credit-risk-predictor` is deployed as an InferenceService in namespace `ml-finance`. The compliance team requires bias monitoring and drift detection before the model can process live traffic.

## Requirements

1. Verify the TrustyAIService CRD exists on the cluster (`trustyaiservices.trustyai.opendatahub.io`)
2. Check that the `credit-risk-predictor` InferenceService is deployed and Ready
3. Deploy a TrustyAIService instance in the `ml-finance` namespace if not already present
4. Configure **bias monitoring** with:
   - SPD (Statistical Parity Difference) metric on protected attribute `applicant_age` with favorable outcome `approved`, threshold ±0.1
   - DIR (Disparate Impact Ratio) metric on the same attribute, threshold 0.8-1.2
5. Configure **drift detection** with:
   - MeanShift detector on model outputs
   - FourierMMD detector for frequency-domain drift, with a 0.05 significance threshold
6. Validate monitoring by querying TrustyAI Prometheus metrics (`trustyai_spd`, `trustyai_dir`)
7. Present monitoring dashboard configuration and alerting thresholds

Write your complete analysis in `/solution/report.md`.
