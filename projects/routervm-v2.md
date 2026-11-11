# RouterVM v2 — segregated Alpine router design

**Primary host:** Linux Mint KVM/QEMU. **Recorded checkpoint:** November 2026. **Status:** Architecture and bounded validation; a full production cutover is not claimed.

## Objective

Develop a lightweight Alpine Linux router with purpose-separated virtual networks for test WAN, study, development, private use, malware analysis, work and management. The design is distinct from the original Debian classroom RouterVM and from its narrower Fedora laptop fallback copy.

## Engineering decisions

- Alpine Linux 3.24 guest with UEFI boot and small allocated CPU/memory footprint.
- Dedicated management interface and host-only management bridge.
- nftables default-drop controls on the management side with SSH restricted to that path.
- Separate validation VM for controlled startup, kernel compatibility and guard checks.
- Retention of legacy Mint VMs during migration and validation.

## Observed evidence

The management interface was observed UP after reboot with the intended static address. nftables and SSH were checked as started at the recorded checkpoint. Separate controlled validation work exercised startup guards and an updated Linux LTS kernel.

These observations **do not** prove that every planned network has been deployed or that every permitted and denied inter-segment flow has passed its test matrix.

## Remaining work

Document a complete allowed/denied traffic matrix, run independent positive and negative probes, correlate firewall counters with packets, verify persistence after the relevant restarts and take verified backups. Legacy Debian RouterVM findings remain historically valid for their own tested configuration only.

Related: [Portable Fedora environment](portable-homelab.md), [original Debian RouterVM](../router-vm/README.md).
