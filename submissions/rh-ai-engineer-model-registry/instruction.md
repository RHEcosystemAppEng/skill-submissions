# Model Registry Management Task

You are an OpenShift AI engineer. The ML team has trained a new fraud detection model and needs to register it in the Model Registry, create a versioned entry with storage URI, and plan a promotion from dev to production.

## Requirements

1. Verify the Model Registry instance is deployed in the cluster
2. List existing registered models and their versions
3. Register a new model called `fraud-detector-v2` with:
   - Description: "XGBoost fraud detection model for payment transactions"
   - Custom properties: framework=xgboost, task=classification, dataset=payments-2026-q1
4. Create a ModelVersion `v2.1.0` with:
   - Storage URI: `s3://ml-models/fraud-detector/v2.1.0/model.onnx`
   - State: "LIVE"
   - Author and creation metadata
5. Create a ModelArtifact linking the version to its storage location
6. Plan a cross-environment promotion workflow (dev -> staging -> prod) using RHOAI Data Science Projects and data connections
7. Show how to deploy the registered model version via `/model-deploy`

Write your complete analysis in `/solution/report.md`.
