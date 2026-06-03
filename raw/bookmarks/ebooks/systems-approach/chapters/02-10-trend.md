---
source: https://book.systemsapproach.org/direct/trend.html
title: "Perspective: Race to the Edge &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation"
type: ebook-section
---

# Perspective: Race to the Edge &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation

Perspective: Race to the Edge — Computer Networks: A Systems Approach Version 6.2-dev documentation
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
[Problem: Connecting to a Network](problem.html)
- [2.1 Technology Landscape](perspective.html)
- [2.2 Encoding](encoding.html)
- [2.3 Framing](framing.html)
- [2.4 Error Detection](error.html)
- [2.5 Reliable Transmission](reliable.html)
- [2.6 Multi-Access Networks](ethernet.html)
- [2.7 Wireless Networks](wireless.html)
- [2.8 Access Networks](access.html)
- Perspective: Race to the Edge
- [Chapter 3:  Internetworking](../internetworking.html)
- [Chapter 4:  Advanced Internetworking](../scaling.html)
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
          - [Chapter 2:  Direct Links](../direct.html)
      - Perspective: Race to the Edge
      -
            [ View page source](../_sources/direct/trend.rst.txt)
        [ Previous](access.html)
        [Next ](../internetworking.html)
# Perspective: Race to the Edge
As we start to explore how softwarization is transforming the network,
we should recognize that it is the access network that connects homes,
businesses, and mobile users to the Internet that is undergoing the
most radical change. The fiber-to-the-home and cellular networks
described in [Section 2.8](access.html#access-networks) are currently
constructed from complex hardware appliances (e.g., OLTs, BNGs, BBUs,
EPCs). Not only have these devices historically been closed and
proprietary, but the vendors that sell them have typically bundled a
broad and diverse collection of functionality in each. As a
consequence, they have become expensive to build, complicated to
operate, and slow to change.
In response, network operators are actively transitioning from these
purpose-built appliances to open software running on commodity servers,
switches, and access devices. This initiative is often called *CORD*,
which is an acronym for **C**entral **O**ffice **R**e-architected
as a **D**atacenter, and as the name suggests, the idea is to build
the Telco Central Office (or the Cable Head End, resulting in the
acronym *HERD*) using exactly the same technologies as in the large
datacenters that make up the cloud.
The motivation for operators to do this is in part to benefit from the
cost savings that come from replacing purpose-built appliances with
commodity hardware, but it is mostly driven by the need to accelerate
the pace of innovation. Their goal is to enable new classes of edge
services—e.g., Public Safety, Autonomous Vehicles, Automated Factories,
Internet-of-Things (IoT), Immersive User Interfaces—that benefit from
low latency connectivity to end users, and more importantly, to the
increasing number of devices those users surround themselves with. This
results in a multi-tier cloud similar to the one shown in Figure
55.
[![../_images/Slide3.png](./images/Slide3.png)
](../_images/Slide3.png)
Figure 55. Emerging multi-tier cloud includes datacenter-based public clouds,
IXP-hosted distributed clouds, and access-based edge clouds, such as
CORD. While there are on the order of 150 IXP-hosted clouds
worldwide, we can expect there to be thousands or even tens of
thousands of edge clouds.
This is all part of the growing trend to move functionality out of the
datacenter and closer to the network edge, a trend that puts cloud
providers and network operators on a collision course. Cloud providers,
in pursuit of low-latency/high-bandwidth applications, are moving out of
the datacenter and towards the edge at the same time network operators
are adopting the best practices and technologies of the cloud to the
edge that already exists and implements the access network. It’s
impossible to say how this will all play out over time; both industries
have their particular advantages.
On the one hand, cloud providers believe that by saturating metro areas
with edge clusters and abstracting away the access network, they can
build an edge presence with low enough latency and high enough bandwidth
to serve the next generation of edge applications. In this scenario, the
access network remains a dumb bit-pipe, allowing cloud providers to
excel at what they do best: run scalable cloud services on commodity
hardware.
On the other hand, network operators believe that by building the next
generation access network using cloud technology, they will be able to
co-locate edge applications in the access network. This scenario comes
with built-in advantages: an existing and widely distributed physical
footprint, existing operational support, and native support for both
mobility and guaranteed service.
While acknowledging both of these possibilities, there is a third
outcome that is not only worth considering, but also worth working
towards: the *democratization of the network edge.* The idea is to make
the access-edge cloud accessible to anyone, and not strictly the domain
of incumbent cloud providers or network operators. There are three
reasons to be optimistic about this possibility:
- Hardware and software for the access network is becoming commoditized
and open. This is a key enabler that we were just talking about. If
it helps Telcos and CableCos be agile, then it can provide the same
value to anyone.
- There is demand. Enterprises in the automotive, factory, and
warehouse space increasingly want to deploy private 5G networks for a
variety of physical automation use cases (e.g., a garage where a
remote valet parks your car or a factory floor making use of
automation robots).
- Spectrum is becoming available. 5G is opening up for use in an
unlicensed or lightly licensed model in the US and Germany as two
prime examples, with other countries soon to follow. This means 5G
should have around 100-200 MHz of spectrum available for private use.
In short, the access network has historically been the purview of the
Telcos, CableCos, and the vendors that sell them proprietary boxes, but
the softwarization and virtualization of the access network opens the
door for anyone (from smart cities to underserved rural areas to
apartment complexes to manufacturing plants) to establish an access-edge
cloud and connect it to the public Internet. We expect it to become as
easy to do this as it is today to deploy a WiFi router. Doing so not
only brings the access-edge into new (edgier) environments, but also has
the potential to open the access network to developers that
instinctively go where there are opportunities to innovate.
Broader Perspective
To continue reading about the cloudification of the Internet, see
[Perspective: Virtual Networks All the Way Down](../internetworking/trend.html#perspective-virtual-networks-all-the-way-down).
To learn more about the transformation taking place in access networks, we recommend: [CORD: Central Office Re-architected as a Datacenter, IEEE Communications, October 2016](https://wiki.opencord.org/display/CORD/Documentation?preview=/1278027/1966399/PETERSON_CORD.pdf) and [Democratizing the Network Edge SIGCOMM CCR, April 2019](https://ccronline.sigcomm.org/2019/democratizing-the-network-edge/).
        [ Previous](access.html)
        [Next ](../internetworking.html)
    © Copyright 2024.
  Built with [Sphinx](https://www.sphinx-doc.org/) using a
    [theme](https://github.com/readthedocs/sphinx_rtd_theme)
    provided by [Read the Docs](https://readthedocs.org).