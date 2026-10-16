# Security findings and verification matrix

These entries summarize **earlier reviewed assessments** of the Linux Mint 22.3 host. Exact command transcripts and dated scan files have not been committed here; evidence is therefore summarized, not represented as raw artifacts.

| Finding | Assessment | Remediation / response | Verification | Status |
| --- | --- | --- | --- | --- |
| Lynis 70/100 baseline | Configuration hardening opportunities | Multiple targeted changes | Follow-up scan reached 75/100 | Improved, not fully resolved |
| 14 installed kernel packages | Maintenance overhead | Remove unnecessary old images while retaining rollback options | Three remaining | Verified in earlier session |
| auditd lacked monitoring rules | Important changes less observable | Add persistent identity, sudoers and sshd-related rules | Seven loaded, test audit event generated | Verified |
| APT caching on TCP 3142 (all interfaces) | Unneeded reachable service | Disable APT caching | TCP 3142 no longer listening | Verified |
| Docker group access | Privileged daemon access | Remove user from Docker group | Permission denied without sudo | Verified |
| No file integrity baseline | No reference for detecting changes | Initialize AIDE, exclude large changing VM images | 9,365 entries, clean check, exit 0 | Verified |
| Journal integrity | Integrity review useful | Run journal verification | Exit code 0 | Verified |
| Chkrootkit BPFDoor-related alert | Potential false positive | Inspect Helium AppImage broker and local IPC | No evidence of BPFDoor established | Likely false positive; not exhaustive |
| Version-based LinPEAS kernel CVE flag | Could be inaccurate on patched distro kernel | Do not treat as confirmed without vendor advisory/backport check | Not fully established | Unconfirmed |
| Virtualization TAP warning | Expected virtualization context | Preserve KVM/libvirt operations | Warning persisted as expected | Accepted |
| Full-disk/swap encryption | Physical threat model issue | Deferred / review separately | No completion evidence | Open |

## Interpretation
The hardening index and the number of warnings are **not vulnerability counts**. LinPEAS observations are enumeration leads, not automatic exploit proofs. Controls must be justified according to risk and operational dependency.

## Follow-up evidence to capture
- [ ] Redacted Lynis baseline and follow-up summary outputs
- [ ] Current `auditctl -l` with rule count and sample non-sensitive event
- [ ] Current service binding check for port 3142
- [ ] Current user group listing and Docker permission behavior
- [ ] AIDE check result with monitored entry count (without sensitive paths)
- [ ] Summary of outstanding Lynis suggestions and their disposition


## Follow-up Lynis report — 2026-10-16

A fresh Lynis 3.0.9 audit on the Linux Mint workstation reported **hardening index 75/100**, **283 tests**, and **2 enabled plugins**. The user shared the filtered report output; it included **33 suggestion entries and no `warning[]` entries in that extraction**. This is not equivalent to asserting all tools found zero vulnerabilities.

### Priority triage (provisional)

| Priority | Lynis ID | Follow-up |
| --- | --- | --- |
| High investigation | `KRNL-6000` | Determine exact sysctl mismatches before deciding on any change |
| High investigation | `BOOT-5264` | Inspect important systemd units with `systemd-analyze security`; assess actual exposed service context |
| Medium | `AUTH-9328`, `AUTH-9230` | Inspect umask and password hashing rounds; avoid disruptive changes without understanding login stack |
| Medium | `FILE-7524` | Identify specific reported file permissions before adjusting |
| Medium | `FINT-4402` | Check current AIDE digest settings and integrity baseline strategy |
| Medium / maintenance | `PKGS-7370` | Consider periodic package integrity and consistency checks |
| Low / contextual | `NETW-3200` | Review DCCP, SCTP, RDS and TIPC module necessity |
| Low / future installation | `FILE-6310` | Separate /home, /tmp, /var partitions only if the operational costs justify it |
| Low | `BANN-7126`, `BANN-7130` | Optional login notices |
| Future homelab project | `LOGG-2154` | Remote centralized logging, after design and resource review |

Additional suggestions include GRUB bootloader password (`BOOT-5122`), password expiration policies, USB module policy, process accounting, compiler restrictions, and service hardening. These require a **threat-model and usability review**, especially given virtualization, Tailscale school lab access, and regular desktop use.

The report also includes a **Lynis-version age notice**. Check distribution package availability and upstream releases; the notice alone does not indicate a host vulnerability.

### Documentation limitation

Only the filtered report screenshot was reviewed for this update, not the complete raw Lynis log or exact findings for every test. All priorities are **provisional review priorities rather than confirmed vulnerabilities**, and no new remediations are claimed.

## IPv4 source-routing hardening — 2026-10-16

The host originally reported `net.ipv4.conf.default.accept_source_route=1`, and listed existing interfaces (including the physical NIC, virtual bridges, Docker and Tailscale) reported `accept_source_route=1`. The `all` setting was already `0`.

A persistent file, `/etc/sysctl.d/90-disable-source-routing.conf`, was created with:

```ini
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
```

The setting was also applied immediately to the currently present `/proc/sys/net/ipv4/conf/*/accept_source_route` entries. The user-provided verification screenshot showed **0 for every listed interface**, including `all`, `default`, `enp6s0`, `tailscale0`, `docker0` and the active virtual bridges.

**Status:** Active settings verified. Persistence after reboot and VM/Tailscale connectivity regression checks remain pending. This change was made on the Mint host; it does not establish the RouterVM guest's own sysctl configuration.

## BPF JIT hardening — 2026-10-16

The host initially reported `net.core.bpf_jit_enable=1` and `net.core.bpf_jit_harden=0`. The owner applied `sudo sysctl -w net.core.bpf_jit_harden=2` and created `/etc/sysctl.d/90-bpf-hardening.conf` containing `net.core.bpf_jit_harden = 2`.

A subsequent read of both sysctl values showed **`net.core.bpf_jit_enable=1` and `net.core.bpf_jit_harden=2`**. This enables JIT hardening for privileged and unprivileged BPF programs without disabling JIT compilation.

**Verification:** live values and persistent file creation confirmed by user-provided terminal screenshot. **Pending:** reboot persistence, representative Tailscale/libvirt connectivity checks, and post-change Lynis assessment. No hardening index increase is claimed yet.

## Post-change operational checks — 2026-10-16

The host owner verified that `libvirtd` was active and the following live values remained in effect:

- `net.core.bpf_jit_harden=2`
- `net.ipv4.conf.all.accept_source_route=0`
- `net.ipv4.conf.default.accept_source_route=0`
- `net.ipv4.ip_forward=1`

All listed VMs were shut off at test time; VM startup and guest networking were **not yet regression tested**. Tailscale returned device status but reported that configured DNS servers were unreachable; the cause and any connection to the hardening changes remain **unconfirmed**. No tailnet device names or addresses are reproduced here.

**Pending:** troubleshoot Tailscale DNS, start a representative VM and check outbound connectivity, then verify reboot persistence and rerun Lynis.

## VM network regression check — 2026-10-16

After the source-routing and BPF JIT changes, `virsh list` showed **RouterVM** and **AgentVM** running. From AgentVM, three ICMP requests to its RouterVM gateway (`10.1.30.254`) and three to an external IPv4 test endpoint (`1.1.1.1`) all received replies (0% loss in each test). This supports that VM startup, guest routing, and outbound connectivity remained functional in the tested configuration.

This check does not cover every guest, DNS inside the guest, all virtual network policies, or persistence after a host reboot. No school tailnet device listing is included.

## Post-hardening Lynis reassessment — 2026-10-16

After disabling IPv4 source routing and enabling BPF JIT hardening, a new Lynis report showed **hardening_index=76**, up from the preceding **75** (and an initial recorded baseline of **70**). The user-provided filtered report screenshot displayed suggestions but no `warning[]` entries. The `KRNL-6000` profile mismatch suggestion persists; it does not establish that the two remediations failed because other sysctl values differ from Lynis expectations.

The two changes were verified as active, and a subsequent check confirmed RouterVM/AgentVM startup and guest gateway/external IPv4 connectivity. **Persistence following a host reboot remains untested.** This score is a configuration-hardening index, not a security guarantee; all unresolved suggestions require context-aware decisions.

## Reboot persistence check — 2026-10-16

After rebooting the Linux Mint host, the following were confirmed from terminal output:

- `net.core.bpf_jit_harden=2`: persisted.
- `net.ipv4.conf.all.accept_source_route=0` and `net.ipv4.conf.default.accept_source_route=0`: persisted.
- `net.ipv4.ip_forward=1`: unchanged.
- `libvirtd` was active and all seven VM definitions remained registered; all VMs were stopped at inspection time.
- Tailscale reported the local device connected; no full post-reboot school application access test was provided.
- Source-routing acceptance was `0` on the physical NIC, Tailscale, virtual bridges, Docker and global/default settings. **Exception:** loopback (`lo`) was `1` after reboot, unlike the immediate post-change verification. This remains to be understood; it is not a claim of externally exposed source routing.

The final recheck after boot does not by itself prove guest network connectivity; pre-reboot RouterVM/AgentVM regression tests passed. No sensitive tailnet device list is reproduced.

## Portfolio evidence review — 2026-10-16

The owner supplied screenshots of the post-reboot sysctl query and `sudo auditctl -l`, and a text export of Lynis query output.

- The sysctl screenshot again showed `net.core.bpf_jit_harden=2`, `net.ipv4.conf.all.accept_source_route=0`, `net.ipv4.conf.default.accept_source_route=0`, and `net.ipv4.ip_forward=1`.
- `auditctl -l` showed **seven loaded watch rules**: `/etc/passwd`, `/etc/group`, `/etc/shadow`, `/etc/gshadow`, `/etc/sudoers`, `/etc/sudoers.d`, and `/etc/ssh/sshd_config` (write/attribute permission monitoring). This validates rule loading in the current post-reboot session; it is not a new audit-event test.
- A Lynis report query showed `lynis_version=3.0.9` and `hardening_index=76`.
- `lynis show details KRNL-6000` returned *historical* log lines timestamped earlier on October 16, **before** the kernel remediations; values such as `bpf_jit_harden=0` in that output must **not** be presented as current state.

The source screenshots and full Lynis transcript remain outside the repository pending sanitation/publication review.
