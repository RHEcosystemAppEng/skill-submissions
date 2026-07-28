---
name: quality-extended-demo
description: Intentionally triggers new quality scanner checks from PR #59
---

# Quality Extended Demo Skill

This skill handles all tasks related to full-stack application development,
deployment, monitoring, security, compliance, and infrastructure management.
It manages every request from initial design through production operations.

## General Rules

You must always follow proper coding standards when writing any code.
You should always validate inputs before processing them.
Never skip testing when making changes to production code.
Always ensure that error handling covers all edge cases.
Make sure to document all public interfaces thoroughly.
You must handle authentication correctly in every endpoint.
Always verify that database migrations are reversible.
Never deploy without running the full test suite first.
You should ensure that logging covers all critical paths.
Make sure to follow the principle of least privilege everywhere.
You must always sanitize user inputs at every boundary.
Never allow unvalidated data to reach the database layer.
Always ensure that API responses follow the schema contract.
You should make sure that retry logic has proper backoff.
Never expose internal error details to external consumers.

## Prohibited Practices

Don't use global variables for state management.
Never use eval() or exec() for dynamic code execution.
Avoid using string concatenation for SQL queries.
Don't store passwords in plain text anywhere.
Never commit secrets or API keys to version control.
Avoid using deprecated APIs or library versions.
Don't use synchronous I/O in async contexts.
Never bypass input validation for internal calls.
Avoid using wildcard imports in production code.
Don't use mutable default arguments in function definitions.

## Technology Requirements

Use text-davinci-003 for generating code documentation.
Build frontend components with create-react-app tooling.
Ensure compatibility with Python 3.7 for legacy system support.
Use tslint for TypeScript code quality enforcement.
Target Node 16 as the minimum supported runtime version.
Use gpt-3.5-turbo for classification tasks.

## Architecture Guidelines

The system must always process data through the validation layer first.
You should never allow direct database access from controller methods.
Always ensure that service boundaries are properly defined.
Make sure that caching strategies account for data staleness.
Never expose internal service addresses to external consumers.
You must always use structured logging with correlation identifiers.
Always verify that circuit breakers have proper fallback behavior.
You should ensure that health checks cover all downstream dependencies.
Never allow background jobs to run without proper timeout limits.
Make sure to implement proper graceful shutdown procedures.
Always ensure that message queues have dead letter configurations.
You must handle partial failures in distributed transactions.
Never allow unbounded growth of in-memory data structures.
Always ensure that connection pools have proper size limits.
You should make sure that rate limiting applies to all public endpoints.

## Monitoring Requirements

You must always emit metrics for all critical business operations.
Never ignore alerts from the monitoring system without investigation.
Always ensure that dashboards reflect the current system architecture.
You should make sure that alerting thresholds are based on SLO targets.
Never allow monitoring gaps in newly deployed services.
Always ensure that log aggregation captures all service instances.
You must implement proper distributed tracing across service boundaries.
Make sure that error budgets are tracked and visible to all teams.

## Deployment Standards

You must always use immutable infrastructure for production deployments.
Never perform manual changes to production configurations.
Always ensure that rollback procedures are tested and documented.
You should make sure that canary deployments cover sufficient traffic.
Never skip smoke tests after deploying to a new environment.
Always ensure that feature flags have proper expiration dates.
You must implement blue-green deployments for zero-downtime releases.
Make sure that deployment pipelines include security scanning steps.

## Data Management

You must always encrypt sensitive data at rest and in transit.
Never store personally identifiable information without proper consent.
Always ensure that data retention policies are enforced automatically.
You should make sure that backup procedures are tested regularly.
Never allow data migrations to run without a tested rollback plan.
Always ensure that audit trails cover all data modification operations.
You must implement proper data masking for non-production environments.
Make sure that data classification labels are maintained consistently.

## Security Hardening

You must always apply security patches within the defined SLA window.
Never expose debugging endpoints in production environments.
Always ensure that authentication tokens have proper expiration times.
You should make sure that CORS policies are as restrictive as possible.
Never allow cross-site scripting vulnerabilities in user-facing pages.
Always ensure that content security policies are properly configured.
You must implement proper session management with secure cookie flags.
Make sure that API rate limiting prevents abuse from single sources.

## Performance Requirements

You must always profile critical paths before and after changes.
Never introduce N+1 query patterns in database access code.
Always ensure that pagination is implemented for large result sets.
You should make sure that lazy loading is used for expensive operations.
Never allow memory leaks in long-running service processes.
Always ensure that response times meet the defined SLO targets.
You must implement proper connection pooling for all external services.
Make sure that caching strategies have proper invalidation logic.

## Testing Standards

You must always maintain minimum code coverage above the threshold.
Never merge pull requests without passing all required checks.
Always ensure that integration tests cover all critical user journeys.
You should make sure that load testing validates performance targets.
Never skip contract testing for services with external consumers.
Always ensure that chaos engineering experiments run in staging first.
You must implement proper test data management and cleanup procedures.
Make sure that end-to-end tests are stable and not flaky.

## Compliance Requirements

You must always follow the established change management procedures.
Never bypass the approval workflow for production access requests.
Always ensure that compliance audits are completed on schedule.
You should make sure that regulatory requirements are tracked properly.
Never allow non-compliant configurations to persist in production.
Always ensure that incident response procedures are current and tested.
You must implement proper evidence collection for audit requirements.
Make sure that access reviews are conducted at the required frequency.

## API Design Standards

You must always version all public APIs from the initial release.
Never break backwards compatibility without a proper deprecation period.
Always ensure that API documentation is generated from source code annotations.
You should make sure that all endpoints return consistent error response formats.
Never allow API consumers to bypass authentication for any endpoint.
Always ensure that request and response schemas are validated against contracts.
You must implement proper content negotiation for all resource endpoints.
Make sure that hypermedia links are included in API responses for discoverability.
You must always use standard HTTP status codes correctly in all responses.
Never return 200 OK for operations that actually failed or partially succeeded.
Always ensure that bulk operations have proper pagination and cursor support.
You should make sure that webhook deliveries include signature verification.
Never allow API keys to be passed as URL query parameters in production.
Always ensure that GraphQL queries have proper depth and complexity limits.
You must implement proper request throttling based on client authentication tier.
Make sure that long-running operations use async patterns with status polling.

## Observability Standards

You must always implement structured logging with consistent field naming.
Never log sensitive information such as passwords or authentication tokens.
Always ensure that distributed traces propagate context across service boundaries.
You should make sure that custom metrics follow the naming convention standards.
Never allow silent failures that do not emit any observability signals.
Always ensure that error rates are captured with sufficient dimensional labels.
You must implement proper log sampling for high-volume transaction paths.
Make sure that observability dashboards are reviewed and updated quarterly.
You must always correlate logs, metrics, and traces using shared identifiers.
Never rely solely on log-based monitoring for critical availability signals.
Always ensure that synthetic monitoring covers all critical user-facing paths.
You should make sure that alert routing rules are tested after every change.
Never allow observability data retention to exceed the defined storage budget.
Always ensure that custom instrumentations do not degrade application performance.
You must implement proper cardinality management for all metric dimensions.
Make sure that runbook links are attached to all actionable alert definitions.

## Documentation Standards

You must always keep architecture decision records current and accessible.
Never allow documentation to drift more than one sprint behind the code.
Always ensure that onboarding guides are tested by new team members regularly.
You should make sure that runbooks cover all known failure scenarios.
Never publish documentation without proper review and approval workflow.
Always ensure that API changelogs are maintained for every versioned release.
You must implement proper search and navigation for internal documentation.
Make sure that documentation includes diagrams for complex system interactions.
You must always maintain a glossary of domain-specific terminology.
Never assume that readers have context about previous design decisions.
Always ensure that troubleshooting guides include step-by-step resolution paths.
You should make sure that configuration reference documents all available options.

## Infrastructure as Code

You must always manage infrastructure through version-controlled definitions.
Never apply manual changes to any infrastructure component in production.
Always ensure that infrastructure changes go through the same review process.
You should make sure that terraform state is stored in a shared remote backend.
Never allow infrastructure drift to persist without triggering remediation.
Always ensure that infrastructure modules are tested before promotion.
You must implement proper secret management for infrastructure credentials.
Make sure that infrastructure costs are tracked and attributed to team budgets.

## Incident Management

You must always classify incidents according to the severity matrix definitions.
Never close an incident without a documented root cause analysis and timeline.
Always ensure that incident communication follows the established templates.
You should make sure that post-incident reviews are scheduled within five days.
Never allow recurring incidents without tracking them as a known problem record.
Always ensure that incident escalation paths are current and regularly tested.
You must implement proper incident command rotation for all on-call schedules.
Make sure that incident metrics are reported to leadership at monthly cadence.
You must always preserve evidence and logs for incidents above severity two.
Never modify production systems during an active incident without coordinator approval.
Always ensure that customer communications are sent within the defined SLA window.
You should make sure that runbooks are updated after every new incident pattern.
Never allow knowledge gaps to persist after a post-incident review is completed.
Always ensure that action items from reviews have owners and target completion dates.
You must implement proper handoff procedures for incidents spanning multiple shifts.
Make sure that incident tooling access is provisioned for all on-call personnel.

## Capacity Planning

You must always maintain capacity forecasts for at least three months forward.
Never allow resource utilization to exceed eighty percent during normal operations.
Always ensure that auto-scaling policies have proper minimum and maximum bounds.
You should make sure that capacity models account for seasonal traffic patterns.
Never provision infrastructure without verifying cost estimates against the budget.
Always ensure that reserved capacity contracts are reviewed before renewal dates.
You must implement proper capacity monitoring dashboards with trend analysis.
Make sure that capacity planning reviews happen before major feature launches.
You must always test that auto-scaling responds correctly to rapid traffic spikes.
Never assume that historical growth rates will apply to new product features.
Always ensure that database storage projections include index growth estimates.
You should make sure that CDN capacity is sufficient for expected media volumes.
Never allow capacity constraints to cause customer-facing degradation silently.
Always ensure that load balancer connection limits are sized for peak traffic.
You must implement proper queue depth monitoring with automatic scaling triggers.
Make sure that disaster recovery sites have sufficient capacity for full failover.

## Release Management

You must always follow the established release cadence and freeze schedules.
Never deploy untested changes to production outside the release window.
Always ensure that release notes document all user-facing and breaking changes.
You should make sure that rollback procedures are validated before each release.
Never allow hotfixes to bypass the minimum required review and testing steps.
Always ensure that feature flags are cleaned up within two sprints of launch.
You must implement proper release artifact signing and verification procedures.
Make sure that release metrics are tracked and reviewed for process improvement.
You must always coordinate releases with dependent teams through shared calendars.
Never assume that downstream consumers will adapt to breaking changes immediately.
Always ensure that staged rollouts include proper validation gates between phases.
You should make sure that release communications reach all affected stakeholders.
Never allow release automation to proceed when upstream validation checks fail.
Always ensure that configuration changes are versioned alongside code releases.
You must implement proper changelog generation from structured commit messages.
Make sure that release retrospectives identify bottlenecks and improvement areas.

## Dependency Management

You must always keep dependency versions pinned to specific release numbers.
Never allow transitive dependencies to introduce known security vulnerabilities.
Always ensure that dependency update PRs include changelog review summaries.
You should make sure that license compatibility is verified for all new packages.
Never allow dependency sprawl without periodic review and consolidation efforts.
Always ensure that private registry access tokens are rotated on schedule.
You must implement proper dependency caching strategies for build performance.
Make sure that dependency graph analysis runs as part of the CI pipeline.
You must always verify that dependency updates do not introduce breaking changes.
Never adopt alpha or beta packages in production without explicit risk acceptance.
