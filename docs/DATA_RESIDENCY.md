# Data Residency

## Current Requirement

All data must reside in Australian regions. Enforced at the Terraform/IaC level.

- **Primary region:** Azure Australia East (`australiaeast`)
- **Secondary region:** Azure Australia Southeast (`australiasoutheast`)
- **Enforcement:** Azure Policy `allowed_locations` — no resource can be provisioned outside approved regions

## Future: Government / Defence

The IaC-enforced data residency is designed to be extensible for ISM PROTECTED-level data handling. When required, Terraform policies can be tightened to mandate certified regions, encryption-at-rest configurations, and network isolation controls without application-layer changes.
