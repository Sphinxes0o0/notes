---
source: https://book.systemsapproach.org/scaling/problem.html
title: "Problem: Scaling to Billions &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation"
type: ebook-section
---

# Problem: Scaling to Billions &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation

Problem: Scaling to Billions — Computer Networks: A Systems Approach Version 6.2-dev documentation
      -
          [
            Computer Networks: A Systems Approach
          ](../index.html)
    *
              Table of Contents
[Foreword](../foreword.html)
- [Foreword to the First Edition](../foreword_1e.html)
- [Preface](../preface.html)
- [Chapter 1:  Foundation](../foundation.html)
- [Chapter 2:  Direct Links](../direct.html)
- [Chapter 3:  Internetworking](../internetworking.html)
- [Chapter 4:  Advanced Internetworking](../scaling.html)
Problem: Scaling to Billions
- [4.1 Global Internet](global.html)
- [4.2 IP Version 6](ipv6.html)
- [4.3 Multicast](multicast.html)
- [4.4 Multiprotocol Label Switching](mpls.html)
- [4.5 Routing Among Mobile Devices](mobile-ip.html)
- [Perspective: The Cloud is Eating the Internet](trend.html)
- [Chapter 5:  End-to-End Protocols](../e2e.html)
- [Chapter 6:  Congestion Control](../congestion.html)
- [Chapter 7: End-to-End Data](../data.html)
- [Chapter 8: Network Security](../security.html)
- [Chapter 9: Applications](../applications.html)
- [About This Book](../README.html)
- [Read the Latest!](../latest.html)
- [Print Copies](../print.html)
          *
          [Computer Networks: A Systems Approach](../index.html)
      - [](../index.html)
          - [Chapter 4:  Advanced Internetworking](../scaling.html)
      - Problem: Scaling to Billions
      -
            [ View page source](../_sources/scaling/problem.rst.txt)
        [ Previous](../scaling.html)
        [Next ](global.html)
# Problem: Scaling to Billions
We have now seen how to build an internetwork that consists of a number
of networks of different types. That is, we have dealt with the problem
of *heterogeneity*. The second critical problem in
internetworking—arguably the fundamental problem for all networking—is
*scale*. To understand the problem of scaling a network, it is worth
considering the growth of the Internet, which has roughly doubled in
size each year for 30 years. This sort of growth forces us to face a
number of challenges.
Chief among these is how do you build a routing system that can handle
hundreds of thousands of networks and billions of end nodes? As we will
see in this chapter, most approaches to tackling the scalability of
routing depend on the introduction of hierarchy. We can introduce
hierarchy in the form of areas within a domain; we also use hierarchy to
scale the routing system among domains. The interdomain routing protocol
that has enabled the Internet to scale to its current size is BGP. We
will take a look at how BGP operates, and consider the challenges faced
by BGP as the Internet continues to grow.
Closely related to the scalability of routing is the problem of
addressing. Even two decades ago it had become apparent that the 32-bit
addressing scheme of IP version 4 would not last forever. That led to
the definition of a new version of IP—version 6, since version 5 had
been used in an earlier experiment. IPv6 primarily expands the address
space but also adds a number of new features, some of which have been
retrofitted to IPv4.
While the Internet continues to grow in size, it also needs to evolve
its functionality. The final sections of this chapter cover some
significant enhancements to the Internet’s capabilities. The first,
multicast, is an enhancement of the basic service model. We show how
multicast—the ability to deliver the same packets to a group of
receivers efficiently—can be incorporated into an internet, and we
describe several of the routing protocols that have been developed to
support multicast. The second enhancement, Multiprotocol Label Switching
(MPLS), modifies the forwarding mechanism of IP networks. This
modification has enabled some changes in the way IP routing is performed
and in the services offered by IP networks. Finally, we look at the
effects of mobility on routing and describe some enhancements to IP to
support mobile hosts and routers. For each of these enhancements, issues
of scalability continue to be important.
        [ Previous](../scaling.html)
        [Next ](global.html)
    © Copyright 2024.
  Built with [Sphinx](https://www.sphinx-doc.org/) using a
    [theme](https://github.com/readthedocs/sphinx_rtd_theme)
    provided by [Read the Docs](https://readthedocs.org).