# Fedora Portable Cybersecurity Homelab

**Project type:** Personal cybersecurity infrastructure and educational lab  
**Environment:** Fedora 45 KDE, KVM/QEMU, libvirt, virt-manager  
**Evidence checkpoint:** 11 November 2026  
**Status:** Operational components and selected security controls verified; comprehensive isolation, persistence and recovery validation incomplete

## 1. Objective and context

This project establishes a portable, encrypted virtualization environment for cybersecurity coursework, security-tool development, malware-analysis preparation and technical demonstrations.

The main objective was to make selected lab workloads available on a Fedora laptop while preserving the existing permanent Linux Mint homelab.

The two environments have separate hypervisors, VM definitions, storage, networks and verification requirements. The Fedora deployment is not a replacement for Mint.

Key design goals included:

- Protecting host and selected guest data at rest.
- Separating workloads with different trust requirements.
- Providing controlled networking for authorized exercises.
- Limiting unnecessary interaction between vulnerable or malware-analysis environments and other workloads.
- Keeping configuration and validation evidence specific to each machine.

The project uses layered controls rather than relying on one firewall, virtual network or encryption mechanism.

## 2. Technical environment

The portable host is an Acer Nitro V 15 laptop running Fedora 45 KDE with KVM/QEMU, system libvirt and virt-manager.

The documented environment includes the following main virtual machines:

| VM | Primary role | Main security considerations |
| --- | --- | --- |
| Debian RouterVM fallback | Routing, DHCP and DNS for AgentVM | Restricted, two-network fallback configuration |
| AgentVM | Coding-agent experimentation | Dedicated agent network and controlled connectivity |
| Kali PentestVM | Authorized penetration-testing coursework and vulnerable exercises | Disk encryption, forwarding guard and Docker lab networks |
| PrivateVM | Separate personal browsing and communications | Guest encryption, guest firewall and host ingress policy |
| Windows MalwareVM | Offline malware-analysis preparation and demonstrations | BitLocker, analysis tooling, network and clipboard restrictions |

A separate temporary Windows servicing VM was also used during MalwareVM preparation. Its presence in historical records does not establish that it remains deployed or has been deleted.

### Relationship to Linux Mint

The Linux Mint desktop remains the primary homelab.

It retains the original Debian RouterVM, the separate Alpine RouterVM v2 project and its own virtualization and networking infrastructure.

The Fedora fallback is a copied and adapted Debian RouterVM, not a completed migration of Alpine RouterVM v2.

Validation results from one host must not be attributed to the other.

## 3. Architecture and implementation

### Host virtualization and storage

Fedora uses KVM/QEMU, libvirt and virt-manager to host the portable virtual machines.

LUKS2 encryption was confirmed for the Fedora host storage. This provides a host-level data-at-rest protection layer, subject to the usual assumptions about key management, system state and physical access.

Guest disk encryption is tracked separately because host encryption does not automatically provide an equivalent independent protection boundary for each running guest.

### Debian RouterVM fallback

The original Debian RouterVM was copied from the Mint environment and adapted for Fedora's virtualization configuration.

The fallback was deliberately simplified to use two networks:

- `travel-nat` for upstream connectivity.
- `agent-net` for AgentVM connectivity.

The migration involved adapting the VM definition, network attachments and guest routing services to Fedora.

The resulting configuration uses dnsmasq for AgentVM DHCP/DNS and nftables for forwarding and source NAT.

On 6 November 2026, controlled validation recorded:

- Successful RouterVM startup.
- Validated nftables and dnsmasq configurations.
- AgentVM DHCP addressing and default route.
- Successful gateway and external IPv4 connectivity.
- HTTP/2 200 from a selected HTTPS endpoint.
- WAN-side observations consistent with RouterVM source NAT.
- Successful connectivity after a controlled RouterVM and AgentVM restart.

The original Mint VM and its configuration were retained.

This validation covers the intended temporary fallback path. It does not establish that every Fedora VM routes through RouterVM.

### AgentVM

AgentVM is a separate Fedora guest used for coding-agent tools and development experiments.

The documented fallback configuration places it on `agent-net`, with the Debian RouterVM providing its gateway and DNS/DHCP services.

Selected gateway, internet and HTTPS checks passed after the fallback migration.

Broader management access, guest security controls and isolation requirements are tracked independently from these connectivity checks.

### Kali PentestVM

PentestVM is a Kali Linux guest used for authorized security testing and coursework.

The recorded Fedora environment includes a direct `travel-nat` connection and Docker-based vulnerable-lab services.

An nftables forwarding guard was configured to restrict forwarding involving the vulnerable-lab interface.

The recorded rule was installed in an `inet vuln_lab_guard` table at forward-hook priority `-100`, with drops matching traffic entering or leaving the guarded interface.

The associated `vuln-lab-guard.service` was observed enabled and active, with the forwarding rule loaded.

LUKS2 guest disk encryption was also reported as verified.

A separate vulnerable-lab libvirt network was created later and assigned host firewall restrictions. This network must not be confused with the earlier two-network RouterVM fallback inventory.

**Verification boundary:** A loaded forwarding rule demonstrates configuration state, not complete isolation. Container networking, direct host access, other interfaces and prohibited cross-network paths require separate tests.

### PrivateVM

PrivateVM is a Linux guest intended for separate personal browsing and communications.

The recorded storage arrangement includes LUKS2 encryption with LVM-backed guest storage.

Guest UFW inspection showed:

- Incoming connections denied by default.
- Outgoing connections allowed by default.
- Routed traffic disabled.

A separate Fedora host firewalld policy, `privatevm-inbound-deny`, was created to restrict inbound traffic toward PrivateVM.

These are distinct host and guest enforcement layers.

Clipboard functionality was observed during setup, but working clipboard integration is a usability observation rather than evidence of strong guest isolation.

**Verification boundary:** The available records support the configured encryption and firewall controls. They do not establish complete cross-VM network isolation or persistence of every rule after a later host or guest reboot.

### Windows MalwareVM

MalwareVM is a Windows 11 Pro guest built for authorized malware-analysis coursework and demonstrations.

The recorded implementation includes:

- Windows 11 Pro build 26300 (26300.9457).
- UEFI/OVMF with Secure Boot enabled and a virtual TPM.
- BitLocker protection on the Windows system volume.
- FLARE-VM analysis tooling.
- Windows image preparation using a separate offline servicing VM.
- SPICE guest integration during preparation.
- Removal of the guest network adapter after setup.
- Disabled shared clipboard at the recorded isolation checkpoint.

BitLocker inspection reported the C: volume as `FullyEncrypted`, with `Protection On` and XTS-AES128.

Chocolatey version 2.7.5 was observed during tooling preparation.

A HardeningKitty audit was performed, but the existence of that audit does not establish that every recommended hardening change was applied.

Windows Defender and related security settings were inspected or adjusted during preparation; the available documentation does not establish a fully validated final security baseline.

The removal of the NIC and disabling of shared clipboard reduce selected interaction paths. They do not establish comprehensive isolation against all host/guest escape mechanisms or other virtual-machine integration channels.

MalwareVM is documented as offline at the recorded checkpoint, not as a production-secure endpoint or a machine safe for unrestricted execution of unknown malware.

## 4. Security architecture

The portable homelab combines several security-control layers.

| Layer | Implemented or observed control | Purpose |
| --- | --- | --- |
| Host storage | Fedora LUKS2 | Protect host data at rest |
| Guest storage | LUKS2 or BitLocker where documented | Add guest-specific encryption boundaries |
| Virtual networking | Separate libvirt networks and attachments | Organize workload connectivity |
| Router firewall | Debian RouterVM nftables | Control the AgentVM fallback route |
| Host firewall | Fedora firewalld policies | Apply host-side traffic restrictions |
| Guest firewall | PentestVM nftables and PrivateVM UFW | Enforce selected guest-level traffic policies |
| MalwareVM interfaces | NIC removal and clipboard restrictions | Reduce selected external interaction paths |

These layers address different threats.

Storage encryption does not guarantee runtime isolation. Separate virtual networks do not by themselves prove that unintended routes are blocked. Active firewall services do not establish that all policy expectations have been tested.

Each boundary requires its own positive and negative verification.

## 5. Testing and verification

### Documented validation matrix

| Component | Test or observation | Recorded result | Limitation |
| --- | --- | --- | --- |
| Fedora host | LUKS2 inspection | Encryption confirmed | Does not validate every physical attack scenario |
| RouterVM fallback | Configuration and service checks | nftables and dnsmasq checks passed | Limited to the inspected configuration |
| RouterVM and AgentVM | Controlled VM restart | Selected connectivity restored | Not full host-reboot validation |
| AgentVM | Gateway, external IPv4 and HTTPS | Passed at the migration checkpoint | Limited to selected destinations |
| PentestVM | Forwarding guard inspection | Rule and loader service observed active | No complete negative-path matrix |
| PentestVM | Guest encryption inspection | LUKS2 reported verified | Current unlock/boot behavior not rechecked here |
| PrivateVM | Guest disk inspection | LUKS2/LVM observed | No independent restore test |
| PrivateVM | Guest UFW inspection | Default inbound deny observed | Does not establish all blocked paths |
| Fedora host | PrivateVM firewalld policy | Inbound-deny policy created | No complete traffic validation |
| MalwareVM | BitLocker inspection | C: fully encrypted; protection on | Point-in-time result |
| MalwareVM | NIC and clipboard configuration | NIC removed; clipboard disabled | Other interaction paths not exhaustively assessed |
| MalwareVM | HardeningKitty | Audit performed | Complete remediation not established |

### Reboot and persistence evidence

Fedora host pre-/post-reboot logs were collected on 10 November 2026.

However, the collected records have not been comprehensively reconciled across every VM, network and security service.

A later presentation-guide summary reports selected MalwareVM-related host-reboot checks, including a changed boot ID, MalwareVM remaining stopped and a provisioning network remaining inactive.

These observations provide bounded persistence evidence. They do not establish that every Fedora VM, libvirt network, firewall service or storage configuration passed a complete reboot test.

### Backup and recovery evidence

The available documentation records backup inventories and reported local MalwareVM copy/checksum checks.

A later guide describes successful checksum comparisons for selected MalwareVM disk, configuration and secure-state files.

These observations have not been independently reconciled against every underlying artifact.

A complete off-device backup, verified restore and boot-tested recovery are not established. Backup status for other Fedora VMs must be evaluated separately.

A backup inventory or matching hash alone is not proof that an entire virtual machine can be restored successfully.

## 6. Results and limitations

### Verified or documented outcomes

The available November 2026 evidence supports:

- An independent Fedora KVM/libvirt homelab alongside the Mint primary environment.
- Host LUKS2 encryption.
- Functional Debian RouterVM fallback connectivity for AgentVM.
- Selected guest disk encryption controls.
- Loaded PentestVM forwarding restrictions.
- Configured PrivateVM guest and host firewall controls.
- Windows MalwareVM preparation with BitLocker and analysis tooling.
- MalwareVM network-adapter removal and clipboard restrictions.
- Selected VM restart, service and security-state observations.

These results demonstrate implemented infrastructure and measured checkpoints, not complete security assurance.

### Outstanding verification

The project does not yet establish:

- Comprehensive isolation between all Fedora workloads.
- Full negative-path validation for PentestVM's vulnerable network.
- Complete persistence of guest and host firewall policies after relevant reboots.
- Comprehensive validation of MalwareVM hardening.
- Resistance to guest escape or host compromise.
- Independently verified off-device backups and successful restoration.
- Complete reconciliation of the November 10 host-reboot evidence.
- Current operational status following subsequent configuration changes.

The latest documented state may differ from the state of a running host. New technical claims should be based on fresh, dated evidence from the appropriate machine.

## 7. Lessons learned

**A portable copy is a separate deployment.** Virtual-machine definitions, machine types, networks, storage permissions and firewall behavior must be checked on the destination host rather than inherited as assumptions.

**Encryption has multiple boundaries.** Host disk encryption and guest disk encryption protect different data and operational states.

**Isolation requires evidence.** A configured nftables or firewalld rule is a starting point; controlled prohibited-path tests are needed to evaluate enforcement.

**Security tooling creates operational trade-offs.** Clipboard integration, temporary network access and installation services may be useful during VM preparation, but their final exposure must be reviewed.

**Recovery is part of security engineering.** A successful checksum comparison is valuable, but restoration needs separate validation.

**Different environments require distinct evidence.** Mint RouterVM results cannot validate Fedora's fallback, and Fedora's individual guests should not be treated as one uniformly secured system.

## 8. Evidence and references

This public case study summarizes technical work recorded in private homelab documentation and associated project conversations.

The underlying material includes:

- Fedora architecture and VM inventories.
- Debian RouterVM fallback migration observations.
- Host and guest security-control records.
- MalwareVM preparation notes.
- Reboot and backup evidence summaries.

Private logs, screenshots, disk images, recovery information and internal VM identifiers are not automatically approved for publication.

Related public documentation:

- [Original Debian RouterVM case study](../router-vm/README.md)
- [Alpine RouterVM v2 design](routervm-v2.md)
- [Firewall verification methodology](../firewall-verification/README.md)

## 9. Next steps

The next technical validation priorities are:

1. Reconcile the saved Fedora host-reboot evidence against the expected persistence matrix.
2. Verify permitted and prohibited traffic paths for the vulnerable-lab and PrivateVM networks.
3. Record guest firewall persistence at appropriate restart checkpoints.
4. Reconcile MalwareVM hardening decisions with the actual applied configuration.
5. Verify independent backup copies and perform a controlled restore test.
6. Refresh the VM and network inventory after significant configuration changes.

These items remain outstanding and are not presented as completed achievements.

## Authorization and publication

The environment is used for personal cybersecurity experimentation and authorized educational activities.

This repository intentionally excludes credentials, BitLocker and LUKS recovery information, private network inventories, sensitive guest identifiers, malware specimens and unreviewed operational logs.

The case study describes the documented configuration and validation checkpoints without claiming production-grade security or a comprehensive penetration-test result.
