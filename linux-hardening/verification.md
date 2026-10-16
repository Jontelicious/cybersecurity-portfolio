# Linux Mint hardening — revalidation checklist

These are **read-only checks** where possible. Their output reflects the *current* state when run, not necessarily the October 2026 assessment. Review output before publishing.

## Identity and privileges
```bash
id
groups
getent group docker
```
Verify the non-root user no longer has access to the rootful Docker socket unless explicitly intended.

## Listening services
```bash
sudo ss -lntup
systemctl is-active apt-cacher-ng 2>/dev/null || true
```
Confirm any port 3142 listener and review other listeners against actual needs (Tailscale, libvirt, Xbox file transfer, etc.).

## Audit subsystem
```bash
sudo auditctl -l
systemctl is-active auditd
```
Ensure rules load after reboot and relevant audit records appear when appropriately tested.

## Integrity monitoring
```bash
sudo aide --check
```
Only run when the baseline is valid and you're ready to interpret results. AIDE may take some time; expected changes or access warnings need review.

## Kernel and network configuration
```bash
uname -r
dpkg -l 'linux-image*' | grep '^ii'
sysctl fs.protected_fifos
sudo ufw status verbose
```

## Lynis follow-up
Use the same compatible Lynis invocation and retain a **private** dated log; compare findings individually, not just the score. Do not publish unredacted logs or let automated recommendations disable required Tailscale, libvirt networking, or intentionally used services.

## Review status
- [ ] Revalidate current system state
- [ ] Confirm no sensitive content in excerpts
- [ ] Add redacted evidence only after review
- [ ] Record exceptions and unresolved items
