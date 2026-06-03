---
source: https://book.systemsapproach.org/internetworking/problem.html
title: "Problem: Not All Networks are Directly Connected &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation"
type: ebook-section
---

# Problem: Not All Networks are Directly Connected &mdash; Computer Networks: A Systems Approach Version 6.2-dev documentation

Problem: Not All Networks are Directly Connected — Computer Networks: A Systems Approach Version 6.2-dev documentation
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
Problem: Not All Networks are Directly Connected
- [3.1 Switching Basics](switching.html)
- [3.2 Switched Ethernet](ethernet.html)
- [3.3 Internet (IP)](basic-ip.html)
- [3.4 Routing](routing.html)
- [3.5 Implementation](impl.html)
- [Perspective: Virtual Networks All the Way Down](trend.html)
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
          - [Chapter 3:  Internetworking](../internetworking.html)
      - Problem: Not All Networks are Directly Connected
      -
            [ View page source](../_sources/internetworking/problem.rst.txt)
        [ Previous](../internetworking.html)
        [Next ](switching.html)
# Problem: Not All Networks are Directly Connected
As we have seen, there are many technologies that can be used to build
last-mile links or to connect a modest number of nodes together, but how
do we build networks of global scale? A single Ethernet can interconnect
no more than 1024 hosts; a point-to-point link connects only two.
Wireless networks are limited by the range of their radios. To build a
global network, we need a way to interconnect these different types of
links and multi-access networks. The concept of interconnecting
different types of networks to build a large, global network is the core
idea of the Internet and is often referred to as *internetworking*.
We can divide the internetworking problem up into a few subproblems.
First of all, we need a way to interconnect links. Devices that
interconnect links of the same type are often called *switches*, or
sometimes *Layer 2* (L2) switches. These devices are the first topic of
this chapter. A particularly important class of L2 switches in use today
are those used to interconnect Ethernet segments. These switches are
also sometimes called *bridges*.
The core job of a switch is to take packets that arrive on an input and
*forward* (or *switch*) them to the right output so that they will reach
their appropriate destination. There are a variety of ways that the
switch can determine the “right” output for a packet, which can be
broadly categorized as connectionless and connection-oriented
approaches. These two approaches have both found important application
areas over the years.
Given the enormous diversity of network types, we also need a way to
interconnect disparate networks and links (i.e., deal with
*heterogeneity*). Devices that perform this task, once called
*gateways*, are now mostly known as *routers*, or alternatively, *Layer
3* (L3) switches. The protocol that was invented to deal with
interconnection of disparate network types, the Internet Protocol (IP),
is the topic of our second section.
Once we interconnect a whole lot of links and networks with switches and
routers, there are likely to be many different possible ways to get from
one point to another. Finding a suitable path or *route* through a
network is one of the fundamental problems of networking. Such paths
should be efficient (e.g., no longer than necessary), loop free, and
able to respond to the fact that networks are not static—nodes may fail
or reboot, links may break, and new nodes or links may be added. Our
third section looks at some of the algorithms and protocols that have
been developed to address these issues.
Once we understand the problems of switching and routing, we need some
devices to perform those functions. This chapter concludes with some
discussion of the ways switches and routers are implemented. While many
packet switches and routers are quite similar to a general-purpose
computer, there are many situations where more specialized designs are
used. This is particularly the case at the high end, where there seems
to be a never-ending need for more switching capacity that can handle
the ever-increasing traffic load in the Internet’s core.
        [ Previous](../internetworking.html)
        [Next ](switching.html)
    © Copyright 2024.
  Built with [Sphinx](https://www.sphinx-doc.org/) using a
    [theme](https://github.com/readthedocs/sphinx_rtd_theme)
    provided by [Read the Docs](https://readthedocs.org).