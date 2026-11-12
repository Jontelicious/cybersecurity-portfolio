# Cybersecurity Portfolio

**Cybersecurity and penetration-testing student | Linux security · Network segmentation · Python · Security verification**

This repository documents selected work from my cybersecurity studies and independent homelab projects. My focus is on implementing security controls, testing whether they behave as intended, and documenting both the results and their limitations.

The projects include Linux host hardening, virtualized network security, firewall verification, Python tooling and controlled AI-assisted software engineering experiments.

All work is presented as educational or personal technical experience, not professional employment.

## Featured projects

| Project | Technical focus | Documented results |
| --- | --- | --- |
| **[Firewall Policy Verification](firewall-verification/README.md)** | Python, nftables, network security testing | 14 passing live checks, four isolation timeouts corroborated by firewall counters, and no recorded failures in the documented test run. |
| **[Linux Mint Security Assessment & Hardening](linux-hardening/README.md)** | Linux hardening, auditing, system integrity | Lynis hardening index improved from 70 to 76; selected audit and kernel settings verified. |
| **[Debian RouterVM — Network Segmentation](router-vm/README.md)** | KVM/libvirt, routing, NAT, DHCP/DNS, nftables | Tested permitted connectivity and LAN3 isolation, including a reproducible firewall counter increase. |
| **[Cross-Agent Code Review](ai-agent-evaluation/README.md)** | Python, secure input handling, automated testing, AI-agent evaluation | Cross-review uncovered defects missed by initial passing tests; final independent verification recorded 20 passing tests. |

Results describe the specific documented configurations and test runs. They do not establish comprehensive security assurance or imply that all subsequent configurations were tested.

## Homelab infrastructure

I maintain two separate Linux virtualization environments for cybersecurity coursework and technical experimentation.

### Linux Mint — primary homelab

The permanent Linux Mint environment uses KVM/QEMU, libvirt and virt-manager.

Its documented work includes:

- An original Debian RouterVM with routing, NAT, DHCP/DNS and segmented virtual networks.
- Firewall policy implementation and independent connectivity verification.
- Linux host hardening and system auditing.
- A separate Alpine-based RouterVM v2 implementation undergoing bounded validation.

**Documentation:** [Debian RouterVM](router-vm/README.md) · [Firewall Verification](firewall-verification/README.md) · [RouterVM v2](projects/routervm-v2.md)

### Fedora KDE — portable homelab

The separate Fedora laptop provides a portable environment for coursework and demonstrations.

Documented components include:

- A temporary Debian RouterVM fallback for selected guest connectivity.
- Kali PentestVM with vulnerable-lab forwarding controls.
- An encrypted PrivateVM with host and guest firewall protections.
- A Windows 11 MalwareVM with BitLocker, FLARE-VM tooling and an offline configuration.

Host storage encryption, virtual networking, guest security controls and isolation testing are documented separately. A configured control is not automatically treated as a completely verified security boundary.

**Documentation:** [Portable Homelab Case Study](projects/portable-homelab.md)

**The Fedora environment does not replace the Linux Mint deployment.** Each host has independent configurations, storage, networks and verification requirements.

## Software engineering and security testing

### Firewall verification

I developed a repeatable Python-based checker for selected network security requirements, alongside a test matrix and dated observations from virtual machines.

The documented work includes:

- Positive and negative connectivity tests.
- Firewall counter correlation.
- DNS, HTTPS, DHCP and NAT checks.
- Automated tests for checker behavior.
- Explicit interpretation of inconclusive observations.

[Explore the implementation and evidence](firewall-verification/README.md)

### AI-assisted code review

I evaluated reusable coding-agent Skills through a controlled offline development exercise using Codex and OpenCode.

The agents independently developed Python utilities for processing synthetic Nmap XML, performed reciprocal code reviews and applied targeted corrections.

The evaluation demonstrated how passing tests can coexist with defects and why independent review, negative testing and cross-runtime verification matter.

[Read the evaluation](ai-agent-evaluation/README.md)

## Education and learning

I am studying cybersecurity and penetration testing in Sweden. The repository documents practical work alongside structured training.

- **[TryHackMe — Cyber Security 101](certifications/tryhackme-cyber-security-101.md):** Completed on 22 October 2026, with 45 hours and 23 minutes recorded on the completion certificate.
- **[TryHackMe — Jr Penetration Tester](training/tryhackme-jr-penetration-tester.md):** In progress. Last verified at 17% on 11 November 2026; Nmap Basic Port Scans was 5% complete at that checkpoint.

The Cyber Security 101 credential is a **learning-path completion certificate**, not the separate SEC1 professional certification.

[TryHackMe profile](https://tryhackme.com/p/macfarlane.jonathan)

## Technical skills and tools demonstrated

| Area | Technologies and techniques |
| --- | --- |
| Linux security | Linux Mint, Fedora, systemd, sysctl, Lynis, auditd, AIDE |
| Networking | IPv4 routing, NAT, nftables, dnsmasq, SSH, ICMP, network segmentation |
| Virtualization | KVM/QEMU, libvirt, virt-manager, virtual network bridges |
| Software engineering | Python, CLI development, Git, automated testing, code review |
| Security documentation | Test matrices, evidence preservation, technical reporting, architecture diagrams |
| Security environments | Kali Linux, isolated virtual machines, encryption and firewall controls |

These tools appear in documented educational or personal projects. Their inclusion is not a claim of professional-level expertise in every technology.

## Documentation approach

Each technical case study aims to explain:

1. The problem and intended objective.
2. The relevant environment and implementation.
3. Security assumptions and design decisions.
4. Testing methods and observed evidence.
5. Results, limitations and lessons learned.

Historical observations are labeled by environment and date. Successful individual checks are not generalized into claims of complete security.

[Technical case-study template](templates/technical-case-study.md)

## Current work and limitations

- RouterVM v2 requires further end-to-end segmentation and persistence verification.
- Fedora portable security controls require additional negative-path testing and backup/restore validation.
- Network monitoring and detection engineering remain [planned work](network-monitoring/README.md).
- Historical RouterVM and Linux hardening results apply to their documented configurations and dates.

## Responsible and authorized testing

The work documented here was performed in personal environments or within authorized educational activities.

This repository is intended to contain selected, sanitized technical documentation. Credentials, private keys, recovery information, confidential school-lab material and unreviewed operational evidence are excluded from intended publication.

Security findings and exploitation results are reported only to the extent supported by the available evidence.

---

**Recommended starting points:** [Firewall Verification](firewall-verification/README.md) · [Linux Hardening](linux-hardening/README.md) · [RouterVM](router-vm/README.md) · [Cross-Agent Code Review](ai-agent-evaluation/README.md)
