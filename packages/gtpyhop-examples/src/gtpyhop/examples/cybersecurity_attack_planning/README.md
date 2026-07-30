# Cybersecurity Attack Planning

## Overview

Models insider attacks against a network with a Document Management System (DMS), based on the **BAMS (Behavioral Adversary Modeling System)** domain from Boddy et al. (ICAPS 2005) and the hierarchy design by Pragst (2013/2014).

A malicious insider (Bob) attempts to steal a secret document from a DMS server using combinations of physical, cyber, and malware attacks. The planner generates attack plans that help network administrators identify vulnerabilities — this is a **defensive** tool.

The domain demonstrates:
- **HTN decomposition** of multi-phase attacks into primitive actions
- **Backtracking** across alternative attack strategies when countermeasures block a path
- **5 BAMS modules**: Physical, Process, Network, DMS, Malware

## Scenarios

| # | Scenario | Attack path | Backtracking | Greedy | Actions |
|---|----------|-------------|--------------|--------|---------|
| 1 | `direct_access` | Known DMS credentials, ACL granted | None | OK | 8 |
| 2 | `shoulder_surfing` | Physical observation of password typing | None | OK | 11 |
| 3 | `network_sniffing` | Sniff DMS password from hub traffic | None | OK | 10 |
| 4 | `locked_room_fallback` | Door locked, surf fails at `a_open_door`, backtrack to sniff | cred: surf -> sniff | **FAIL** | 10 |
| 5 | `firewall_sniff_blocked` | Firewall would block sniffing, but surf succeeds first | None | OK | 11 |
| 6 | `admin_acl_change` | Sniff admin password, modify document ACL, then DMS access | None | OK | 12 |
| 7 | `direct_client_hack` | No ACL and no admin path, legitimate fails, malware relay | top: legit -> malware | **FAIL** | 6 |
| 8 | `custom_virus_bypass` | Scanner blocks known virus, custom virus bypasses it | top + malware: known -> custom | **FAIL** | 6 |
| 9 | `covert_exfiltration` | Sniff credentials, no ACL, malware relay | top: legit -> malware | **FAIL** | 8 |

### What makes each scenario interesting

- **S1-S3**: Each uses a different credential acquisition method (direct knowledge, physical observation, network sniffing). Same goal, different attack vectors.
- **S4**: Backtracking in action. The locked door causes `a_open_door` to fail at action execution time. The shoulder surfing decomposition collapses, and the planner falls back to network sniffing. The greedy planner commits to shoulder surfing and fails.
- **S5**: The firewall would block sniffing, but shoulder surfing is tried first in the method ordering and succeeds. Demonstrates that method ordering provides natural resilience.
- **S6**: Multi-step attack combining credential sniffing and privilege escalation. The planner sniffs the admin password, uses it to modify the document ACL, then proceeds with standard DMS access.
- **S7-S9**: Malware-based attacks. The legitimate DMS path fails (no ACL, no admin), so the planner backtracks to covert malware relay — deploying a virus, injecting code into the server, and relaying the document without ever touching the DMS directly.
- **S8**: Double backtracking. First the legitimate path fails, then within the malware path, the known virus is caught by the scanner. The planner falls back to writing a custom virus (requires `tech_skill = high`).

## Domain Structure

### Actions (21)

| Module | Actions | Description |
|--------|---------|-------------|
| Physical (5) | `a_move_to_room`, `a_sit_at_host`, `a_leave_host`, `a_open_door`, `a_shoulder_surf` | Movement, positioning, physical observation |
| Process (4) | `a_login`, `a_launch_shell`, `a_nes_admin_login`, `a_dms_group_allow` | Authentication, shell access, admin operations |
| Network (2) | `a_start_sniffer`, `a_read_sniffer` | Packet sniffing on hub networks |
| DMS (6) | `a_start_dms_session`, `a_dms_find_client`, `a_dms_connect`, `a_dms_auth_password`, `a_dms_auth_certificate`, `a_dms_request_and_read` | Document Management System pipeline |
| Malware (4) | `a_deploy_known_virus`, `a_write_custom_virus`, `a_inject_code`, `a_relay_document` | Virus deployment, code injection, covert relay |

### Methods (16)

| Task | Alternatives | Backtracking point |
|------|-------------|-------------------|
| `m_steal_secret_document` | `m_steal_via_legitimate_access`, `m_steal_via_malware_relay` | Top-level strategy |
| `m_gain_credentials` | `m_credentials_already_known`, `m_credentials_via_shoulder_surf`, `m_credentials_via_sniff` | Credential acquisition |
| `m_gain_system_access` | (single method) | — |
| `m_gain_document_access` | `m_access_already_granted`, `m_access_via_admin` | Document permissions |
| `m_gain_admin_credentials` | `m_admin_credentials_already_known`, `m_admin_credentials_via_sniff` | Admin access |
| `m_dms_exfiltrate` | (single method) | — |
| `m_dms_authenticate` | `m_dms_auth_via_password`, `m_dms_auth_via_certificate` | DMS authentication |
| `m_deploy_and_relay` | (single method) | — |
| `m_deploy_malware` | `m_deploy_via_known_virus`, `m_deploy_via_custom_virus` | Virus scanner evasion |

## Usage

```python
import gtpyhop
from gtpyhop.examples.cybersecurity_attack_planning import the_domain, get_problems

problems = get_problems()

# Run scenario 4 (requires backtracking)
state, tasks, desc = problems['scenario_4_locked_room_fallback']
with gtpyhop.PlannerSession(domain=the_domain, verbose=1,
        strategy='iterative_dfs_backtracking') as s:
    result = s.find_plan(state, tasks)

print(f"Success: {result.success}, Actions: {len(result.plan)}")
for i, action in enumerate(result.plan):
    print(f"  {i}: {action}")
```

Run doctests:

```bash
python -m doctest -v src/gtpyhop/examples/cybersecurity_attack_planning/problems.py
```

## References

1. Boddy, M., Gohde, J., Haigh, T., Harp, S. (2005). "Course of Action Generation for Cyber Security Using Classical Planning." *Proceedings of ICAPS 2005*, pp. 12-21.
2. Boddy, M., Shackleton, H. (2007). "The Behavioral Adversary Modeling System — Console Based Generator." *The Second International Competition on Knowledge Engineering for Planning and Scheduling*, 2007.
3. Pragst, L. (2013). "Hybrid Planning in Cyber Security Applications." Bachelor thesis defense slides, Ulm University. 20 November 2013.
4. Pragst, L., Richter, F., Bercher, P., Schattenberg, B., Biundo, S. (2014). "Introducing Hierarchy to Non-Hierarchical Planning Models — A Case Study for Behavioral Adversary Models." *28th PuK Workshop*, 2014.

## File Structure

```
cybersecurity_attack_planning/
├── __init__.py     # Package initialization
├── domain.py       # 21 actions, 16 methods
├── problems.py     # 9 scenarios, 71 doctests
└── README.md       # This file
```

---
*Generated 2026-04-14*
