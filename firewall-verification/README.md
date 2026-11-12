# RouterVM Firewall Policy Verification

**Project type:** Educational networking and security engineering  
**Environment:** Linux Mint primary homelab, Debian RouterVM, KVM/QEMU, libvirt  
**Technologies:** Python 3, nftables, dnsmasq, TCP/IP, DNS, DHCP, NAT  
**Verification date:** 19 October 2026  
**Status:** Completed verification of selected IPv4 policies, with documented limitations

## 1. Objective and problem

This project evaluates whether a virtualized Debian RouterVM enforces the network forwarding policies required by a school networking assignment and an additional personal homelab isolation requirement.

The original assignment requires communication between LAN1 and LAN2, while allowing both networks to access external services. A third network, LAN3, was added for AgentVM and configured to prevent new connections between that network and the two coursework LANs.

The objective was to verify the intended behavior using positive and negative tests rather than relying only on firewall configuration inspection or unsuccessful connections.

I also developed a Python checker to make the client-side tests repeatable and preserve structured evidence.

## 2. Technical environment

The project runs on the primary Linux Mint KVM/libvirt homelab.

| Component | Purpose |
| --- | --- |
| Debian RouterVM | IPv4 routing, nftables firewall, NAT and dnsmasq services |
| Client1 — LAN1 | Coursework network client |
| Client2 — LAN2 | Coursework network client |
| AgentVM — LAN3 | Additional isolated development network |
| Python checker | Client-side connectivity and application-level verification |

The WAN connects through libvirt NAT. The three internal networks use separate virtual interfaces and subnets.

This environment is distinct from the later Alpine RouterVM v2 implementation and the Fedora laptop's temporary Debian routing fallback.

[Historical network topology](../diagrams/router-vm-topology.md)

### Expected forwarding policy

| Traffic path | Expected behavior |
| --- | --- |
| LAN1 → LAN2 | Allow |
| LAN2 → LAN1 | Allow |
| LAN1/LAN2/LAN3 → WAN | Allow |
| LAN3 → LAN1/LAN2 | Block new connections |
| LAN1/LAN2 → LAN3 | Block new connections |
| Other unmatched forwarding | Drop |

Stateful established/related traffic is handled before the segment-specific restrictions. The policy table therefore does not imply that pre-existing connections are necessarily terminated.

The complete test expectations are recorded in the [test matrix](test-matrix.md).

## 3. Implementation

### Firewall and network services

The Debian RouterVM uses:

- **nftables** for packet filtering, forwarding policy and source NAT.
- **dnsmasq** for DHCP and DNS services on the internal networks.
- **IPv4 forwarding** for permitted traffic between networks and toward WAN.
- **Connection tracking** to support permitted return traffic.

The firewall separates allowed traffic from prohibited new connections. LAN1 ↔ LAN2 communication is intentionally permitted to satisfy the original assignment.

LAN3 isolation is an additional security boundary introduced for the personal homelab.

### Python verification checker

I developed [check_firewall.py](check_firewall.py) to run a controlled set of checks from the designated virtual machines.

The checker:

1. Confirms the expected source IPv4 address and default gateway before probing.
2. Tests local TCP/22 connectivity as a positive control.
3. Tests permitted and prohibited TCP/22 connections between lab clients.
4. Queries the router's DNS service over UDP and TCP.
5. Performs an IPv4 HTTPS HEAD request with proxies bypassed.
6. Produces a structured JSON report containing observations, classifications and supporting output.

The script uses explicit source addresses and a fixed set of known lab peers. It does not perform general port scanning, authenticate to SSH, modify firewall rules or restart services.

### Result classification

The checker uses three result statuses:

| Status | Meaning |
| --- | --- |
| `PASS` | An expected allowed behavior was observed |
| `FAIL` | A required check failed or a prohibited TCP connection succeeded |
| `NEEDS_ROUTER_EVIDENCE` | A prohibited connection was unsuccessful, but its cause has not been established |

A timeout alone cannot prove that RouterVM blocked the traffic. A host firewall, missing listener, routing problem or other condition might explain the same observation.

For that reason, prohibited-path timeouts require supporting router-side evidence before drawing conclusions about policy enforcement.

## 4. Testing and verification

### Initial manual verification

Manual testing on 19 October 2026 covered:

- Bidirectional LAN1/LAN2 TCP/22 connectivity.
- Four prohibited TCP/22 paths between LAN3 and the coursework LANs.
- DNS resolution over UDP and TCP.
- Direct IPv4 HTTPS sessions.
- Router-side NAT observations.
- DHCP lease and service-status evidence.

The observed LAN1/LAN2 accept counters increased during successful connectivity tests.

The LAN3 isolation counters also increased during prohibited connection attempts, corroborating blocking at the router rather than relying solely on timeouts.

[Manual verification evidence](evidence-2026-10-19.md)

### Automated checker validation

The checker was subsequently run on all three designated virtual machines.

| Node | PASS | NEEDS_ROUTER_EVIDENCE | FAIL |
| --- | ---: | ---: | ---: |
| Client1 | 5 | 1 | 0 |
| Client2 | 5 | 1 | 0 |
| AgentVM | 4 | 2 | 0 |
| **Total** | **14** | **4** | **0** |

All three machines passed their source-address and default-gateway preflight checks.

The four prohibited TCP connections timed out. Their original reports retained `NEEDS_ROUTER_EVIDENCE` rather than being rewritten as automated passes.

During this run, both grouped LAN3 isolation counters increased by six packets and 360 bytes. These counters corroborate drops during the probe interval but do not independently identify every source/destination pair.

[Live checker validation](live-checker-validation-2026-10-19.md)

### Logging improvement and retest

After the initial validation, separate rate-limited logging rules were added before the existing unconditional LAN3 drop rules.

The revised configuration was loaded and the checker was run again.

The subsequent kernel journal recorded all four prohibited TCP/22 paths, with source/destination addresses, interfaces and matching drop-counter observations.

This provided stronger path-specific evidence than the initial grouped counters alone.

The logging rules use separate rate limits of five events per second with a burst allowance of five. The following drop rules remain unconditional.

The rate-limit configuration was observed loaded, but sustained high-volume logging behavior was not tested.

[Logging change and retest](logging-validation-2026-10-19.md)

### Checker unit tests

The Python test suite covers:

- Timeout and socket-error classification.
- Unexpectedly successful prohibited connections.
- A real loopback TCP positive control.
- DNS response classification.
- Prevention of probes when machine preflight fails.
- Output-file error handling without overwriting existing reports.
- Separation of automated results from router evidence requirements.

Seven tests passed for the version used in the recorded live runs.

A subsequent correction to output-file error handling introduced an additional regression test, bringing the locally recorded result to **eight passing tests**.

The archived live reports retain the original checker hash. The correction did not change the network probe logic.

To run the local tests:

```bash id="g8yrlk"
cd firewall-verification
python3 -B -m unittest discover -s tests -v
```

## 5. Reproducing client-side checks

The checker requires Linux, Python 3, `ip`, `dig` and `curl`.

Run it directly on an appropriately configured, authorized lab VM using the node identifier matching that machine.

For Client1:

```bash id="kzl4eo"
python3 -B check_firewall.py \
  --node client1 \
  --output client1-results.json
```

For Client2:

```bash id="5bs4dp"
python3 -B check_firewall.py \
  --node client2 \
  --output client2-results.json
```

For AgentVM:

```bash id="hexlzf"
python3 -B check_firewall.py \
  --node agent-vm \
  --output agent-results.json
```

The checker refuses to overwrite an existing output file. Use a new filename for each run.

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | All automated checks passed |
| `1` | At least one check failed |
| `2` | A setup problem occurred or manual router evidence remains necessary |

Invalid command-line arguments also produce exit code 2.

Expected isolation timeouts commonly produce exit code 2. This is not automatically a failed firewall policy.

### Router-side corroboration

Record the relevant RouterVM forwarding counters before and after the selected probes:

```bash id="n8w9t8"
sudo nft -a list chain inet filter forward
```

Do not reset counters or reload the firewall between snapshots.

Compare the matching rules and their packet/byte counter changes. Grouped counters may include retransmissions or unrelated traffic, so a precise conclusion may require individual probes or targeted packet-capture evidence.

The checker does not independently verify NAT translations, DHCP lease exchanges, service persistence or every firewall drop.

## 6. Results and limitations

### Verified outcomes

The recorded work demonstrates:

- Permitted new TCP/22 communication between LAN1 and LAN2.
- Router-corroborated blocking of four tested new TCP/22 connections involving LAN3.
- Working UDP/TCP DNS responses from the expected router gateways.
- Successful direct IPv4 HTTPS requests from all three clients.
- Observed source NAT translation at RouterVM through matching packet pairs.
- DHCP service evidence from lease records and server journal entries.
- Path-specific LAN3 denial logging in the subsequent retest.
- Eight passing local checker tests after the output-file correction.

These results apply to the documented October 2026 configuration and tests.

### Limitations

The project does not establish:

- Comprehensive firewall correctness across all ports or protocols.
- IPv6 isolation or forwarding behavior.
- Protection against spoofing or VM/container breakout.
- Isolation of established sessions after firewall policy changes.
- Complete validation of RouterVM INPUT policy and WAN-side SSH restrictions.
- Exhaustive firewall logging or rate-limit behavior.
- Service persistence after a new host reboot during this verification session.
- Independent reproduction of the original terminal observations.

AgentVM also had a separate host firewall restriction affecting SSH from RouterVM. This control was preserved rather than relaxed to produce a successful connection. RouterVM counter and journal evidence were therefore important when attributing the prohibited-path observations.

The source material consists of recorded user-run terminal output, JSON reports and reviewed firewall observations. It is not an independent third-party security audit.

## 7. Lessons learned

**A failed connection is not automatically evidence of firewall enforcement.** Negative tests require positive controls and evidence from the system expected to block the traffic.

**Requirements matter when evaluating a policy.** The original assignment required LAN1/LAN2 communication. Treating their permitted forwarding as a defect would have been an incorrect interpretation of the requirements.

**Automated tests and router observations serve different purposes.** The Python checker provides repeatable client-side observations, while counters, logs and packet captures support conclusions about forwarding and translation.

**Changes require separate verification.** Adding denial logging was followed by another controlled test rather than being treated as automatically successful.

**Evidence needs explicit boundaries.** Packet counters, service status, successful HTTPS responses and passing unit tests each support different conclusions.

## 8. Supporting evidence

| Resource | Contents |
| --- | --- |
| [Test matrix](test-matrix.md) | Expected policy and individual test coverage |
| [Python checker](check_firewall.py) | Repeatable IPv4 client-side verification |
| [Checker unit tests](tests/test_checker.py) | Test classification and error handling |
| [Manual evidence](evidence-2026-10-19.md) | Connectivity, NAT, DNS, DHCP and services |
| [Live checker results](live-checker-validation-2026-10-19.md) | Three-machine automated validation |
| [Logging retest](logging-validation-2026-10-19.md) | Path-specific denied-traffic observations |
| [Historical RouterVM topology](../diagrams/router-vm-topology.md) | Network architecture and policy context |

## 9. Remaining work

Further verification could cover:

- RouterVM INPUT and WAN-side SSH policy.
- Additional TCP/UDP protocols and IPv6 behavior.
- Stateful connections across policy changes.
- Logging under sustained traffic.
- Persistence after relevant guest and host restarts.

These are future validation opportunities, not completed results.

---

**Scope:** Authorized educational and personal homelab testing. Historical evidence is retained with its original dates and limitations. Sensitive operational details should be reviewed before any additional public release.
