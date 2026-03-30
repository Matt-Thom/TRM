# Temper Risk Management (TRM) — Development Roadmap

## Overview

A container-first development roadmap for **Temper Risk Management (TRM)** — an ISO 31000 and ISO 27001:2022 compliant risk management platform. The architecture is designed for multi-tenant SaaS delivery, targeting MSP client environments with integration into existing tooling (ConnectWise, Microsoft 365, CrowdStrike). Temper is a product of Subnet.

---

## Phase 1: Infrastructure, Containerization, and Core Scaffolding

The foundation prioritises local development velocity using Docker Compose, establishing the architecture that will eventually translate to Kubernetes for production. Tenant isolation and identity are treated as day-zero concerns — nothing ships without them.

### Docker Compose Dev Environment

Create a `docker-compose.yml` defining the entire local stack: FastAPI backend, Next.js frontend, PostgreSQL database, Redis (for message brokering), and a Celery worker container.

### Database & Multi-Tenancy Setup

Provision PostgreSQL. Implement Row-Level Security (RLS) policies at the database level. Configure SQLAlchemy in FastAPI to inject the current `tenant_id` into every session, ensuring data isolation is enforced by the database engine, not just application logic.

> **Architecture Note:** RLS is the hardest component to change after the fact and underpins every subsequent phase. The tenant isolation pattern must be proven and load-tested before any CRUD operations are built on top of it. Every table carrying tenant-scoped data must have RLS policies applied from initial migration — retrofitting is a showstopper for multi-tenant compliance.

### Backend Scaffolding (FastAPI)

Initialise the Python application. Set up Alembic for database migrations. Establish the Pydantic schemas for request/response validation.

### Authentication & Identity (Entra ID Early Registration)

Build the local authentication system using Argon2 password hashing and JWT issuance. Integrate `msal-python` to establish the OAuth2 flow for Microsoft Entra ID (Azure AD) SSO.

> **Integration Note:** Register a single multi-purpose Entra ID application at this stage with incremental consent scopes. This same app registration will later serve the Microsoft Graph API integration for Teams adaptive cards (Phase 4) and email notifications, avoiding a second registration and reducing Azure admin overhead. Define initial scopes for SSO only; Graph scopes (`ChannelMessage.Send`, `Mail.Send`) will be requested via incremental consent when those features are activated.

### Audit Trail Foundation

Build SQLAlchemy event listeners (`before_update`, `before_insert`, `before_delete`). Configure these to automatically write a record to an `audit_logs` table capturing the user ID, timestamp, the exact fields changed, old values, and new values.

> **Dependency Note:** The audit trail is moved into Phase 1 because it underpins the compliance evidence story for every subsequent phase. Getting the event listener pattern locked in before Risk Register CRUD goes live in Phase 2 means audit coverage is never retrofitted — every operation from day one is captured.

### Frontend Scaffolding (Next.js)

Initialise the Next.js application. Configure Tailwind CSS for styling and a state management library (like Zustand or Redux) to handle user sessions and tenant context.

---

## Phase 2: Core Risk Management Engine (ISO 31000)

This phase builds the CRUD operations and the logic required to identify and analyse risks. With RLS and audit logging already proven in Phase 1, every operation here is automatically tenant-isolated and fully auditable.

### Risk Register API

Develop FastAPI endpoints to handle the lifecycle of a risk entity (Identification, Threat Source, Vulnerability, Asset at Risk).

### Qualitative Scoring Matrix

Implement the logic for a 5x5 scoring grid. Create configuration endpoints so administrators can define the labels for Likelihood (e.g., Rare to Almost Certain) and Impact (e.g., Negligible to Severe), which automatically compute the Inherent Risk Score.

### Next.js Risk Dashboard

Build the primary user interface featuring a data table with filtering, sorting, and pagination for the risk register. Implement forms for creating and editing risk entries.

---

## Phase 3: ConnectWise Manage Integration

This phase connects the risk register to external asset and configuration data, fulfilling the asset management requirement.

### Asynchronous Task Queue

Configure Celery and Redis to handle background jobs, preventing long-running ConnectWise API calls from blocking the FastAPI web server.

### API Client Development

Write a dedicated Python module to interact with the ConnectWise Manage API, specifically targeting the `/company/configurations` endpoints.

### Asset Synchronisation

Create Celery tasks to periodically fetch Configuration Items (CIs) from ConnectWise and mirror relevant metadata (Name, Type, Status, EOL dates) into a local `assets` table.

### Risk-to-Asset Mapping

Build the UI and backend logic allowing users to search the synced ConnectWise CIs and link them to specific risks within the register as "Affected Assets."

---

## Phase 4: Treatment Workflows and Notifications

This phase shifts focus from identifying risks to acting on them, satisfying the "Risk Treatment" requirements of the ISO standards. The Entra ID app registration from Phase 1 is extended here with Graph API scopes via incremental consent — no new Azure admin setup required.

### Treatment State Machine

Implement a workflow engine in FastAPI for risk treatments (Draft, Pending Approval, Mitigated, Accepted).

### Microsoft Graph API Integration

Using the existing Entra ID app registration from Phase 1, request incremental consent for Graph API scopes. Build functions to dispatch actionable adaptive cards to specific Microsoft Teams channels when a risk requires approval.

### SMTP Email Alerts

Configure an email service to dispatch notifications for overdue risk reviews or critical score changes.

### Treatment UI

Build Next.js interfaces for assigning "Risk Owners," documenting existing controls, proposing new treatments, and calculating the anticipated "Residual Risk Score."

---

## Phase 5: ISO 27001 Compliance Artifacts and Board Reporting

This phase translates the operational data into the formal evidence required by auditors and the visual summaries required by executives.

### Annex A Control Library

Seed the database with the 93 controls from ISO 27001:2022.

### Statement of Applicability (SoA) Builder

Create an interface where users evaluate each Annex A control against their risk register, mark it as Included/Excluded, provide justification, and link to internal policies.

### Risk Treatment Plan (RTP) Generator

Build a reporting engine (using a library like ReportLab for Python or a headless browser service) to compile all accepted treatments, owners, and timelines into a formalised, timestamped PDF document.

### Executive Dashboards

Implement charting libraries (like Recharts or Chart.js) in Next.js to visualise the organisation's risk posture. Build heat maps showing risk distribution and trend lines demonstrating risk reduction over time.

---

## Phase 6: Production Kubernetes Deployment

Transitioning from the local Docker Compose environment to a highly available production environment hosted in Australia.

| Component | Production Strategy (Kubernetes) |
| :--- | :--- |
| **Container Images** | Create multi-stage Dockerfiles for both FastAPI and Next.js to minimise image size and attack surface. Push to a private container registry. |
| **Workloads** | Define Kubernetes `Deployment` manifests for the frontend, backend web server, and Celery workers. Configure Horizontal Pod Autoscaling (HPA) based on CPU/Memory usage. |
| **Networking** | Implement an `Ingress` controller to route external traffic. Automate TLS certificate provisioning using cert-manager. |
| **Configuration & Secrets** | Store environment variables in `ConfigMaps`. Store database credentials, ConnectWise API keys, and Azure secrets securely using Kubernetes `Secrets` or an external vault. |
| **Data Persistence** | Deploy PostgreSQL and Redis using Helm charts, backed by `PersistentVolumeClaims`. |
| **Data Residency (IaC-Enforced)** | Australian data residency is enforced at the Terraform/IaC level, not reliant on Helm chart configuration alone. Azure Australia East is the primary region. Region constraints are codified in Terraform `allowed_locations` policies so that no resource can be provisioned outside approved regions, regardless of who is deploying. |

> **Future Consideration — Government / Defence:** The current architecture does not target Defence customers, but data residency enforcement at the IaC level is designed to be extensible. When Government or Defence classification requirements are introduced (e.g., PROTECTED-level data under the ISM), the Terraform policies can be tightened to mandate specific certified regions, encryption-at-rest configurations, and network isolation controls without requiring architectural changes to the application layer.

---

## Recommended Implementation Order

The closing recommendation is to begin with a **detailed technical specification of the Row-Level Security architecture** (Phase 1), as it is the foundation every other phase builds on and the most difficult component to change retroactively. The specification should cover:

- PostgreSQL RLS policy definitions per table
- SQLAlchemy session-level `tenant_id` injection pattern
- Migration strategy (Alembic) for adding RLS to new tables
- Testing approach to verify tenant isolation under concurrent load
- Edge cases: cross-tenant reporting, superadmin access, tenant onboarding/offboarding
