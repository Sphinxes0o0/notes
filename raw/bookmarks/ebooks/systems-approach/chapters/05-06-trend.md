---
source: https://book.systemsapproach.org/e2e/trend.html
title: "Perspective: HTTP is the New Narrow Waist &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation"
type: ebook-section
---

# Perspective: HTTP is the New Narrow Waist &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation

Perspective: HTTP is the New Narrow Waist — Computer Networks: A Systems Approach Version 6.2-dev documentation
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
- [Chapter 5:  End-to-End Protocols](../e2e.html)
[Problem: Getting Processes to Communicate](problem.html)
- [5.1 Simple Demultiplexor (UDP)](udp.html)
- [5.2 Reliable Byte Stream (TCP)](tcp.html)
- [5.3 Remote Procedure Call](rpc.html)
- [5.4 Transport for Real-Time (RTP)](rtp.html)
- Perspective: HTTP is the New Narrow Waist
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
          - [Chapter 5:  End-to-End Protocols](../e2e.html)
      - Perspective: HTTP is the New Narrow Waist
      -
            [ View page source](../_sources/e2e/trend.rst.txt)
        [ Previous](rtp.html)
        [Next ](../congestion.html)
# Perspective: HTTP is the New Narrow Waist
The Internet has been described as having a *narrow waist* architecture,
with one universal protocol in the middle (IP), widening to support many
transport and application protocols above it (e.g., TCP, UDP, RTP,
SunRPC, DCE-RPC, gRPC, SMTP, HTTP, SNMP) and able to run on top of many
network technologies below (e.g., Ethernet, PPP, WiFi, SONET, ATM). This
general structure has been a key to the Internet becoming ubiquitous: by
keeping the IP layer that everyone has to agree to minimal, a thousand
flowers were allowed to bloom both above and below. This is now a widely
understood strategy for any platform trying to achieve universal
adoption.
But something else has happened over the last 30 years. By not
addressing all the issues the Internet would eventually face as it grew
(e.g., security, congestion, mobility, real-time responsiveness, and so
on) it became necessary to introduce a series of additional features
into the Internet architecture. Having IP’s universal addresses and
best-effort service model was a necessary condition for adoption, but
not a sufficient foundation for all the applications people wanted to
build.
We’re yet to see some of these solutions—future chapters will describe
how the Internet manages congestion ([Chapter 6](../congestion.html#chapter-6-congestion-control)), provides security ([Chapter 8](../security.html#chapter-8-network-security)), and supports real-time multimedia
applications ([Chapters 7](../data.html#chapter-7-end-to-end-data) and
[9](../applications.html#chapter-9-applications))—but it is informative to take this
opportunity to reconcile the value of a universal narrow waist with the
evolution that inevitably happens in any long-lived system: the “fixed
point” around which the rest of the architecture evolves has moved to a
new spot in the software stack. In short, HTTP has become the new narrow
waist; the one shared/assumed piece of the global infrastructure that
makes everything else possible. This didn’t happen overnight or by
proclamation, although some did anticipate it would happen. The narrow
waist drifted slowly up the protocol stack as a consequence of an
evolution (to mix geoscience and biological metaphors).
[![../_images/Slide31.png](./images/Slide31.png)
](../_images/Slide31.png)
Figure 151. HTTP (plus TLS, TCP, and IP) forming the narrow
waist of today’s Internet architecture.
Putting the narrow waist label purely on HTTP is an over simplification.
It’s actually a team effort, with the HTTP/TLS/TCP/IP combination now
serving as the Internet’s common platform.
- HTTP provides global object identifiers (URIs) and a simple GET/PUT
interface.
- TLS provides end-to-end communication security.
- TCP provides connection management, reliable transmission, and
congestion control.
- IP provides global host addresses and a network abstraction layer.
In other words, even though you are free to invent your own congestion
control algorithm, TCP solves this problem quite well, so it makes sense
to reuse that solution. Similarly, even though you are free to invent
your own RPC protocol, HTTP provides a perfectly serviceable one (which
because it comes bundled with proven security, has the added feature of
not being blocked by enterprise firewalls), so again, it makes sense to
reuse it rather than reinvent the wheel.
Somewhat less obviously, HTTP also provides a good foundation for
dealing with mobility. If the resource you want to access has moved,
you can have HTTP return a *redirect response* that points the client
to a new location. Similarly, HTTP enables injecting *caching proxies*
between the client and server, making it possible to replicate popular
content in multiple locations and save clients the delay of going all
the way across the Internet to retrieve some piece of
information. (Both of these capabilities are discussed in
[Section 9.1](../applications/traditional.html#traditional-applications).) Finally, HTTP has
been used to deliver real-time multimedia, in an approach known as
*adaptive streaming*. (See how in [Section 7.2](../data/multimedia.html#multimedia-data).)
Broader Perspective
To continue reading about the cloudification of the Internet, see
[Perspective: Software-Defined Traffic Engineering](../congestion/trend.html#perspective-software-defined-traffic-engineering).
To learn more about the centrality of HTTP, we recommend: [HTTP:
An Evolvable Narrow Waist for the Future
Internet](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2012/EECS-2012-5.pdf),
January 2012.
        [ Previous](rtp.html)
        [Next ](../congestion.html)
    © Copyright 2024.
  Built with [Sphinx](https://www.sphinx-doc.org/) using a
    [theme](https://github.com/readthedocs/sphinx_rtd_theme)
    provided by [Read the Docs](https://readthedocs.org).