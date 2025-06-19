<p data-nodeid="1429" class="">TCP 和 UDP 是今天应用最广泛的传输层协议，拥有最核心的垄断地位。今天互联网的整个传输层，几乎都是基于这两个协议打造的。无论是应用开发、框架设计选型、做底层和优化，还是定位线上问题，只要碰到网络，就逃不开 TCP 协议相关的知识。在面试中 <strong data-nodeid="1543">TCP</strong> 一直是一个高频考察内容，外加 TCP 关联的知识比较多，因此面试题五花八门。</p>
<p data-nodeid="1430">在介绍今天的主题之前，我先提一道高频面试题：<strong data-nodeid="1548">TCP 协议为什么握手是 3 次，挥手却是 4 次？下面请你带着这个问题，开启今天的学习。</strong></p>
<h3 data-nodeid="1431">TCP 协议</h3>
<p data-nodeid="1432">要想把开篇这道面试题回答得漂亮，我们有必要先说一下概念，然后我再逐字给你解读。</p>
<p data-nodeid="1433"><strong data-nodeid="1555">TCP（Transport Control Protocol）是一个传输层协议，提供 Host-To-Host 数据的可靠传输，支持全双工，是一个连接导向的协议</strong>。</p>
<p data-nodeid="1434">这里面牵涉很多概念，比如主机到主机、连接、会话、双工/单工及可靠性等，接下来我会为你逐一解释。</p>
<h4 data-nodeid="1435">主机到主机（Host-To-Host）</h4>
<p data-nodeid="1436"><strong data-nodeid="1562">TCP 提供的是 Host-To-Host 传输，一台主机通过 TCP 发送数据给另一台主机</strong>。这里的主机（Host）是一个抽象的概念，可以是手机、平板、手表等。收发数据的设备都是主机，所以双方是平等的。</p>
<p data-nodeid="1437"><img src="https://s0.lgstatic.com/i/image6/M00/38/6D/Cgp9HWB5RAmAZRwzAACtAP-CPWs242.png" alt="Drawing 1.png" data-nodeid="1565"></p>
<p data-nodeid="1438"><strong data-nodeid="1570">TCP 协议往上是应用到应用（Application-To-Application）的协议</strong>。什么是应用到应用的协议呢？比如你用微信发信息给张三，你的微信客户端、微信聊天服务都是应用。微信有自己的聊天协议，微信的聊天协议是应用到应用的协议；如果微信的聊天协议想要工作，就需要一个主机到主机的协议帮助它实现通信。</p>
<p data-nodeid="1439">而 TCP 上层有太多的应用，不仅仅有微信，还有原神、抖音、网易云音乐……因此 TCP 上层的应用层协议使用 TCP 能力的时候，需要告知 TCP 是哪个应用——这就是<strong data-nodeid="1580">端口号</strong>。<strong data-nodeid="1581">端口号用于区分应用</strong>，下文中我们还会详细讨论。</p>
<p data-nodeid="1440">TCP 要实现主机到主机通信，就需要知道主机们的<strong data-nodeid="1587">网络地址（IP 地址）</strong>，但是 TCP 不负责实际地址到地址（Address-To-Address）的传输，因此 TCP 协议把 IP 地址给底层的互联网层处理。</p>
<p data-nodeid="3961" class=""><strong data-nodeid="3970">互联网层，也叫网络层（Network Layer），提供地址到地址的通信</strong>，IP 协议就在这一层工作。互联网层解决地址到地址的通信，但是不负责信号在具体两个设备间传递。因此，网络层会调用下方的<strong data-nodeid="3971">链路层</strong>在两个相邻设备间传递信息。当信号在两个设备间传递的时候，科学家又设计出了物理层封装最底层的物理设备、传输介质等，由最下方的物理层提供最底层的传输能力。</p>




<p data-nodeid="1442">以上的 5 层架构，我们称为<strong data-nodeid="1611">互联网协议群</strong>，也称作 <strong data-nodeid="1612">TCP/IP 协议群</strong>。<strong data-nodeid="1613">总结下，主机到主机（Host-To-Host）为应用提供应用间通信的能力</strong>。</p>
<h4 data-nodeid="1443">什么是连接和会话？</h4>
<p data-nodeid="1444">下一个关联的概念是<strong data-nodeid="1620">连接（Connection）——连接是数据传输双方的契约</strong>。</p>
<p data-nodeid="1445">连接是通信双方的一个约定，目标是让两个在通信的程序之间产生一个默契，保证两个程序都在线，而且尽快地响应对方的请求，这就是<strong data-nodeid="1626">连接（Connection）</strong>。</p>
<p data-nodeid="1446">设计上，连接是一种传输数据的行为。传输之前，建立一个连接。具体来说，数据收发双方的内存中都建立一个用于维护数据传输状态的对象，比如双方 IP 和端口是多少？现在发送了多少数据了？状态健康吗？传输速度如何？等。所以，<strong data-nodeid="1632">连接是网络行为状态的记录</strong>。</p>
<p data-nodeid="1447">和连接关联的还有一个名词，叫作<strong data-nodeid="1638">会话（Session），会话是应用的行为</strong>。比如微信里张三和你聊天，那么张三和你建立一个会话。你要和张三聊天，你们创建一个聊天窗口，这个就是会话。你开始 Typing，开始传输数据，你和微信服务器间建立一个连接。如果你们聊一段时间，各自休息了，约定先不要关微信，1 个小时后再回来。那么连接会断开，因为聊天窗口没关，所以会话还在。</p>
<p data-nodeid="1448">在有些系统设计中，会话会自动重连（也就是重新创建连接），或者帮助创建连接。 此外，会话也负责在多次连接中保存状态，比如 HTTP Session 在多次 HTTP 请求（连接）间保持状态（如用户信息）。</p>
<p data-nodeid="1449"><strong data-nodeid="1644">总结下，会话是应用层的概念，连接是传输层的概念</strong>。</p>
<h4 data-nodeid="1450">双工/单工问题</h4>
<p data-nodeid="1451">接下来我们聊聊什么是<strong data-nodeid="1651">双工/单工</strong>。</p>
<p data-nodeid="1452">在任何一个时刻，如果数据只能单向发送，就是<strong data-nodeid="1665">单工</strong>，所以单工需要至少一条线路。如果在某个时刻数据可以向一个方向传输，也可以向另一个方向反方向传输，而且交替进行，叫作<strong data-nodeid="1666">半双工</strong>；半双工需要至少 1 条线路。最后，如果任何时刻数据都可以双向收发，这就是<strong data-nodeid="1667">全双工</strong>，全双工需要大于 1 条线路。当然这里的线路，是一个抽象概念，你可以并发地处理信号，达到模拟双工的目的。</p>
<p data-nodeid="1453"><strong data-nodeid="1676">TCP 是一个双工协议，数据任何时候都可以双向传输</strong>。这就意味着客户端和服务端可以平等地发送、接收信息。正因为如此，客户端和服务端在 TCP 协议中有一个平等的名词——<strong data-nodeid="1677">Host（主机）</strong>。</p>
<h4 data-nodeid="1454">什么是可靠性？</h4>
<p data-nodeid="1455">上文提到 TCP 提供可靠性，那么可靠性是什么？</p>
<p data-nodeid="1456"><strong data-nodeid="1688">可靠性指数据保证无损传输</strong>。如果发送方按照顺序发送，然后数据无序地在网络间传递，就必须有一种算法在接收方将数据恢复原有的顺序。另外，如果发送方同时要把消息发送给多个接收方，这种情况叫作<strong data-nodeid="1689">多播</strong>，可靠性要求每个接收方都无损收到相同的副本。多播情况还有强可靠性，就是如果有一个消息到达任何一个接收者，那么所有接受者都必须收到这个消息。说明一下，本专栏中，我们都是基于单播讨论可靠性。</p>
<h3 data-nodeid="1457">TCP 的握手和挥手</h3>
<p data-nodeid="1458">TCP 是一个连接导向的协议，设计有建立连接（握手）和断开连接（挥手）的过程。TCP 没有设计会话（Session），因为会话通常是一个应用的行为。</p>
<h4 data-nodeid="1459">TCP 协议的基本操作</h4>
<p data-nodeid="1460">TCP 协议有这样几个基本操作：</p>
<ul data-nodeid="1461">
<li data-nodeid="1462">
<p data-nodeid="1463">如果一个 Host 主动向另一个 Host 发起连接，称为 SYN（Synchronization），请求同步；</p>
</li>
<li data-nodeid="1464">
<p data-nodeid="1465">如果一个 Host 主动断开请求，称为 FIN（Finish），请求完成；</p>
</li>
<li data-nodeid="1466">
<p data-nodeid="1467">如果一个 Host 给另一个 Host 发送数据，称为 PSH（Push），数据推送。</p>
</li>
</ul>
<p data-nodeid="1468">以上 3 种情况，接收方收到数据后，都需要给发送方一个 ACK（Acknowledgement）响应。请求/响应的模型是可靠性的要求，如果一个请求没有响应，发送方可能会认为自己需要重发这个请求。</p>
<h4 data-nodeid="1469">建立连接的过程（三次握手）</h4>
<p data-nodeid="1470">因为要保持连接和可靠性约束，TCP 协议要保证每一条发出的数据必须给返回，返回数据叫作 ACK（也就是响应）。</p>
<p data-nodeid="1471">按照这个思路，你可以看看建立连接是不是需要 3 次握手：</p>
<p data-nodeid="1472"><img src="https://s0.lgstatic.com/i/image6/M00/3A/20/CioPOWB-RYSASfPkAAEen4ZR3gw297.png" alt="619.png" data-nodeid="1703"></p>
<ol data-nodeid="1473">
<li data-nodeid="1474">
<p data-nodeid="1475">客户端发消息给服务端（SYN）</p>
</li>
<li data-nodeid="1476">
<p data-nodeid="1477">服务端准备好进行连接</p>
</li>
<li data-nodeid="1478">
<p data-nodeid="1479">服务端针对客户端的 SYN 给一个 ACK</p>
</li>
</ol>
<p data-nodeid="1480">你可以能会问，到这里不就可以了吗？2 次握手就足够了。但其实不是，因为服务端还没有确定客户端是否准备好了。比如步骤 3 之后，服务端马上给客户端发送数据，这个时候客户端可能还没有准备好接收数据。因此还需要增加一个过程。</p>
<p data-nodeid="1481">接下来还会发生以下操作：</p>
<ol start="4" data-nodeid="1482">
<li data-nodeid="1483">
<p data-nodeid="1484">服务端发送一个 SYN 给客户端</p>
</li>
<li data-nodeid="1485">
<p data-nodeid="1486">客户端准备就绪</p>
</li>
<li data-nodeid="1487">
<p data-nodeid="1488">客户端给服务端发送一个 ACK</p>
</li>
</ol>
<p data-nodeid="1489">你可能会问，上面不是 6 个步骤吗？ 怎么是 3 次握手呢？下面我们一起分析一下其中缘由。</p>
<ul data-nodeid="1490">
<li data-nodeid="1491">
<p data-nodeid="1492">步骤 1 是 1 次握手；</p>
</li>
<li data-nodeid="1493">
<p data-nodeid="1494">步骤 2 是服务端的准备，不是数据传输，因此不算握手；</p>
</li>
<li data-nodeid="1495">
<p data-nodeid="1496">步骤 3 和步骤 4，因为是同时发生的，可以合并成一个 SYN-ACK 响应，作为一条数据传递给客户端，因此是第 2 次握手；</p>
</li>
<li data-nodeid="1497">
<p data-nodeid="1498">步骤 5 不算握手；</p>
</li>
<li data-nodeid="1499">
<p data-nodeid="1500">步骤 6 是第 3 次握手。</p>
</li>
</ul>
<p data-nodeid="1501">为了方便你理解步骤 3 和步骤 4，这里我画了一张图。可以看到下图中 SYN 和 ACK 被合并了，因此建立连接一共需要 3 次握手，过程如下图所示：</p>
<p data-nodeid="1502"><img src="https://s0.lgstatic.com/i/image6/M00/38/6D/Cgp9HWB5RCqAVfhiAADJmfGn2O0616.png" alt="Drawing 4.png" data-nodeid="1721"></p>
<p data-nodeid="1503">从上面的例子中，你可以进一步思考 SYN、ACK、PSH 这些常见的标识位（Flag）在传输中如何表示。</p>
<p data-nodeid="1504">一种思路是为 TCP 协议增加协议头。在协议头中取多个位（bit），其中 SYN、ACK、PSH 都占有 1 个位。比如 SYN 位，1 表示 SYN 开启，0 表示关闭。因此，SYN-ACK 就是 SYN 位和 ACK 位都置 1。这种设计，我们也称为<strong data-nodeid="1734">标识（Flag）</strong>。标识位是放在 TCP 头部的，关于标识位和 TCP 头的内容，我会在“<a href="https://kaiwu.lagou.com/course/courseInfo.htm?courseId=837#/detail/pc?id=7268" data-nodeid="1732">04 | TCP 的稳定性：滑动窗口和流速控制是怎么回事？</a>”中详细介绍。</p>
<h4 data-nodeid="1505">断开连接的过程（4 次挥手）</h4>
<p data-nodeid="1506">继续上面的思路，如果断开连接需要几次握手？给你一些提示，你可以在脑海中这样构思。</p>
<ol data-nodeid="1507">
<li data-nodeid="1508">
<p data-nodeid="1509">客户端要求断开连接，发送一个断开的请求，这个叫作（FIN）。</p>
</li>
<li data-nodeid="1510">
<p data-nodeid="1511">服务端收到请求，然后给客户端一个 ACK，作为 FIN 的响应。</p>
</li>
<li data-nodeid="1512">
<p data-nodeid="1513">这里你需要思考一个问题，<strong data-nodeid="1746">可不可以像握手那样马上传 FIN 回去</strong>？<br>
其实这个时候服务端不能马上传 FIN，因为断开连接要处理的问题比较多，比如说服务端可能还有发送出去的消息没有得到 ACK；也有可能服务端自己有资源要释放。因此断开连接不能像握手那样操作——将两条消息合并。所以，服务端经过一个等待，确定可以关闭连接了，再发一条 FIN 给客户端。</p>
</li>
<li data-nodeid="1514">
<p data-nodeid="1515">客户端收到服务端的 FIN，同时客户端也可能有自己的事情需要处理完，比如客户端有发送给服务端没有收到 ACK 的请求，客户端自己处理完成后，再给服务端发送一个 ACK。</p>
</li>
</ol>
<p data-nodeid="1516">经过以上分析，就可以回答上面这个问题了。是不是刚刚好 4 次挥手？过程如下图所示：</p>
<p data-nodeid="1517"><img src="https://s0.lgstatic.com/i/image6/M00/3D/55/CioPOWCTwu-AD9PgAABp1yJqsPI439.png" alt="图片2.png" data-nodeid="1751"></p>
<h4 data-nodeid="1518">总结</h4>
<p data-nodeid="1519">在学习 3 次握手、4 次挥手时，你一定要理解为什么这么设计，而不是死记硬背。最后。我们一起总结一下今天的重点知识。</p>
<ol data-nodeid="1520">
<li data-nodeid="1521">
<p data-nodeid="1522">TCP 提供连接（Connection），让双方的传输更加稳定、安全。</p>
</li>
<li data-nodeid="1523">
<p data-nodeid="1524">TCP 没有直接提供会话，因为应用对会话的需求多种多样，比如聊天程序会话在保持双方的聊天记录，电商程序会话在保持购物车、订单一致，所以会话通常在 TCP 连接上进一步封装，在应用层提供。</p>
</li>
<li data-nodeid="1525">
<p data-nodeid="1526">TCP 是一个面向连接的协议（Connection -oriented Protocol），说的就是 TCP 协议参与的双方（Host）在收发数据之前会先建立连接。后面我们还会学习 UDP 协议，UDP 是一个面向报文（Datagram-oriented）的协议——协议双方不需要建立连接，直接传送报文（数据）。</p>
</li>
<li data-nodeid="1527">
<p data-nodeid="1528">最后，连接需要消耗更多的资源。比如说，在传输数据前，必须先协商建立连接。因此，不是每种场景都应该用连接导向的协议。像视频播放的场景，如果使用连接导向的协议，服务端每向客户端推送一帧视频，客户端都要给服务端一次响应，这是不合理的。</p>
</li>
</ol>
<p data-nodeid="1529"><strong data-nodeid="1761">那么通过这一讲的学习，你现在可以尝试来回答本讲关联的面试题目：TCP 为什么是 3 次握手，4 次挥手？</strong></p>
<p data-nodeid="1530">【<strong data-nodeid="1767">解析</strong>】TCP 是一个双工协议，为了让双方都保证，建立连接的时候，连接双方都需要向对方发送 SYC（同步请求）和 ACK（响应）。</p>
<p data-nodeid="1531">握手阶段双方都没有烦琐的工作，因此一方向另一方发起同步（SYN）之后，另一方可以将自己的 ACK 和 SYN 打包作为一条消息回复，因此是 3 次握手——需要 3 次数据传输。</p>
<p data-nodeid="1532">到了挥手阶段，双方都可能有未完成的工作。收到挥手请求的一方，必须马上响应（ACK），表示接收到了挥手请求。<strong data-nodeid="1774">类比现实世界中，你收到一个 Offer，出于礼貌你先回复考虑一下，然后思考一段时间再回复 HR 最后的结果</strong>。最后等所有工作结束，再发送请求中断连接（FIN），因此是 4 次挥手。</p>
<h3 data-nodeid="1533">思考题</h3>
<p data-nodeid="1534"><strong data-nodeid="1780">思考题：一台内存在 8G 左右的服务器，可以同时维护多少个连接</strong>？</p>
