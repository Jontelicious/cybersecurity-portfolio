# Portable cybersecurity homelab — separate Fedora deployment

**Documentation checkpoint: 11 November 2026.** This is an evidence-bounded case study of a portable Linux virtualization environment, not a claim that all planned testing is complete.

## Objective

Maintain a permanent Linux Mint/KVM homelab while building an independent Fedora KDE laptop deployment for coursework, analysis and demonstrations. The Fedora system is **not** a replacement for the Mint installation, and the hosts have separate VM definitions, disks, networks, configurations and verification requirements.

## Implemented components

| Area | Work documented | Verification boundary |
| --- | --- | --- |
| Host at-rest protection | Fedora system volume uses LUKS2 | Encryption was checked; no general physical-attack resistance is claimed |
| Virtualization | KVM/QEMU, libvirt and virt-manager | Fedora hosts a separate set of portable virtual machines |
| Routing | Debian RouterVM fallback with NAT/DHCP/DNS for AgentVM | Guest connectivity and controlled VM restart verified on 6 November; not an Alpine RouterVM v2 migration |
| Penetration-testing environment | Kali PentestVM and deliberately vulnerable Docker lab services | A dedicated nftables forwarding guard was observed loaded and active; this is not exhaustive isolation testing |
| Private browsing | Separate Linux PrivateVM with encrypted data volume and incoming-deny firewall policy | LUKS2 and guest UFW inspected; host firewalld policy configured |
| Malware analysis | Windows 11 Pro guest with BitLocker and FLARE-VM tooling | Encryption protection checked; NIC removed and shared clipboard disabled after setup |

## Design rationale

Isolation relies on **multiple independent boundaries**: encrypted host/guest storage, libvirt network attachments, router forwarding policy, host firewalld controls, guest nftables/UFW, and application-level data sharing decisions. In particular, the PentestVM is not assumed to reach the network through the AgentVM's fallback router. The malware-analysis guest is treated as offline after its adapter removal, not as a general-purpose workstation.

A historical Fedora RouterVM migration report recorded exactly two fallback-related networks as of 6 November. A separate vulnerable-lab network was created afterward; those snapshots should not be conflated.

## Evidence and limitations

- The fallback RouterVM and AgentVM successfully exchanged traffic and accessed external endpoints in a controlled test.
- The vulnerable-lab guard service was enabled and its rule-loading result observed; a complete negative-path test matrix remains separate work.
- LUKS2 and BitLocker were inspected in their respective contexts.
- Collected host reboot logs still require a checkpoint-by-checkpoint comparison before marking all persistence tests passed.
- Backup inventory is not equivalent to an independently verified, restorable backup and checksum match.

## Lessons

A copied VM is not a migration success until machine types, interface mappings, DHCP/DNS, routing, firewall behavior and persistence are checked on the **destination host**. A running security service is not proof of comprehensive policy enforcement. Public documentation here intentionally excludes recovery keys, guest identifiers, raw captures, school infrastructure and detailed internal connectivity artifacts.

Related: [RouterVM v2 design](routervm-v2.md), [legacy Debian network lab](../router-vm/README.md).
