# Data Science Pipeline Management Task

You are an OpenShift AI engineer. The ML Ops team needs to set up and manage Data Science Pipelines (Kubeflow Pipelines 2.0) for their training workflow in namespace `ml-training`.

## Requirements

1. Verify or set up a Data Science Pipelines Application (DSPA) in the `ml-training` namespace
2. List existing pipeline runs and their statuses
3. Submit a new pipeline run from a YAML pipeline definition for a model training pipeline
4. Schedule a recurring pipeline run using a cron expression (`0 2 * * 1` - every Monday at 2 AM)
5. Monitor the running pipeline showing step-level progress and step pod statuses
6. Retrieve logs from individual pipeline step containers
7. Show how to manage pipeline lifecycle (list, get status, delete with proper warnings)

Write your complete analysis in `/solution/report.md`.
