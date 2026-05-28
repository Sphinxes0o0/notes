# TCP SACK and DSACK Implementation

## SACK Overview
SACK (Selective Acknowledgment) allows receivers to explicitly acknowledge **out-of-order** segments. DSACK reports duplicate data reception.

## Scoreboard Tags
In `tcp_sock`, segments are tagged:
- **S** (TCPCB_SACKED_ACKED): Acknowledged via SACK
- **R** (TCPCB_SACKED_RETRANS): Retransmitted
- **L** (TCPCB_LOST): Marked as lost

## Packet State Matrix
| Tag | InFlight | Description |
|-----|----------|-------------|
| 0 | 1 | Normal segment |
| S | 0 | Original reached receiver |
| L | 0 | Original lost in network |
| R | 2 | Both original and retransmit in flight |
| L\|R | 1 | Original lost, retransmit in flight |

## Key Functions
- `tcp_sacktag_one()`: Tags individual packet's scoreboard
- `tcp_sacktag_skip()`: Finds skb at given sequence
- `tcp_sacktag_walk()`: Traverses skbs within SACK block
- `tcp_mark_lost_retrans()`: Detects lost retransmits in Recovery state

## v18 vs v37 Performance
- **v18**: O(num_sacks × cwnd) — each SACK block traverses from head
- **v37**: Uses `recv_sack_cache` + `highest_sack` pointer → much faster

## DSACK Detection
1. First SACK block start_seq < cumulative ACK → duplicate
2. First SACK block contained within second block → duplicate

## Lost Retransmission Detection
When retransmitting, `snd_nxt` saved in `ack_seq` field. Later if new data SACKed but retransmit's `snd_nxt` wasn't → retransmit is lost.
