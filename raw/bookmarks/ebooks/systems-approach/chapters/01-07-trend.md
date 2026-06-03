---
source: https://book.systemsapproach.org/foundation/trend.html
title: "Perspective: Feature Velocity &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation"
type: ebook-section
---

# Perspective: Feature Velocity &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation

Perspective: Feature Velocity — Computer Networks: A Systems Approach Version 6.2-dev documentation
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
[Problem: Building a Network](problem.html)
- [1.1 Applications](applications.html)
- [1.2 Requirements](requirements.html)
- [1.3 Architecture](architecture.html)
- [1.4 Software](software.html)
- [1.5 Performance](performance.html)
- Perspective: Feature Velocity
- [Chapter 2:  Direct Links](../direct.html)
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
          - [Chapter 1:  Foundation](../foundation.html)
      - Perspective: Feature Velocity
      -
            [ View page source](../_sources/foundation/trend.rst.txt)
        [ Previous](performance.html)
        [Next ](../direct.html)
# Perspective: Feature Velocity
This chapter introduces some of the stakeholders in computer
networks—network designers, application developers, end users, and
network operators—to help motivate the technical requirements that shape
how networks are designed and built. This presumes all design decisions
are purely technical, but of course, that’s usually not the case. Many
other factors, from market forces, to government policy, to ethical
considerations, also influence how networks are designed and built.
Of these, the marketplace is the most influential, and corresponds to
the interplay between network operators (e.g., AT&T, Comcast, Verizon,
DT, NTT, China Unicom), network equipment vendors (e.g., Cisco, Juniper,
Ericsson, Nokia, Huawei, NEC), application and service providers (e.g.,
Facebook, Google, Amazon, Microsoft, Apple, Netflix, Spotify), and of
course, subscribers and customers (i.e., individuals, but also
enterprises and businesses). The lines between these players are not
always crisp, with many companies playing multiple roles. The most
notable examples are the large cloud providers, who (a) build
their own networking equipment using commodity components, (b) deploy
and operate their own networks, and (c) provide end-user services and
applications on top of their networks.
When you account for these other factors in the technical design
process, you realize there are a couple of implicit assumptions in the
textbook version of the story that need to be reevaluated. One is that
designing a network is a one-time activity. Build it once and use it
forever (modulo hardware upgrades so users can enjoy the benefits of the
latest performance improvements). A second is that the job of building
the network is largely divorced from the job of operating the network.
Neither of these assumptions is quite right.
The network’s design is clearly evolving, and we have documented these
changes with each new edition of the textbook over the years. Doing that
on a timeline measured in years has historically been good enough, but
anyone that has downloaded and used the latest smartphone app knows how
glacially slow anything measured in years is by today’s standards.
Designing for evolution has to be part of the decision-making process.
On the second point, the companies that build networks are almost always
the same ones that operate them. They are collectively known as *network
operators*, and they include the companies listed above. But if we again
look to the cloud for inspiration, we see that develop-and-operate isn’t
true just at the company level, but it is also how the fastest moving
cloud companies organize their engineering teams: around the *DevOps*
model. (If you are unfamiliar with DevOps, we recommend you read *Site
Reliability Engineering: How Google Runs Production Systems* to see how
it is practiced.)
What this all means is that computer networks are now in the midst of a
major transformation, with network operators trying to simultaneously
accelerate the pace of innovation (sometimes known as feature velocity)
and yet continue to offer a reliable service (preserve stability). And
they are increasingly doing this by adopting the best practices of cloud
providers, which can be summarized as having two major themes: (1) take
advantage of commodity hardware and move all intelligence into software,
and (2) adopt agile engineering processes that break down barriers
between development and operations.
This transformation is sometimes called the “cloudification” or
“softwarization” of the network, and while the Internet has always had
a robust software ecosystem, it has historically been limited to the
applications running *on top of* the network (e.g., using the Socket
API described in [Section 1.4](software.html#software)).  What’s changed
is that today these same cloud-inspired engineering practices are
being applied to the *internals* of the network. This new approach,
known as *Software Defined Networks* (SDN), is a game changer, not so
much in terms of how we address the fundamental technical challenges
of framing, routing, fragmentation/reassembly, packet scheduling,
congestion control, security, and so on, but in terms of how rapidly
the network evolves to support new features.
This transformation is so important that we take it up again in the
*Perspective* section at the end of each chapter. As these discussions
will explore, what happens in the networking industry is partly about
technology, but also partly about many other non-technical factors,
all of which is a testament to how deeply embedded the Internet
is in our lives.
Broader Perspective
To continue reading about the cloudification of the Internet, see
[Perspective: Race to the Edge](../direct/trend.html#perspective-race-to-the-edge).
To learn more about DevOps, we recommend: [Site Reliability
Engineering: How Google Runs Production Systems](https://www.amazon.com/Site-Reliability-Engineering-Production-Systems/dp/149192912X/ref=pd_bxgy_14_img_2/131-5109792-2268338?_encoding=UTF8&pd_rd_i=149192912X&pd_rd_r=4b77155f-234d-11e9-944e-278ce23a35b5&pd_rd_w=qIfxg&pd_rd_wg=12dE2&pf_rd_p=6725dbd6-9917-451d-beba-16af7874e407&pf_rd_r=5GN656H9VEG4WEVGB728&psc=1&refRID=5GN656H9VEG4WEVGB728),
2016.
        [ Previous](performance.html)
        [Next ](../direct.html)
    © Copyright 2024.
  Built with [Sphinx](https://www.sphinx-doc.org/) using a
    [theme](https://github.com/readthedocs/sphinx_rtd_theme)
    provided by [Read the Docs](https://readthedocs.org).