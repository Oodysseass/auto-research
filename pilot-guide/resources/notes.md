# Notes: model and statements

## Model

Parties and corruption.
- There are n parties. The adversary corrupts a fixed set of at most t parties before the execution starts (static corruption).
- At least two parties are honest: n - t >= 2. The adversary may corrupt at least one party: t >= 1.

Time.
- The execution proceeds in rounds r = 1, 2, 3, and so on. Every party knows the current round.
- Before round 1 (round 0), every party holds the genesis chain G.

Chains.
- A chain is a sequence of blocks that starts with G. Its length len(C) is the number of blocks after G, so len(G) = 0.
- Only valid chains exist: the adversary cannot forge blocks, and every chain an honest party receives is valid.

Honest party P in round r, in this order:
1. Receive every chain delivered to P in round r.
2. Adopt the longest chain among its current chain and the received chains. On a tie, keep the current chain.
3. Make one mining attempt. On success, extend the current chain by one block.
4. If the current chain changed during round r, broadcast it.

Mining.
- Each honest party makes one mining attempt per round. Each corrupted party makes one mining attempt per round, on any chain the adversary chooses.
- Whether an attempt succeeds is part of the execution. Every pattern of successes is a possible execution.
- Round r is successful if at least one honest mining attempt succeeds in round r.

Network.
- A chain an honest party broadcasts in round r is delivered to every honest party in round r + 1.
- The adversary cannot drop or delay these deliveries.
- In any round, the adversary may deliver any chain it knows to any subset of the honest parties, and to none of the others.
- The adversary is rushing: in round r it sees the honest broadcasts of round r before it chooses its own deliveries for round r + 1.

Notation.
- C_P^r is the chain of honest party P at the end of round r. C_P^0 = G.
- m_r is the minimum of len(C_P^r) over all honest P. M_r is the maximum. So m_0 = M_0 = 0.

## Statements

Lemma 1 (Chain growth). Main result. For every execution and every round r >= 1: if round r is successful, then m_{r+1} >= m_{r-1} + 1.

Lemma 2 (Bounded honest spread). Auxiliary. For every execution and every round r >= 0: M_r - m_r <= 1.

Neither lemma is used in the proof of the other.
