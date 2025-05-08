<p data-nodeid="26040" class="">上一讲我们提到，TCP 利用发送字节数和接收字节数，这个二元组的唯一性保证顺序。今天我们继续“03 | TCP 的封包格式：TCP 为什么要粘包和拆包？”的话题，讨论下保证顺序的具体算法，以及如何在保证顺序的基础上，同时追求更高的吞吐量。我认为，这部分知识也是 TCP 协议中最有趣的部分——TCP 的滑动窗口算法。</p>
<p data-nodeid="26041"><strong data-nodeid="26110">TCP 作为一个传输层协议，最核心的能力是传输。传输需要保证可靠性，还需要控制流速，这两个核心能力均由滑动窗口提供</strong>。而滑动窗口中解决的问题，是你在今后的工作中可以长期使用的，比如设计一个分布式的 RPC 框架、实现一个消息队列或者分布式的文件系统等。</p>
<p data-nodeid="26042">所以请你带着今天的问题“<strong data-nodeid="26116">滑动窗口和流速控制是怎么回事？</strong>”开始今天的学习吧！</p>
<h3 data-nodeid="26043">请求/响应模型</h3>
<p data-nodeid="26044">TCP 中每个发送的请求都需要响应。如果一个请求没有收到响应，发送方就会认为这次发送出现了故障，会触发重发。</p>
<p data-nodeid="26045">大体的模型，和下图很像。但是如果完全和下图一样，每一个请求收到响应之后，再发送下一个请求，吞吐量会很低。因为这样的设计，会产生网络的空闲时间，说白了，就是浪费带宽。带宽没有用满，意味着可以同时发送更多的请求，接收更多的响应。</p>
<p data-nodeid="26046"><img src="https://s0.lgstatic.com/i/image6/M00/3A/FA/CioPOWCCKu-AJ2NHAACe0M3wDME839.png" alt="image (1).png" data-nodeid="26122"></p>
<div data-nodeid="26047"><p style="text-align:center">TCP 请求/响应模型（吞吐量低）</p></div>
<p data-nodeid="26048">一种改进的方式，就是让发送方有请求就发送出去，而不是等待响应。通过这样的处理方式，发送的数据连在了一起，响应的数据也连在了一起，吞吐量就提升了。</p>
<p data-nodeid="26049"><img src="https://s0.lgstatic.com/i/image6/M00/3A/F2/Cgp9HWCCKvWAKGcEAACep0GQbI0182.png" alt="image (2).png" data-nodeid="26126"></p>
<p data-nodeid="26050">但是如果可以同时发送的数据真的非常多呢？比如成百上千个 TCP 段都需要发送，这个时候带宽可能会不足。像下图这样，很多个数据封包都需要发送，该如何处理呢？</p>
<p data-nodeid="26051"><img src="https://s0.lgstatic.com/i/image6/M01/3A/67/CioPOWB_iSGAJrYTAAA1X0Gw-4U285.png" alt="Drawing 2.png" data-nodeid="26130"></p>
<h4 data-nodeid="26052">排队（Queuing）</h4>
<p data-nodeid="26053">在这种情况下，通常我们会考虑<strong data-nodeid="26137">排队（Queuing）机制</strong>。</p>
<p data-nodeid="26054"><img src="https://s0.lgstatic.com/i/image6/M00/3A/FA/CioPOWCCKwuAfBn5AABKdgtX54w997.png" alt="image (3).png" data-nodeid="26140"></p>
<p data-nodeid="26055">考虑这样一个模型，如上图所示，在 TCP 层实现一个队列。新元素从队列的一端（左侧）排队，作为一个未发送的数据封包。开始发送的数据封包，从队列的右侧离开。你可以思考一下，这个模型有什么问题吗？</p>
<p data-nodeid="26056">这样做就需要多个队列，我们要将未发送的数据从队列中取出，加入发送中的队列。然后再将发送中的数据，收到 ACK 的部分取出，放入已接收的队列。而发送中的封包，何时收到 ACK 是一件不确定的事情，这样使用队列似乎也有一定的问题。</p>
<h3 data-nodeid="26057">滑动窗口（Sliding Window）</h3>
<p data-nodeid="26058">在上面的模型当中，我们之所以觉得算法不好设计，是因为用错了数据结构。有个说法叫作如果程序写复杂了，那就是写错了。这里其实应该用一种叫作<strong data-nodeid="26149">滑动窗口的数据结构</strong>去实现。</p>
<p data-nodeid="26059"><img src="https://s0.lgstatic.com/i/image6/M00/3A/F2/Cgp9HWCCKxSAROSpAAA_zThgiBA669.png" alt="image (4).png" data-nodeid="26152"></p>
<p data-nodeid="26060">如上图所示：</p>
<ul data-nodeid="26061">
<li data-nodeid="26062">
<p data-nodeid="26063">深绿色代表已经收到 ACK 的段</p>
</li>
<li data-nodeid="26064">
<p data-nodeid="26065">浅绿色代表发送了，但是没有收到 ACK 的段</p>
</li>
<li data-nodeid="26066">
<p data-nodeid="26067">白色代表没有发送的段</p>
</li>
<li data-nodeid="26068">
<p data-nodeid="26069">紫色代表暂时不能发送的段</p>
</li>
</ul>
<p data-nodeid="26070">下面我们重新设计一下不同类型封包的顺序，将已发送的数据放到最左边，发送中的数据放到中间，未发送的数据放到右边。假设我们最多同时发送 5 个封包，也就是窗口大小 = 5。窗口中的数据被同时发送出去，然后等待 ACK。如果一个封包 ACK 到达，我们就将它标记为已接收（深绿色）。</p>
<p data-nodeid="26071">如下图所示，有两个封包的 ACK 到达，因此标记为绿色。</p>
<p data-nodeid="26072"><img src="https://s0.lgstatic.com/i/image6/M00/3A/F2/Cgp9HWCCKxuAeVUyAAA_sW29BSM139.png" alt="image (5).png" data-nodeid="26162"></p>
<p data-nodeid="26073">这个时候滑动窗口可以向右滑动，如下图所示：</p>
<p data-nodeid="26074"><img src="https://s0.lgstatic.com/i/image6/M00/3A/FA/CioPOWCCKyCAMaA7AAA_zxqi_ig808.png" alt="image (6).png" data-nodeid="26166"></p>
<h4 data-nodeid="26075">重传</h4>
<p data-nodeid="26076">如果发送过程中，部分数据没能收到 ACK 会怎样呢？这就可能发生重传。</p>
<p data-nodeid="26077">如果发生下图这样的情况，段 4 迟迟没有收到 ACK。</p>
<p data-nodeid="26078"><img src="https://s0.lgstatic.com/i/image6/M00/3A/F2/Cgp9HWCCKyaAcZwMAABGuK2lrZY271.png" alt="image (7).png" data-nodeid="26172"></p>
<p data-nodeid="26079">这个时候滑动窗口只能右移一个位置，如下图所示：</p>
<p data-nodeid="26080"><img src="https://s0.lgstatic.com/i/image6/M00/3A/FA/CioPOWCCKyuADL6mAABGoEBZ_2Y287.png" alt="image (8).png" data-nodeid="26176"></p>
<p data-nodeid="26081">在这个过程中，如果后来段 4 重传成功（接收到 ACK），那么窗口就会继续右移。如果段 4 发送失败，还是没能收到 ACK，那么接收方也会抛弃段 5、段 6、段 7。这样从段 4 开始之后的数据都需要重发。</p>
<h4 data-nodeid="26082">快速重传</h4>
<p data-nodeid="26083">在 TCP 协议中，如果接收方想丢弃某个段，可以选择不发 ACK。发送端超时后，会重发这个 TCP 段。而有时候，接收方希望催促发送方尽快补发某个 TCP 段，这个时候可以使用<strong data-nodeid="26184">快速重传</strong>能力。</p>
<p data-nodeid="26084">例如段 1、段 2、段 4 到了，但是段 3 没有到。 接收方可以发送多次段 3 的 ACK。如果发送方收到多个段 3 的 ACK，就会重发段 3。这个机制称为<strong data-nodeid="26190">快速重传</strong>。这和超时重发不同，是一种催促的机制。</p>
<p data-nodeid="26085">为了不让发送方误以为段 3 已经收到了，在快速重传的情况下，接收方即便收到发来的段 4，依然会发段 3 的 ACK（不发段 4 的 ACK），直到发送方把段 3 重传。</p>
<h4 data-nodeid="26086">思考：窗口大小的单位是？</h4>
<p data-nodeid="26087">请你思考另一个问题，窗口大小的单位是多少呢？在上面所有的图片中，窗口大小是 TCP 段的数量。<strong data-nodeid="26198">实际操作中，每个 TCP 段的大小不同，限制数量会让接收方的缓冲区不好操作，因此实际操作中窗口大小单位是字节数</strong>。</p>
<h3 data-nodeid="26088">流速控制</h3>
<p data-nodeid="26089"><strong data-nodeid="26204">发送、接收窗口的大小可以用来控制 TCP 协议的流速</strong>。窗口越大，同时可以发送、接收的数据就越多，支持的吞吐量也就越大。当然，窗口越大，如果数据发生错误，损失也就越大，因为需要重传越多的数据。</p>
<p data-nodeid="26090">举个例子：我们用 RTT 表示 Round Trip Time，就是消息一去一回的时间。</p>
<p data-nodeid="26091">假设 RTT = 1ms，带宽是 1mb/s。如果窗口大小为 1kb，那么 1ms 可以发送一个 1kb 的数据（含 TCP 头），1s 就可以发送 1mb 的数据，刚好可以将带宽用满。如果 RTT 再慢一些，比如 RTT = 10ms，那么这样的设计就只能用完 1/10 的带宽。 当然你可以提高窗口大小提高吞吐量，但是实际的模型会比这个复杂，因为还存在重传、快速重传、丢包等因素。</p>
<p data-nodeid="26092">而实际操作中，也不可以真的把带宽用完，所以最终我们会使用折中的方案，在延迟、丢包率、吞吐量中进行选择，毕竟鱼和熊掌不可兼得。</p>
<h3 data-nodeid="26093">总结</h3>
<p data-nodeid="26094">为了提高传输速率，TCP 协议选择将多个段同时发送，为了让这些段不至于被接收方拒绝服务，在发送前，双方要协商好发送的速率。但是我们不可能完全确定网速，所以协商的方式，就变成确定窗口大小。</p>
<p data-nodeid="26095">有了窗口，发送方利用滑动窗口算法发送消息；接收方构造缓冲区接收消息，并给发送方 ACK。滑动窗口的实现只需要数组和少量的指针即可，是一个非常高效的算法。像这种算法，简单又实用，比如求一个数组中最大的连续 k 项和，就可以使用滑动窗口算法。如果你对这个问题感兴趣，不妨用你最熟悉的语言尝试解决一下。</p>
<p data-nodeid="26096">那么，现在你可以尝试来回答本讲关联的面试题目：<strong data-nodeid="26216">滑动窗口和流速控制是怎么回事</strong>？</p>
<p data-nodeid="26097">【<strong data-nodeid="26226">解析</strong>】<strong data-nodeid="26227">滑动窗口是 TCP 协议控制可靠性的核心</strong>。发送方将数据拆包，变成多个分组。然后将数据放入一个拥有滑动窗口的数组，依次发出，仍然遵循先入先出（FIFO）的顺序，但是窗口中的分组会一次性发送。窗口中序号最小的分组如果收到 ACK，窗口就会发生滑动；如果最小序号的分组长时间没有收到 ACK，就会触发整个窗口的数据重新发送。</p>
<p data-nodeid="26098">另一方面，在多次传输中，网络的平均延迟往往是相对固定的，这样 TCP 协议可以通过双方协商窗口大小控制流速。补充下，上面我们说的分组和 TCP 段是一个意思。</p>
<h3 data-nodeid="26099">思考题</h3>
<p data-nodeid="26100"><strong data-nodeid="26234">思考题：既然发送方有窗口，那么接收方也需要有窗口吗</strong>？</p>
