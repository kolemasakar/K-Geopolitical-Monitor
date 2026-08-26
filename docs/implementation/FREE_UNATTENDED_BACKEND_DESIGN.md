# Free Unattended Backend Design

Status: ACTIVE_PREPARATION
Date: 2026-08-26
Project: K-Geopolitical Monitor
Deployment class: OWNER_ONLY_TEST
Runtime storage: PROJECT_LOCAL_ONLY

## Goal

Run the existing K-Geopolitical Monitor monitoring runtime continuously without manual user initiation while preserving the approved project-local storage and truth boundaries.

This is a post-Phase-11 test deployment design. It does not approve production/live OPERATIONAL status, shared runtime storage, external publishing or a new roadmap phase.

## Primary Free Host Candidate - Oracle Cloud Infrastructure

Official Oracle Free Tier information rechecked on 2026-08-26.

Always Free Ampere A1 allowance for an Always Free tenancy is currently equivalent to:
- 2 OCPUs total;
- 12 GB memory total;
- 1,500 OCPU hours per month;
- 9,000 GB memory-hours per month;
- up to 200 GB total boot plus block volume storage in the home region;
- up to 10 TB outbound data transfer per month under the Always Free allowance.

Recommended pilot allocation:
- shape: VM.Standard.A1.Flex;
- architecture: Arm64;
- OCPU: 2;
- RAM: 12 GB;
- OS: Ubuntu 24.04 LTS Arm64;
- boot volume: 50 GB initially;
- public IPv4: allowed for the initial test, with minimal ingress;
- region: choose the home region carefully because Always Free compute must be created there.

Oracle constraints to treat as deployment risks:
- Always Free A1 capacity can be unavailable in a selected home region;
- idle Always Free compute may be reclaimed under Oracle idle-resource rules;
- registration normally requires phone and credit-card verification even though Always Free usage is not charged unless the account is upgraded/usage exceeds free limits.

Do not create artificial load merely to evade an idle-resource policy. Real monitoring activity and normal health checks must be sufficient or the host should be considered unsuitable.

## Fallback Free Host - Google Cloud

Current Google Cloud Free Tier provides, for eligible customers:
- one e2-micro VM usage allowance per month in supported US regions;
- up to 30 GB standard persistent disk;
- a much smaller free outbound-data allowance than OCI.

Use Google only as fallback because the e2-micro CPU/RAM envelope is materially weaker for the combined collector, analysis, API and dashboard workload.

## Pilot Host Layout

Recommended project path:
/opt/k-geopolitical-monitor

Required runtime layout:
/opt/k-geopolitical-monitor/
  src/
  scripts/
  data/
    kgeopolitical_monitor.db
  logs/                 optional application logs

The SQLite database must remain under the project data directory because RuntimeStoragePolicy rejects database paths outside PROJECT_LOCAL_ONLY data_root.

Do not expose SQLite over the network.

## Process Model

System manager:
- systemd

Target processes during the first unattended pilot:
- kgm-monitor.service - continuous monitoring supervisor;
- later: kgm-api.service - private HTTPS/API surface for GPT Actions;
- later: kgm-dashboard.service - read-only admin dashboard, preferably served by the same API application if practical.

The first deployment should enable only the monitoring service. API/dashboard exposure is a separate test gate.

## Monitoring Service Semantics

Existing components are reused:
- OperationalMonitoringRuntime determines due watches and persists monitoring runs;
- recover_interrupted_runs marks abandoned RUNNING work after restart;
- MonitoringCycle or another approved cycle executor handles each due watch;
- per-watch failures remain persisted and isolated;
- the post-Phase-11 UnattendedMonitoringService adds only the long-running supervisor loop.

Required startup sequence:
1. service manager starts process after boot/network readiness;
2. project-local database initializes/migrates;
3. interrupted RUNNING monitoring runs are recovered exactly once per process startup;
4. due watches are evaluated;
5. approved collection/processing cycle executes;
6. process sleeps for a bounded poll interval;
7. loop repeats until service stop/restart.

Unexpected supervisor exceptions must terminate the process rather than be silently swallowed. systemd must restart the process and retain the failure in journal logs. Per-watch exceptions remain handled by the cycle executor and persisted as FAILED run state.

## Proposed systemd Policy

Pilot target values:
- Restart=on-failure
- RestartSec=10
- StartLimitIntervalSec=300
- StartLimitBurst=10
- User=kgm
- WorkingDirectory=/opt/k-geopolitical-monitor
- Environment=PYTHONUNBUFFERED=1

Do not create the final unit until the concrete live cycle entry point is validated. The service supervisor module alone is intentionally processor-agnostic.

## Polling and Resource Budget

Initial supervisor poll interval:
- 60 seconds

This does not mean every source is fetched every 60 seconds. Each watch retains its own cadence. The supervisor only asks which watches are due.

Suggested test envelopes:
- normal CPU target: mostly low, with short collection/analysis bursts;
- application memory target: under 2 GB during the initial source set;
- SQLite/database plus logs: under 10 GB initially;
- free disk reserve: keep at least 20 percent free;
- outbound traffic: monitor actual usage even though OCI allowance is large.

## Network Security Baseline

Initial monitoring-only host:
- inbound SSH 22: restrict by source IP where practical;
- inbound 80/443: CLOSED until API/dashboard gate;
- database ports: CLOSED;
- all outbound requests: HTTPS only for approved public-source adapters where supported.

When GPT Actions are later enabled:
- expose only HTTPS 443 through a controlled reverse proxy/tunnel/API gateway;
- do not expose admin dashboard publicly by default;
- require explicit API authentication policy;
- add privacy-policy and Action contract review before any public sharing.

## Backup Baseline

During owner-only test:
- create project-local SQLite backup before migrations/deploy updates;
- maintain at least one recent off-host backup before unattended operation is considered stable;
- validate restore, not only backup creation.

Oracle Always Free includes volume-backup allowance, but project-level SQLite backup/restore must remain independently testable.

## Dashboard Placement

Free/test dashboard remains inside this project and reads the same project-local runtime state.

Initial access:
- localhost on the VM, or SSH tunnel from the owner workstation;
- read-only;
- no public anonymous access.

Recommended later implementation:
- FastAPI-based admin/API process;
- server-rendered minimal HTML or similarly low-resource UI;
- no separate frontend platform required for the first pilot.

## Pilot Deployment Gates

Gate A - Free host availability
- OCI account available;
- A1 capacity available in chosen home region;
- VM created inside free allowance.

Gate B - Base system
- Ubuntu patched;
- non-root service user created;
- SSH access verified;
- repository checkout and Python environment validated.

Gate C - Project-local runtime
- full test suite green on ARM64 host;
- RuntimeStoragePolicy keeps DB under project data/;
- migrations complete;
- backup/restore smoke passes.

Gate D - Unattended restart
- monitoring service starts automatically after reboot;
- interrupted RUNNING state is recovered;
- due watches resume without manual command;
- repeated startup does not duplicate completed work.

Gate E - Live controlled pilot
- approved live adapters collect successfully or fail visibly;
- failures do not terminate unrelated watches;
- coverage state updates;
- no truth-boundary regression.

Only after these gates should the private GPT Action/API connection be designed as the next pilot step.

## Current Decision

Primary free unattended host candidate: ORACLE_OCI_ALWAYS_FREE_A1
Fallback: GOOGLE_CLOUD_E2_MICRO
Current production/live status: NOT_OPERATIONAL
Current runtime mode: PROJECT_LOCAL_ONLY
Shared production runtime: DEFERRED
