---
type: source
source-type: pdf
title: "2024-INFOCOM-PTPsec"
path: papers/2024-INFOCOM-PTPsec.pdf
size: 838 KB
category: paper
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 2024-INFOCOM-PTPsec

> Ingested from `papers/2024-INFOCOM-PTPsec.pdf` via `lit parse` on 2026-06-04.
> Source file: 0.82 MB.

## Page 1

                            PTPsec: Securing the Precision Time Protocol
                            Against Time Delay Attacks Using Cyclic Path
                                         Asymmetry Analysis

Andreas Finkenzeller∗, Oliver Butowski∗, Emanuel Regnath†, Mohammad Hamad∗, and Sebastian Steinhorst∗
                              ∗Technical University of Munich, Germany
                                        †Siemens AG, Germany
                 Email: ∗firstname.lastname@tum.de, †firstname.lastname@siemens.com

               Abstract—High-precision time synchronization is a vital pre-
    requisite for many modern applications and technologies, in-
    cluding Smart Grids, Time-Sensitive Networking (TSN), and
    5G networks. Although the Precision Time Protocol (PTP) can
    accomplish this requirement in trusted environments, it becomes
    unreliable in the presence of specific cyber attacks. Mainly, time
    delay attacks pose the highest threat to the protocol, enabling at-
    tackers to diverge targeted clocks undetected. With the increasing
    danger of cyber attacks, especially against critical infrastructure,
    there is a great demand for effective countermeasures to secure
    both time synchronization and the applications that depend
    on it. However, current solutions are not sufficiently capable
    of mitigating sophisticated delay attacks. For example, they
    lack proper integration into the PTP protocol, scalability, or
    sound evaluation with the required microsecond-level accuracy.
    This work proposes an approach to detect and counteract                     Fig. 1: The path asymmetry analysis concept to detect time delay attacks
    delay attacks against PTP based on cyclic path asymmetry                    within our proposed PTPsec protocol. The PTP Sync message, sent via the
    measurements over redundant paths. For that, we provide a                   attacked path P0 (1), is followed by our newly introduced Meas message
    method to find redundant paths in arbitrary networks and show               over the genuine path P1 to complete the first round trip (2). Similarly, the
    how this redundancy can be exploited to reveal and mitigate                 exchange of the Delay_Req (3) and another Meas message (4) leads to a
    undesirable asymmetries on the synchronization path that cause              second circulation. This allows for cyclic RTT measurements from which we
    the malicious clock divergence. Furthermore, we propose PTPsec,             derive the current path asymmetry αP0 to reveal and mitigate ongoing delay
    a secure PTP protocol and its implementation based on the                   attacks.
    latest IEEE 1588-2019 standard. With PTPsec, we advance the
    conventional PTP to support reliable delay attack detection and             in mind and, hence, makes certain network assumptions, such
    mitigation. We validate our approach on a hardware testbed,
    which includes an attacker capable of performing static and                 as path symmetry and message integrity, that might not always
    incremental delay attacks at a microsecond precision. Our                   hold. Especially in spatially large networks like Smart Grids,
    experimental results show that all attack scenarios can be reliably         for instance, cyber attacks targeting the network infrastructure
    detected and mitigated with minimal detection time.                         are becoming more likely, forcing the protocol designers to
                   Index Terms—Security, IEEE 1588, PTP, Time Delay Attack,     reconsider security concepts in PTP. With the four-pronged
    Time Synchronization
                                                                                approach in Annex P of the latest revision from 2019 [2],
        I. INTRODUCTION                                                         the PTP standard aims to address this problem. While the
                     Precise time synchronization is indispensable for many     suggested cryptographic countermeasures can guarantee mes-
    applications and technologies, such as Smart Grids, Time                    sage integrity and protect against many other attack vectors,
    Sensitive Networking (TSN), and 5G networks. To work                        including message replay and spoofing attacks, they cannot
    correctly, these applications usually require synchronization               counteract all known threats. In particular, time delay attacks
    accuracies on a microsecond or sub-microsecond level, and                   (see § II-B) remain an unsolved problem so far, as previous
    even small deviations can already have significant impacts.                 work has extensively shown [3, 4, 5].
    The consequences range from performance degradation to, in                  Delay attacks exploit and violate the protocol’s assumption
    the worst case, full system failure. For example, delay attacks             of symmetric path delays by maliciously introducing uni-
    in Smart Grids render the control loops unstable, eventually                directional delays into the network. In the literature, initial
    disrupting the entire system [1].                                           solutions to counteract delay attacks against PTP have been
                   The Precision Time Protocol (PTP) (see § II-A) is a com-     proposed recently, none of which provide an effective solution
    monly used network protocol to provide accurate time syn-                   to the problem yet. Threshold-based approaches, for exam-
    chronization in the aforementioned scenarios. Unfortunately,                ple, as presented in [6, 7], perform the attack detection by
    PTP was initially designed without any security considerations              means of continuously monitoring the reported path delay and

## Page 2

comparing it to a previously defined threshold. However, the
threshold definition is quite challenging. Static thresholds must
be set very conservatively to avoid false alarms, while dynamic
thresholds, which adapt based on previous measurements,
cannot adequately protect the system from incremental delay
attacks. Moreover, the reported path delay is not guaranteed
to change at all during a successful delay attack [8]. Other
solutions, including additional network guards [9, 10] or
special monitoring and reporting mechanisms [11, 12] only
work within a limited attacker model. Because the detection
method is not sufficiently coupled to the time synchronization,
attackers can distinguish PTP messages from other network
traffic and handle them differently to bypass the existing               Fig. 2: a) PTP message flow with timestamping to minimize the clock offset
mitigations. Besides, there are first efforts to countermeasures         θ. b) When attackers can delay PTP event messages (Sync or Delay_Req),
based on path redundancy. However, the available works                   they create path asymmetries that impair the clock synchronization.
[8, 13] only present some general ideas that, among other
things, lack scalability and proper protocol integration to              Clocks (OCs) denote master and slave nodes1 which either
become applicable. Hence, there is still a great need for a              provide a time reference to others or synchronize their clocks
secure and comprehensive solution that entirely protects PTP             to a specific master, respectively. In contrast, Transparent
from time delay attacks.                                                 Clocks (TCs) do not actively synchronize to other clocks
             Contributions: This work investigates cyclic Round-Trip     but are transparent switching devices that connect multiple
Time (RTT) measurements to analyze network path asym-                    OCs to form a large network. The synchronization procedure
metries and the applicability for delay attack detection and             comprises two phases. In the protocol’s first phase, all par-
mitigation in time synchronization protocols. The cyclic anal-           ticipating nodes announce their existence and determine the
ysis is enabled by dedicated measurement packets that we                 best (i.e., most accurate) clock in the network, denoted the
introduce in our proposed PTPsec protocol to entangle the                Grandmaster clock, using the Best Master Clock Algorithm
attack detection with the synchronization procedure. Each                (BMCA). In the second phase, all other nodes start actively
PTP event message invokes a subsequent measurement packet                synchronizing their clocks to the Grandmaster by periodi-
that is returned to the originator via a redundant path to               cally exchanging PTP messages. Along with the exchange
complement the cyclic RTT measurement as depicted in Fig. 1.             of Sync and Delay_Req messages, four timestamps are
To finally mitigate ongoing delay attacks, we analyze the path           captured at both the transmission and reception of each packet.
asymmetry based on the two RTT measurements obtained                     Here, the required use of hardware timestamping increases
in one PTP synchronization round and compensate for it                   the synchronization accuracy significantly. The two so-called
accordingly. To the best of our knowledge, PTPsec is the                 event messages are critical for the achieved synchronization
first protocol that efficiently detects and mitigates time delay         accuracy since the obtained timestamps are the basis for
attacks. In particular, we:                                              subsequent offset calculations. With the additional assumption
             • analyze cyclic RTT measurements and show their effec-     of symmetric path delays (dMS = dSM), which is an indis-
        tiveness for reliable path asymmetry identification (§ III),     pensable assumption for PTP, the current clock offset θ can
          • derive a theoretical model for delay attack detection in     be computed as:
arbitrary networks (§ IV),                                                   (t2 − t1) − (t4 − t3)
• present  PTPsec, a secure PTP protocol and its imple-                      θ =        2                                                       (1)
                  mentation as an extension of the latest IEEE 1588-
            2019 standard that adopts our proposed attack mitigation     where t1, t2, t3, and t4 denote the captured timestamps of
method (§ V), and                                                        the two event messages. The diagram in Fig. 2a depicts the
• validate the PTPsec implementation on a realistic hard-                captured timestamps along the entire message flow of one
              ware testbed to confirm that our approach successfully     synchronization round. Note that the Follow_Up message
detects and mitigates time delay attacks (§ VI).                         conveying the captured transmission timestamp t1 is only
                                                                         required when PTP operates in two-step mode.
    II.     SYSTEM MODEL                                                 B. Time Delay Attack
A. Precision Time Protocol                                                However, if the synchronization path is not symmetric
            The precision time protocol, as defined in the IEEE 1588     because of malicious network activities, for example, the offset
standard [2], is a network protocol that synchronizes devices            calculations are based on an invalid assumption, leading to
with an accuracy of less than 1 µs. Thereby, the standard                erroneous synchronization results. So, if attackers were able
considers various clock types to account for different device            1In this work, we stick to the terminology used in the official standard to
behaviors in common PTP networks. Particularly, Ordinary                 avoid any confusion besides being potentially inappropriate.

## Page 3

to deliberately delay the Sync and Delay_Req messages by               D. Attacker Model
1 and 2 respectively with 1 6= 2, as illustrated in Fig. 2b,       There exist many attacks against time synchronization pro-
the clock offset θ0 would mistakenly compute as:                       tocols, particularly against PTP [14]. In this work, however, we
                                                                       mainly focus on delay attacks and related attacker capabilities
θ0 =     ((t2 + 1) − t1) − ((t4 + 2) − t3)                           due to their criticality. Similar to [3, 5], we deny the attackers
                        2                                              internal access to the protocol, i.e., the possibility to directly
     (t2 − t1) − (t4 − t3)      1 − 2                        (2)     modify PTP header fields. If this was possible, the attackers
 =                      2        +     2                               were powerful enough to manipulate the synchronization on a
 = θ +              α                                                  protocol level by changing timestamps and the correction field
                    2                                                  contents, which would render delay attacks superfluous. Secu-
with α = dMS − dSM = 1 − 2. Provided α = 0, the                      rity protocols, such as IPsec and MACsec, can be appropriate
path is perfectly symmetric, and the time synchronization is           remedies to ensure message integrity. Furthermore, attackers
successful. However, if α 6= 0, the path becomes asymmetric,           are not allowed to compromise hosts or intermediary network
and the synchronized clock runs behind or ahead in time of             devices in a way that would grant them internal protocol access
the Grandmaster clock, respectively. The described time delay          or allow them to update the clocks directly with a similar
attack can be implemented in multiple ways. For example,               reasoning.
Barreto et al. [3] present a static delay attack scenario, where       Nevertheless, we assume the attackers to have full knowl-
the attackers deliberately extend the optical fibers in smart          edge of the network topology, including knowledge about
grid networks to add a constant one-way delay, turning the             deployed PTP clock types. Additionally, they are fully aware
synchronization path asymmetric. In [5], the authors perform           of any implemented protection methods (e.g., IPsec). After
an incremental delay attack, where the introduced asymmetric           compromising a link, the attackers can delay all passing
path delay gradually increases, to showcase more dynamic               packets individually. More precisely, they can deliberately add
attacks. Both works show the general feasibility of time delay         unidirectional delays to selected messages in both transmission
attacks and further emphasize their devastating impact on PTP,         directions independently. This fine-grained packet delay is
highlighting the great need for sound countermeasures.                 even possible with specific protection mechanisms enabled,
                                                                       such as traffic encryption, as shown in [4]. Moreover, the
                                                                       attackers are able to simultaneously perform multiple delay
C. Network Model                                                       attacks precisely synchronized at different locations in the
                                                                       network if they compromise more than one link. There are
             A typical PTP deployment comprises an entire network,     no restrictions on the number of compromised links or the
including many devices that shall be synchronized. Therefore,          strategy of how attackers perform joint attacks. However, we
we model a given PTP network as the graph G = (V, E)                   assume that the selection of hijacked links will remain constant
with V = {v0, . . . , vn}, n ∈ N denoting the set of vertices          for a sufficiently long period to allow for steady-state analysis.
and E = {e0, . . . , em} ⊆ V × V, m ∈ N the set of                     Particularly, the attackers may freely change the introduced
edges. Each vertex vi ∈ V represents a node participating              delay for an attacked link over time but not attack a different
in the PTP protocol. For proper synchronization, we require            link. Finally, we require all nodes that participate in the PTP
at least the elected Grandmaster node and one additional slave         protocol to be honest, i.e., to follow the protocol as specified in
device that synchronizes to the master. Thus, we assume our            the standard or in our proposed PTPsec protocol, respectively.
vertex set V to contain these two nodes at the minimum,                    III.     ASYMMETRY ANALYSIS
which we denote for further reference as M ∈ V for the                 If we could precisely measure unidirectional delays in
master and S ∈ V for the slave node, respectively. All edges           the network, time delay attacks would be easily detected.
ei ∈ E are considered bidirectional and model the connecting           However, accurate one-way path delay measurements are a
links between all involved network devices. Furthermore, we            challenging problem in network theory [15]. In the following
assume G to be connected. Hence, at least one path connects            analysis, we benefit from the work of Gurewitz et al. [16, 17]
M and S for the PTP message exchange, which we denote                  on one-way delay estimation which we extend to derive our
as P0. Also, we extend the notation of α to express the                cyclic path asymmetry analysis. Additionally, we propose a
asymmetry αei          of a specific edge ei ∈ E. Additionally, we     general path asymmetry model that forms the basis for the
define the path asymmetry αPi , which is experienced by all            delay attack detection method presented in § IV. First, we
traversing packets on path Pi, as the sum of the individual            start with a simple two-node example from which we develop
link asymmetries of all composing links:                               the general model for arbitrary networks.
     αPi =              X    αej , ∀ej ∈ Pi.                   (3)     A. Two-Node Scenario
                        j                                              Given a simple synchronization scenario with only two
      Finally, we assume full control of the packet routing, which     nodes M and S and one attacked edge e0, as shown in
can be achieved, for example, by leveraging Software-defined           Fig. 3a, we are trying to estimate the link asymmetry αe0     6= 0.
Networking (SDN) capabilities [7].                                     However, it is impossible to reliably determine αe0 with only

## Page 4

                                                                                        while the individual links become asymmetric. In such a
                                                                                        case, we need another edge e2 with symmetric link delay for
                                                                                        compensation. This additional link increases the number of
                                                                                        cycles in our network allowing for further independent cyclic
                                                                                        measurements. With two redundant edges, we can perform two
                                                                                        asymmetry measurements that include e0 leading to:

    Fig. 3: Cyclic path asymmetry analysis illustrated with two nodes. While                       α (1) = RT Te0,e1  − RT Te1,e0                   (6)
    there is no efficient method to calculate the asymmetry with only one link                     α (2) = RT Te0,e2  − RT Te2,e0
    (a), a second link enables a cyclic structure for further analysis (b). Two RTT
    measurements in opposing directions can be smartly combined to determine            with α(1) and α(2) being independent estimates for the targeted
    the link asymmetry αe0 of the attacked link e0.                                     link asymmetry αe0. Although α(1)           might equal to zero
                                                                                        indicating perfect link symmetry due to the mentioned attack
    one available link. Thus, we need at least one additional link to                   strategy, α(2) will   yield the correct estimate because of the
    obtain a circular structure that we can use for further analysis.                   demanded link symmetry of e2 and the reasoning of (5).
                            1) One redundant link: If there exists a second edge e1            Similarly, we can derive the general case of n redundant
    which is redundant to e0, both edges form a cycle, as depicted                      edges (in addition to e0) for the two-node scenario. From
    in Fig. 3b. Now, we can perform a cyclic RTT measurement                            2n pairwise RTT measurements RT Te0,ei           and RT Tei,e0,
    using e0 and e1 by forwarding a packet from M to S on link                          i ∈ [1, n], we get n estimates for the link asymmetry αe0 :
    e0 which is subsequently returned to M via e1. Upon arrival
    at node M, the elapsed time RT Te0,e1     computes as:                                         α (1) = RT Te0,e1  − RT Te1,e0
   RT Te0,e1 = tin − teg                                                        (4)                α (2) = RT Te0,e2  − RT Te2,e0                   (7)
    where tin is the packet’s measured ingress and teg the egress                                        .
    timestamp at node M. Additionally, we conduct a second RTT                                     α (n)      = RT Te0,en − RT Ten,e0
    measurement RT Te1,e0 with reverse transmission direction,                          Furthermore, we can state the following important finding:
    i.e., forwarding the packet on link e1 to S and returning it
    via e0. Both measurements include unidirectional delays of                           Finding 1: In order to successfully determine αe0, we
    e0, however, in opposite directions. For RT Te0,e1 ,                    edge e0    need at least one link ei, i ∈ [1, n] with symmetric link
    contributes in forward direction (M to S) while RT Te1,e0                             delay αei = 0, which is redundant to e0. Using this
    contains its delay in backward direction (S to M). If we further                      symmetric link ei, the asymmetry measurement yields
    assume that link e1 is perfectly symmetric (αe1 = 0), i.e.,                        a correct estimate α (i)  = RT Te0,ei − RT Tei,e0 = αe0.
    the contributed link delay is equal in both directions, we can
    calculate the asymmetry of link e0 as:                                              This necessary condition directly results from the previous
                                                                                        reasoning that attackers could introduce various unidirectional
αe0 = RT Te0,e1 − RT Te1,e0                                                     (5)     delays to cancel out each other in the cyclic measurements if
    Note that the opposing one-way delays of link e1 cancel out                         we allowed all links to be asymmetric.
    due to its symmetry and we are left with the desired difference
    of both unidirectional delays of e0. Here, the essential part is                    B. Multi-Node Scenario
    the cyclic measurement approach capturing the opposing one-                                Realistic networks usually comprise more than two nodes.
    way delays of a single link isolated in distinct measurements.                      Therefore, we need to derive a general path asymmetry model
    Furthermore, the two RTTs measurements originate from the                           that is applicable to networks of any size. Similar to the two-
    same clock avoiding the need for any time synchronization.                          node scenario, we attempt to estimate the asymmetry αP0
    Also note that the same measurements could have likewise                            on the synchronization path P0. We equally require at least
    been taken on node S since the starting point in a cyclic                           one redundant path P1 in addition to P0, as exemplified in
    measurement is irrelevant.                                                          Fig. 4, to enable the cyclic measurements previously proposed
                             2) N redundant links: In the previous example with one     in § III-A. Note that P1 must not share any edge with P0
    redundant edge, the asymmetry measurement only worked                               to be considered fully redundant since all edges of P0 are
    because we assumed the additional link e1 to be symmetric.                          contributing to its total path asymmetry as defined in (3). If
    However, if the second link was also asymmetric due to                              a single joint edge existed, it would affect both paths equally
    another delay attack, for example, attackers could thwart                           and make a cyclic measurement with independent forward and
    the measurement attempt while still successfully introducing                        backward delays impossible. Therefore, we need P0 and P1 to
    unidirectional delays on e0. For that, they need to add similar                     be edge-disjoint: P0 ∩ P1 = ∅. With this requirement, we can
    one-way delays  to both links e0 and e1 but in opposing                            formulate the general approach to estimate path asymmetries
    directions, so that the delays cancel out each other in (5)                         in arbitrary networks. Given the network G = (E, V ), the

## Page 5

                                                                                     Algorithm 1 Adapted Ford-Fulkerson Algorithm
                                                                                     Input: Network G = (V, E), Source M ∈ V , Sink S ∈ V
                                                                                     Output: Set of edge-disjoint paths P from M to S
                                                                                    1: paths ← ∅
                                                                                    2: flow(e) ← 0 for each e ∈ E
                                                                                    3: while p ← find M-S path with flow(e) = 0 ∀e ∈ p do
                                                                                    4:     paths.insert(p)
    Fig. 4: Redundant path principle in multi-node networks. To efficiently         5:     flow(e) ← 1 for each e ∈ p
    estimate the path asymmetry αP0, we require other edge-disjoint paths Pi        6: end while
    to enable cyclic RTT measurements.
                                                                                    7: return paths

    synchronization path P0, and n redundant paths Pi, i ∈ [1, n]
    between nodes M and S, we perform 2n cyclic RTT mea-                             into two groups, where one group is either entirely genuine
    surements for each pair P0 and Pi, i ∈ [1, n].                    From these     and the other fully attacked or vice versa. However, this
    measurements, we derive the following set of equations to get                    decision cannot be made without further assumptions, such
    n estimates for the path asymmetry αP0 :                                         as limiting the number of attackers to an upper bound of
                      (1) = RT TP0,P1                                                # attackers ≤ b n
                 α                       − RT TP1,P0                                                 2c.
                 α    (2) = RT TP0,P2    − RT TP2,P0                                 B. Attack Mitigation
                                                                             (8)            If an attack is detected, we can furthermore use the mea-
                          .                                                          sured path asymmetry αP0 of the synchronization path P0
                 α    (n) = RT TP0,Pn − RT TPn,P0                                    to mitigate the ongoing attack. For that, we calculate the
    Moreover, we state the generalized finding from our path                         rectified clock offset θrect that is compensating malicious path
    asymmetry analysis in arbitrary networks:                                        asymmetries using the reported PTP offset θrep from (1) and
                                                                                     the insight gained from (2):
    Finding 2: For all symmetric paths Pi, i                ∈ [1, n]                           αP0
    with αPi     = 0, we get correct estimates α    (i)            =                           θrect = θrep −     2                              (10)
  RT TP0,Pi − RT TPi,P0 = αP0. Hence, we require at                                  This rectified clock offset can be used as input for PTP’s
least one redundant path to be symmetric in order to                                 control algorithm to securely update the local clock oscillator
successfully determine the desired path asymmetry αP0                                despite any ongoing attack.
    for the synchronization path P0.
                                                                                     C. Finding Redundant Paths
                                                                                          Another essential aspect of the presented method is finding
    IV. ATTACK DETECTION AND MITIGATION                                              redundant paths in a given network G which results to finding
    A. Detection Criteria                                                            edge-disjoint paths to obtain full redundancy. For that, we
                            From (2), we know that successful time delay attacks     present an approach to derive all eligible paths by leverag-
    result in non-zero path asymmetries. Hence, we can now use                       ing both Menger’s theorem [18] and the Max-Flow-Min-Cut
    the previously derived path asymmetry model to detect and                        theorem [19]. Menger states there are k pairwise edge-disjoint
    mitigate these attacks in PTP networks. With n+ 1 total edge-                    M-S paths if and only if S is still reachable from M after
    disjoint paths Pi, i ∈ [0, n] connecting nodes M and S, where                    removing k − 1 arbitrary edges from the graph [18]. Hence,
    P0 is used for PTP synchronization, we yield n independent                       we are interested in the minimum edge cut k that is required
    asymmetry estimates for αP0 , as stated in (8). Based on these                   to disconnect the two nodes M and S in G. By introducing the
    estimates, we define the detection criterion for an ongoing                      non-negative capacity function c(e) = 1, which assigns each
    delay attack on path P0 impeding the time synchronization                        edge ei ∈ E the maximum capacity of one, this problem is
    between M and S as follows:                                                      equivalent to maximizing the flow from M to S, as stated by
                                                                                     the Max-Flow-Min-Cut theorem. Finally, the maximum flow
                          (    T rue,    ∃ α(i) 6= 0, i ∈ [1, n]                     can be efficiently computed by the Ford-Fulkerson algorithm
    delay_attack ←        F alse,        otherwise                           (9)     [20] in polynomial time. Thus, to derive the number of edge-
                                                                                     disjoint M-S paths in a given PTP network G, we propose
    Additionally, we know that the cyclic measurements only work                     an adapted version of the Ford-Fulkerson algorithm which
    if at least one path is symmetric. Thus, we can successfully                     is depicted in Algorithm 1.      First, we initialize the set of
    detect delay attacks that include up to n attacked paths.                        existing paths and the assigned flow values for each edge
    Furthermore, we can try to determine the actual position of                      to zero (lines 1-2). Then, we repeatedly search for M-S
    the attacked paths by analyzing the estimated path asym-                         paths containing only edges with remaining capacity, i.e., with
    metries α(i)                 and search for attack configurations that match     flow(e) = 0 (line 3) and insert them into the set of existing
    the obtained result. It turns out that we can cluster all paths                  paths (line 4). The search can be accomplished, for example,

## Page 6

                                                                                         response is returned to M via the redundant path Pi to finish
                                                                                         the round trip. Since this response has a different purpose than
                                                                                         existing PTP message types, we introduce the new message
                                                                                         type Meas in our proposed PTPsec protocol. Similar to Sync
                                                                                         messages, also Meas packets are PTP event messages due to
                                                                                         the requested timestamps at packet transmission and reception.
                                                                                         We denote the captured Meas timestamps with an additional
                                                                                         m, e.g., tm1 , to distinguish them from the four default PTP
                                                                                         timestamps. If the protocol operates in two-step mode, we
                                                                                         require an additional new message Meas_Fup to forward
                                                                                         the captured timestamp in a separate follow-up message. To
                                                                                         continue the message flow, S sends the expected Delay_Req
                                                                                         message via P0 to M which is immediately followed by
                                                                                         another Meas message to S via Pi upon reception to finish the
    Fig. 5: Proposed PTPsec message flow to protect against time delay attacks.          second measurement cycle yielding RT TPi,P0 . Finally, M an-
    After the reception of PTP event messages (Sync and Delay_Req), dedi-                swers the request with a Delay_Resp message to complete
    cated (Meas) messages are returned to the originator via a redundant network         the synchronization protocol. Fig. 5 shows the full sequence of
    path, here indicated with the additional TC, to enable cyclic path asymmetry
    measurements. The Meas_Fup messages convey the captured timestamps                   our proposed PTPsec protocol. With all captured timestamps
    tm1 and tm3 , respectively, when PTP operates in two-step mode.                      in this iteration, the two RTT measurements compute as:

    with the breadth-first search algorithm. For each found path,     RT TP0,Pi = (tm2 − t1) − (tm1 − t2)
    we additionally update the flow values of all comprising edges    RT TPi,P0 = (tm4 − t3) − (tm3 − t4)                                            (11)
    to mark their capacity as consumed (line 5) for subsequent
    search iterations. Finally, we return the resulting set of desired                   from which we derive the path asymmetry estimate for P0:
    edge-disjoint paths (line 7).
    D. Multipoint Synchronization                                         αP0 = RT TP0,Pi − RT TPi,P0                                                (12)
                             In typical PTP deployments, many nodes synchronize to a     Note that in the presented procedure, both critical PTP
    single Grandmaster clock. Thus, we need to find redundant                            event messages are fully integrated into the path asymmetry
    paths for all eligible synchronization paths. For this purpose,                      analysis. Consequently, any malicious delay equally impacts
    we run Algorithm 1 for every node, which shall be synchro-                           the synchronization and the detection mechanism, preventing
    nized to the Grandmaster before the normal protocol flow.                            attackers from bypassing our approach even if individual PTP
    Moreover, we can leverage SDN capabilities to dynamically                            messages can be distinguished and delayed. Since the proposed
    recalculate redundant paths on any network change.                                   PTPsec protocol requires additional measurement packets for
                                                                                         the asymmetry analysis, it also introduces a message overhead
V. PROPOSED PTPSEC                                                                       compared to conventional PTP. In particular, four supplemen-
                         As already highlighted in § II-A, the latest IEEE 1588-2019     tary packets are sent on each of the n redundant network path
    standard (PTP v2.1) is not secure against time delay attacks.                        per PTP synchronization cycle, resulting in the following total
    Hence, we propose the PTPsec protocol, which integrates                              number of PTPsec messages per cycle:
    appropriate countermeasures into the existing IEEE standard
    to improve PTP’s resilience against such attacks. Recall that             # packets = 4 + 4n                                                     (13)
    in our attacker model, attackers can precisely delay individual                      Note the packet count’s linear increase with the number of
    packets. Particularly, they could selectively delay only PTP                         redundant paths. However, the actual number of redundant
    messages if these were distinguishable and independent from                          paths to consider for securing the protocol is a security
    our measurement packets. Therefore, we need to entangle the                          parameter that can be adjusted depending on the assumed
    RTT measurements with the PTP synchronization procedure                              attack model. Furthermore, PTP messages usually account
    to prevent bypassing the presented attack detection and miti-                        only for a small part of the entire network traffic which
    gation approach. For that, we aim to integrate the two critical                      alleviates the impact of the packet increase.
    event messages Sync and Delay_Req directly into the RTT
    measurements. As a consequence, we ensure that deliberate                   VI. EVALUATION
    packet delays, which impede the time synchronization, also                                    For reliable evaluation, we validate the performance of
    equally affect the proposed detection approach.                                      our proposed PTPsec protocol under various realistic attack
                                  Let RT TP0,Pi be the RTT measurement including the     scenarios on our hardware testbed.
    synchronization path P0 and a redundant path Pi                      to estimate
    the path asymmetry αP0 .                           Then, the Sync message, which     A. Hardware Setup
    is sent from node M to S via P0, already initiates the first                                 The hardware setup consists of two PCs serving as master
    RTT measurement. Once received at node S, an immediate                               and slave to be synchronized. Both machines are operating on

## Page 7

                                                                                                   1000

                                                                                                    750

                                                                                                    500

                                                                                                    250

                                                                                                      0
                                                                                                   −250            Static Delay Attack
                                                                                                                   Actual Offset θact
                                                                                                   −500            Reported Offset θrep
                                                                                                                   Estimated Asymmetry αP0
                                                                                                   −750    0 100 200    300            400  500 600
Fig. 6: Hardware testbed for comprehensive evaluation of our proposed ap-                                        Elapsed Time [s]
proach under realistic circumstances. The synchronization path is interrupted    Offset / Asymmetry
                                                                                 Offset / Asymmetry
                                                                                 [µs]
                                                                                 Fig. 7: Static delay attack with 1 = 500 µs targeting the PTP Sync message
by a MitM attacker delaying selected PTP event messages in transit to diverge    [µs]
the slave clock. We closely monitor the malicious clock offset with the          between t = 100 s and t = 500 s. The difference between the measured
oscilloscope by comparing the generated PPS signals.                             clock offset (orange) and the reported clock offset (blue) confirms the ongoing
                                                                                 attack. Nevertheless, our proposed asymmetry analysis successfully detects
                                                                                 this malicious behavior (green).
Ubuntu 20.04 and run an implementation of our PTPsec proto-
col, which is based on linuxptp-v3.1.1. The two OCs use Intel                                       750            Actual Offset θact
i210 Network Interface Cards (NICs) for IEEE 1588-compliant                                         500            Reported Offset θrep
hardware timestamping support and are connected with wired                                                         Estimated Asymmetry αP0
Ethernet connections. The synchronization path is interrupted                                       250            Static Delay Attack
by an attack device running a Data Plane Development Kit                                              0
(DPDK) application to act as a transparent L2 switch. More-
over, it exploits its Machine-in-the-Middle (MitM) position                                        −250
to deliberately delay either Sync or Delay_Req messages                                            −500
to implement an effective time delay attack against PTP, as
described in § II-B. The other path is a direct point-to-point                                     −750    0  100  200  300      400      500   600
connection and constitutes a redundant path that is considered                                                   Elapsed Time [s]
genuine and symmetric for all following experiments. Extend-
ing the setup with more redundant paths follows the same                         Fig. 8: Static delay attack with 2 = 500 µs targeting the PTP Delay_Req
principle, as illustrated in Fig. 6. To monitor the actual clock                 message between t = 100 s and t = 500 s. The difference between the
                                                                                 measured clock offset (orange) and the reported clock offset (blue) confirms
offset between master and slave, we compare the generated                        the ongoing attack. However, our proposed asymmetry analysis successfully
Pulse-Per-Second (PPS) signal phases on a Rohde&Schwarz                          detects this malicious behavior (green).
RTB oscilloscope.
B. Asymmetry Detection                                                           rises to αP0 = 500 µs during the attack period. Since αP0 > 0,
In total, we present three experiments to validate the detec-                    the path delay from node M to node S is higher than in the
tion performance of our protocol. We attack the two relevant                     opposite direction, and we conclude an ongoing delay attack
PTP event messages Sync and Follow_Up and assume                                 targeting the Sync message. Hence, the applied attack was
that Meas and Meas_Fup are only sent via the symmetric                           successfully detected.
redundant path. Attacking the newly introduced measurement                       2) Static Delay (Delay_Req): We repeat the previous
packets instead of the PTP messages would lead to similar                        attack in the second experiment with the only difference in
results because for the asymmetry analysis, it is irrelevant                     the targeted PTP message. This time, the attacker delays
which specific path is attacked provided one genuine path                        passing Delay_Req messages instead, which results in a
exists.                                                                          path asymmetry in the opposite direction. As Fig. 8 depicts,
1) Static Delay (Sync): In the first experiment, we start                        the reported PTP clock offset θrep remains at zero while the
with a static attack scenario, where the attacker adds a constant                actual clock offset θact = −250 µs and the estimated path
delay of 1 = 500 µs to all passing Sync messages. The attack                    asymmetry αP0 = −500 µs both show a change of sign. The
starts at t = 100 s and lasts until t = 500 s, as shown in Fig. 7.               negative values match our expectations due to the different
During that period, we observe that the actual clock offset                      PTP message that was targeted. These results confirm that the
increases to θact = 250 µs, i.e., by half the introduced one-way                 attack detection works independently of the present asymmetry
delay, while the reported PTP clock offset θrep remains at zero.                 direction.
This behavior clearly shows the success of the delay attack                      3) Incremental Delay Attack: Finally, we change the attack
because the actual clock offset changes to the expected value                    method to an incremental delay attack to evaluate the detec-
given by (2) without being reported by conventional PTP.                         tion performance more dynamically. Therefore, we gradually
Furthermore, the estimated synchronization path asymmetry                        increase the packet delay for passing Sync messages to slowly










...




...










...

## Page 8

                       750                                                                                                                   1000
                       500                                                                                                                   500
                       250                                                                                                                   0
                                                                                                                                                                    Actual Offset θact
                      0                                                                                                                      −500                   Reported Offset θrep
                                                                               Static                                                                               Estimated Asymmetry αP0
                      −250      Incremental Delay Attack                       Attack                                                            0                  300                 600
                                      Actual Offset θact                                                                                     1000
                      −500            Reported Offset θrep
                                 Estimated Asymmetry αP0                                                                                     500
                      −750    0  100  200  300              400      500           600                                                       0
                                    Elapsed Time [s]
                                                                                                                                             −500      Attack           Atk.
    Fig. 9: Incremental delay attack, where the offset is gradually increased by
    Offset / Asymmetry
    Sync.
    Error
    [µs]
    [µs]
    ε                                                                                      Offset / Asymmetry [µs]Offset / Asymmetry [µs]        98    103          108 498    503      508
    ∆ = 1.25 µs starting at t = 100 s with 1 = 0 µs to a final level of
    1 = 500 µs. The attack targets the PTP Sync message. The difference                                                                        Elapsed Time [s]        Elapsed Time [s]
    between the measured clock offset (orange) and the reported clock offset               Fig. 11: Timing analysis of our attack detection approach. The magnified plots
    (blue) confirms the ongoing attack. Nevertheless, our proposed asymmetry               at the bottom illustrate our method’s fast detection time at the start and the
    analysis successfully detects this malicious behavior (green).                         end of the applied attack.

                       500        Static Delay Attack       εptp(P T P)                    during which the deployed attack is effective without an
                       250                                  εsec(P T P sec)                appropriate system response and, thus, needs to be minimized.
                      0                                                                    In our setup, the Sync message timeout interval is set to
                      −250
                      −500                                                                 1 s which also predetermines the clock update and asymmetry
                          0      100  200  300              400      500           600     measurement rate to approx. this period. As the plot in Fig. 11
                                    Elapsed Time [s]                                       shows, the measured path asymmetry follows the actual clock
    Fig. 10: Remaining clock error after delay attack compensation considering             offset almost immediately within less than five time steps at
    the estimated path asymmetry.                                                          the start and the end of the attack.

  VII. DISCUSSION
    diverge the slave’s clock. The attack starts at t = 100 s. Each                        The proposed PTPsec protocol has successfully detected and
    second, we increase the added delay by ∆ = 1.25 µs to                                 counteracted the delay attacks in all conducted experiments
    eventually reach a level of 1 = 500 µs at t = 500 s which                             validating the effectiveness of our approach. Since the chosen
    remains as a static offset until the end of the experiment.                            scenarios are representative of all known time delay attack
    From the results in Fig. 9, we observe that not only the                               strategies, we can conclude that our cyclic asymmetry analysis
    actual clock offset gradually ascends from θact = 0 µs to                              enables reliable attack mitigation provided redundant paths are
    θact = 250 µs, but also the estimated path asymmetry αP0                               available in the network. Interestingly, this redundancy require-
    slowly follows the incremental delay to reach a final level                            ment is already enforced by some communication standards,
    of αP0 = 500 µs. Therefore, we conclude that our proposed                              such as TSN, so our secure protocol could be deployed in
    protocol also reliably detects incremental delay attacks.                              related applications at no cost. In all other cases, the introduced
    C. Attack Mitigation                                                                   procedure in Algorithm 1 can serve as a network analysis
                                                                                           tool to evaluate the current security level regarding time delay
    As the previous experiments show, our proposed PTPsec                                  attacks. Once a bottleneck has been identified, the network
    protocol reliably detects the malicious path asymmetry in                              can be selectively patched to meet the specified requirements.
    all attack scenarios. To further evaluate the attack mitigation                        Regarding the protocol overhead of PTPsec, the increased
    performance, we analyze the synchronization errors εptp and                            security is not for free. Since both the number of successfully
    εsec of both conventional PTP and PTPsec, respectively, during                         detected asymmetric paths and the required packet count scale
    a static delay attack by comparing the reported clock offset                           with the number of redundant network paths, it is a trade-
    to the actual clock offset measured by the oscilloscope. For                           off between desired security and acceptable network load that
    PTPsec, we use the rectified offset from (10). As the results                          system designers have to make.
    in Fig. 10 illustrate, PTPsec reliably mitigates the attack.
VIII. RELATED WORK
    D. Detection Time                                                                      Attack detection and prevention in time synchronization
    In addition to the general detection and mitigation capabil-                           have been broadly covered by research in recent years. The
    ities, we further examine the timing behavior of the proposed                          proposed solutions to protect PTP from time delay attacks
    approach. Particularly, we investigate the elapsed time between                        can be mainly clustered into three groups. First, there exist
    the start of the attack and its visibility in the measured path                        threshold-based detection techniques. The idea is to contin-
    asymmetry, i.e., the detection time of our method. This time is                        uously monitor the reported clock offset and path delay and
    critical since it potentially opens a small window for attackers                       decide whether or not the system is under attack based on

## Page 9

a defined threshold. The threshold can be either static, as                  Table I: Delay Attack Detection Approaches Comparison
proposed by Ullmann et al. [21], or dynamically updated over
time, as presented in [6, 7]. However, the performance of these         Solution Approach  Attack Resistance      Scal. Exp.
techniques strongly depends on the chosen threshold, which                                Static     Incr. Select.
is quite challenging. The second category comprises solutions
that rely on special guard devices and additional reporting             [6]       Threshold
systems deployed in the network. Alghamdi et al. [22] present           [21]      Threshold
the idea of a trusted supervisor node that performs anomaly             [7]       Threshold
detection in the network to detect ongoing attacks. Moussa              [22]        Guard
et al. [9] propose a similar idea, including a dedicated guard          [9]         Guard
node that participates in the time synchronization protocol but
does not update its clock. Instead, it only compares the results        [11]        Guard
to another time reference to reveal potential delay attacks.            [12]        Guard
However, the guard node only secures its own synchronization            [13]      Path Red.
path, and other nodes that do not share the same path are still         [8]       Path Red.
vulnerable. In [11], Moussa et al. refine their initial proposal        PTPsec    Path Red.
and introduce a more sophisticated approach, where all nodes
additionally send timestamped reports to a specific network              no or n/a,   partially,     yes
time reference node. These reports are exchanged by means of
custom event messages that are not related to the PTP protocol
stack. Thus, sophisticated attackers can distinguish report              system are [7], [13], and [8]. However, [7] cannot reliably
messages from actual PTP messages and react differently to               detect incremental delay attacks because of the threshold-
disrupt time synchronization without being noticed. Moradi               based approach while additionally requiring an initial learning
et al. [12] present a similar method, including a dedicated              phase that invalidates with any network change. Furthermore,
reporting scheme for attack detection. The third class of                the presented solutions in [13] and [8] lack experimental val-
countermeasures utilizes path redundancy for time delay attack           idation and scalability, respectively. Moreover, while partially
protection. There exist some works, such as [23, 24, 25], which          providing sound detection approaches, none of the compared
cover path redundancy for network-based time synchronization             works can actually mitigate time delay attacks which is an
to improve the provided synchronization accuracy. While not              exclusive feature of PTPsec.
explicitly mentioning any security aspects, the works already
indicate the capabilities of redundant path approaches, which    IX. CONCLUSION
could also be adopted in the security domain. In [13], Mizrahi
proposes redundant paths as countermeasure for delay attacks                     This work introduces a theoretical model for cyclic path
and presents a theoretical analysis of this idea. Furthermore,           asymmetry analysis that can be efficiently used for time delay
Neyer et al. [8] perform supplementary experiments on a hard-            attack mitigation. The derived attack detection method reliably
ware testbed to showcase the general applicability of redundant          reveals both static and incremental time delay attacks provided
paths as viable improvement for time synchronization security.           the existence of at least one redundant network path with
Comparative Analysis: Table I presents an additional com-                symmetric delay. With PTPsec, we present a protocol that se-
parison between our proposed solution and existing works.                cures the latest IEEE 1588 standard against time delay attacks
The comparison is based on the adopted approach, the ability             by incorporating our proposed mitigation techniques on top
to detect static, incremental, and selective delay attacks, the          of conventional cryptographic countermeasures. This makes
scalability of the proposed solution, and the experimental               PTPsec fully resilient against all known attacks against PTP.
validation method employed (hardware setup, simulation, or               The experimental results show that our approach successfully
no validation). While all the solutions are capable of detecting         identifies fine-grained asymmetry changes with microsecond
static attacks, [6, 7, 21] fall short of fully detecting incremental     accuracy and minimal detection time in all evaluated scenarios.
attacks due to the threshold-based approach. Others, like                The authors have provided public access to their code and/or
[11, 12, 22], are still vulnerable to selective delay attacks,           data at https://github.com/tum-esi/ptpsec.
where the attackers distinguish between PTP and other net-
work traffic. In contrast to PTPsec, many other solutions do     ACKNOWLEDGMENT
not adequately scale either due to the need for a recurring setup
phase after each network change, as seen in [6, 21], including           This work has received funding from The Bavarian State
single points of failure [9, 22], or due to limitations in the           Ministry for the Economy, Media, Energy and Technology,
system model [8]. Furthermore, hardware testbed validation is            within the R&D program „Information and Communication
essential for ensuring the effectiveness of proposed detection           Technology”, managed by VDI/VDE Innovation + Technik
methods, which most of the compared solutions are lacking.               GmbH. Also, this work is supported by the European Union-
Based on Table I, the three most comparable solutions to our             funded project CyberSecDome (Agreement No.: 101120779).

## Page 10

    REFERENCES                                                    [13] T. Mizrahi, “A game theoretic analysis of delay attacks
     [1] A. Sargolzaei, K. Yen, and M. N. Abdelghani, “Delayed     against time synchronization protocols,” in 2012 IEEE
inputs attack on load frequency control in smart grid,” in         International Symposium on Precision Clock Synchro-
ISGT 2014.  IEEE, 2014, pp. 1–5.                                   nization for Measurement, Control and Communication
      [2] “IEEE standard for a precision clock synchronization     Proceedings.  IEEE, 2012, Conference Proceedings.
protocol for networked measurement and control sys-                  [14] W. Alghamdi and M. Schukat, “Precision time protocol
tems,” IEEE Std 1588-2019 (Revision of IEEE Std 1588-              attack strategies and their resistance to existing security
2008), pp. 1–499, 2020.                                            extensions,” Cybersecurity, vol. 4, no. 1, 2021.
       [3] S. Barreto, A. Suresh, and J.-Y. Le Boudec, “Cyber-       [15] J.-H. Choi and C. Yoo, “One-way delay estimation and
attack on packet-based time synchronization protocols:             its application,” Computer Communications, 2005.
The undetectable delay box,” in 2016 IEEE International               [16] O. Gurewitz and M. Sidi, “Estimating one-way delays
Instrumentation and Measurement Technology Confer-                 from cyclic-path delay measurements,” in Proceedings
ence Proceedings. IEEE, 2016, Conference Proceedings.              IEEE INFOCOM 2001. Conference on Computer Com-
[4] R. Annessi, J. Fabini, F. Iglesias, and T. Zseby, “Encryp-     munications. Twentieth Annual Joint Conference of the
tion is futile: Delay attacks on high-precision clock syn-         IEEE Computer and Communications Society (Cat. No.
chronization,” arXiv preprint arXiv:1811.08569, 2018.              01CH37213), vol. 2.  IEEE, 2001, pp. 1038–1044.
        [5] A. Finkenzeller, T. Wakim, M. Hamad, and S. Stein-         [17] O. Gurewitz, I. Cidon, and M. Sidi, “One-way delay
horst, “Feasible time delay attacks against the precision          estimation using network-wide measurements,” IEEE
time protocol,” in GLOBECOM 2022-2022 IEEE Global                  Transactions on Information Theory, vol. 52, no. 6, pp.
Communications Conference.      IEEE, 2022.                        2710–2724, 2006.
     [6] Q. Yang, D. An, and W. Yu, “On time desynchronization    [18] T. Böhme, F. Göring, and J. Harant, “Menger’s theorem,”
attack against ieee 1588 protocol in power grid systems,”          Journal of Graph Theory, vol. 37, no. 1, 2001.
in 2013 IEEE Energytech.    IEEE, 2013, pp. 1–5.                    [19] L. R. Ford and D. R. Fulkerson, “Maximal flow through
       [7] H. Li, D. Li, X. Zhang, G. Shou, Y. Hu, and Y. Liu,     a network,” Canadian journal of Mathematics, vol. 8, pp.
“A security management architecture for time synchro-              399–404, 1956.
nization towards high precision networks,” IEEE Access,             [20] L. R. Ford Jr and D. R. Fulkerson, Flows in networks.
vol. 9, pp. 117 542–117 553, 2021.                                 Princeton university press, 2015, vol. 54.
        [8] J. Neyer, L. Gassner, and C. Marinescu, “Redundant       [21] M. Ullmann and M. Vogeler, “Delay attacks — implica-
schemes or how to counter the delay attack on time                 tion on ntp and ptp time synchronization,” in 2009 Inter-
synchronization protocols,” in 2019 IEEE International             national Symposium on Precision Clock Synchronization
Symposium on Precision Clock Synchronization for Mea-              for Measurement, Control and Communication.           IEEE,
surement, Control, and Communication (ISPCS). IEEE,                2009, Conference Proceedings.
2019, Conference Proceedings.                                        [22] W. Alghamdi and M. Schukat, “Cyber attacks on preci-
      [9] B. Moussa, M. Debbabi, and C. Assi, “A detection and     sion time protocol networks—a case study,” Electronics,
mitigation model for ptp delay attack in a smart grid              vol. 9, no. 9, p. 1398, 2020.
substation,” in 2015 IEEE International Conference on           [23] T. Mizrahi, “Slave diversity: Using multiple paths to im-
Smart Grid Communications (SmartGridComm). IEEE,                   prove the accuracy of clock synchronization protocols,”
2015, Conference Proceedings, pp. 497–502.                         in 2012 IEEE International Symposium on Precision
      [10] W. Alghamdi and M. Schukat, “Advanced methodologies     Clock Synchronization for Measurement, Control and
to deter internal attacks in ptp time synchronization              Communication Proceedings.   IEEE, 2012.
networks,” in 2017 28th Irish Signals and Systems Con-                [24] A. Komes and C. Marinescu, “IEEE 1588 for redundant
ference (ISSC).  IEEE, 2017, Conference Proceedings.               ethernet networks,” in 2012 IEEE International Sympo-
       [11] B. Moussa, M. Kassouf, R. Hadjidj, M. Debbabi, and     sium on Precision Clock Synchronization for Measure-
C. Assi, “An extension to the precision time protocol              ment, Control and Communication Proceedings.          IEEE,
(ptp) to enable the detection of cyber attacks,” IEEE              2012, Conference Proceedings.
Transactions on Industrial Informatics, 2020.                      [25] A. Shpiner, Y. Revah, and T. Mizrahi, “Multi-path time
        [12] M. Moradi and A. H. Jahangir, “A new delay attack     protocols,” in 2013 IEEE International Symposium on
detection algorithm for ptp network in power substation,”          Precision Clock Synchronization for Measurement, Con-
International Journal of Electrical Power & Energy                 trol and Communication (ISPCS) Proceedings.           IEEE,
Systems, vol. 133, 2021.                                           2013.

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[papers/2024-INFOCOM-PTPsec.pdf]]`
