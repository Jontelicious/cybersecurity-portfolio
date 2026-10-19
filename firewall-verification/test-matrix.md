# Expected policy and evidence matrix

Policy source: supplied school Router-VM assignment and user clarification;
LAN3 is an additional homelab boundary. All tests below are IPv4.

| ID | Source | Destination | Probe | Expected | Current evidence |
|---|---|---|---|---|---|
| P01 | client1 | client2 | TCP/22 | Allow | Connected, LAN1→LAN2 accept counter +1 |
| P02 | client2 | client1 | TCP/22 | Allow | Connected, LAN2→LAN1 accept counter +1 |
| P03 | client1 | agent-vm | TCP/22 | Block new connection | Timeout; grouped lab→LAN3 counter +6 over P03/P04 |
| P04 | client2 | agent-vm | TCP/22 | Block new connection | Timeout; same grouped counter |
| P05 | agent-vm | client1 | TCP/22 | Block new connection | Timeout; grouped LAN3→lab counter +6 over P05/P06 |
| P06 | agent-vm | client2 | TCP/22 | Block new connection | Timeout; same grouped counter |
| D01–D03 | Each VM | Its router gateway | UDP/53 A query | Allow/resolve | NOERROR with A answers |
| D04–D06 | Each VM | Its router gateway | TCP/53 A query | Allow/resolve | NOERROR with A answers |
| W01–W03 | Each VM | example.com | IPv4 HTTPS HEAD | Allow, receive return traffic | HTTP/2 200 |
| N01–N03 | Each VM | 104.20.23.154:443 via WAN | Paired SYN capture | Source NAT to router WAN | Three pairs observed |
| H01 | client1 | RouterVM DHCP | DHCP exchange | Reserved .10 | Full DISCOVER/OFFER/REQUEST/ACK |
| H02 | client2 | RouterVM DHCP | DHCP exchange | Reserved .10 | Full DISCOVER/OFFER/REQUEST/ACK |
| H03 | agent-vm | RouterVM DHCP | DHCP exchange | Reserved .10 | REQUEST/ACK; initial discovery not in supplied journal |
| S01 | RouterVM | nftables/dnsmasq services | systemctl | Enabled and active | Both enabled/active |
| I01 | LAN clients | RouterVM LAN address | New TCP/22 | Block by current INPUT policy | Not tested here |
| I02 | WAN subnet | RouterVM WAN address | New TCP/22 | Allow by current INPUT policy | Not tested here |
| L01 | Denied probe | Relevant logging destination | Journal/log observation | Document drop logging coverage | LAN3: all four TCP/22 paths logged with matching drop counters in the 09:05 CEST retest; other denial paths untested |

The checker covers local SSH controls, P01–P06, D01–D06 and W01–W03 from the
appropriate node. Blocked-path reports require manual router evidence. Other rows
remain separately observed or pending, not automatic checker passes.
