
虚拟局域网（VLAN，全称为 Virtual Local Area Network）是一种网络分段技术，用于在同一个物理网络基础设施上创建多个逻辑上独立的网络。
通过在网络交换机上配置，使得不同VLAN之间的数据通信被隔离，提升了网络的安全性和管理的灵活性,将一个物理的LAN在逻辑上划分成多个广播域的通信技术。
VLAN内的主机间可以直接通信，而VLAN间不能直接通信，从而将广播报文限制在一个VLAN内。

### 为什么需要它 ？

VLAN将一个物理的LAN在逻辑上划分成多个广播域的通信技术。VLAN内的主机间可以直接通信，而VLAN间不能直接通信，从而将广播报文限制在一个VLAN内；
当主机数目较多时会导致冲突严重、广播泛滥、性能显著下降甚至造成网络不可用等问题，通过VLAN可以解决冲突严重的问题，隔离广播报文和提升网络质量；
用VLAN可以划分不同的用户到不同的工作组，同一工作组的用户也不必局限于某一固定的物理范围，网络构建和维护更方便灵活。


#### VLAN 的不足
- VLAN 使用 12-bit 的 VLAN ID，因此第一个不足之处就是最多只支持 4096 个 VLAN 网络
- VLAN 是基于 L2 的，因此很难跨越 L2 的边界，限制了网络的灵活性
- VLAN 的配置需手动介入较多

## VLAN 数据帧格式

- 不带vlan vs VLAN数据帧

![alt text](../tcpip/imgs/image.png)

- 802.1Q vs QinQ  

![alt text](../tcpip/imgs/image-2.png)

QinQ报文比802.1Q报文多四个字节， 实际的汽车场景中使用的改协议的很少很少。

### 字段说明
#### TPID
Tag Protocol Identifier（标签协议标识符），表示数据帧类型。  
- 2Byte
- 0x8100时表示IEEE 802.1Q的VLAN数据帧，如果不支持802.1Q的设备收到这样的帧，会将其丢弃。 
	各设备厂商可以自定义该字段的值。当邻居设备将TPID值配置
- 为非0x8100时， 为了能够识别这样的报文，实现互通，必须在本设备上修改TPID值，确保和邻居设备的TPID值配置一致。

#### PRI
- 3bit	
- Priority，表示数据帧的802.1Q优先级  
取值范围为0～7，值越大优先级越高。当网络阻塞时，设备优先发送优先级高的数据帧。

#### CFI	
- 1bit	
- Canonical Format Indicator（标准格式指示位）：  
	表示MAC地址在不同的传输介质中是否以标准格式进行封装，用于兼容以太网和令牌环网。	CFI取值为0表示MAC地址以标准格式进行封装，为1表示以非标准格式封装。在以太网中，CFI的值为0。

#### VID
- 12bit	
- VLAN ID，表示该数据帧所属VLAN的编号
- VLAN ID取值范围是0～4095。由于0和4095为协议保留取值，所以VLAN ID的有效取值范围是1～4094。

> 设备利用VLAN标签中的VID来识别数据帧所属的VLAN，广播帧只在同一VLAN内转发，这就将广播域限制在一个VLAN内。


在一个VLAN交换网络中，以太网帧主要有以下两种形式：
- 有标记帧（Tagged帧）：加入了4字节VLAN标签的帧。
- 无标记帧（Untagged帧）：原始的、未加入4字节VLAN标签的帧。

常用设备中：

- 用户主机、服务器、Hub只能收发Untagged帧。
- 交换机、路由器和AC既能收发Tagged帧，也能收发Untagged帧。
- 语音终端、AP等设备可以同时收发一个Tagged帧和一个Untagged帧。

为了提高处理效率，设备内部处理的数据帧一律都是Tagged帧。


### 链路类型和接口类型：
设备内部处理的数据帧一律都带有VLAN标签，而现网中的设备有些只会收发Untagged帧，要与这些设备交互，就需要接口能够识别Untagged帧并在收发时给帧添加、剥除VLAN标签。同时，现网中属于同一个VLAN的用户可能会被连接在不同的设备上，且跨越设备的VLAN可能不止一个，如果需要用户间的互通，就需要设备间的接口能够同时识别和发送多个VLAN的数据帧。

为了适应不同的连接和组网，设备定义了Access接口、Trunk接口和Hybrid接口3种接口类型，以及接入链路（Access Link）和干道链路（Trunk Link）两种链路类型。

#### 链路类型
根据链路中需要承载的VLAN数目的不同，以太网链路分为：

- 接入链路

	接入链路只可以承载1个VLAN的数据帧，用于连接设备和用户终端（如用户主机、服务器等）。通常情况下，用户终端并不需要知道自己属于哪个VLAN，也不能识别带有Tag的帧，所以在接入链路上传输的帧都是Untagged帧。

- 干道链路

	干道链路可以承载多个不同VLAN的数据帧，用于设备间互连。为了保证其它网络设备能够正确识别数据帧中的VLAN信息，在干道链路上传输的数据帧必须都打上Tag。

#### 交换机端口类型
根据接口连接对象以及对收发数据帧处理的不同，以太网接口分为：

- Access接口

Access接口一般用于和不能识别Tag的用户终端（如用户主机、服务器等）相连，或者不需要区分不同VLAN成员时使用。
它只能收发Untagged帧，且只能为Untagged帧添加唯一VLAN的Tag。

- Trunk接口

Trunk接口一般用于连接交换机、路由器、AP以及可同时收发Tagged帧和Untagged帧的语音终端。
它可以允许多个VLAN的帧带Tag通过，但只允许一个VLAN的帧从该类接口上发出时不带Tag（即剥除Tag）。

- Hybrid接口

Hybrid接口既可以用于连接不能识别Tag的用户终端（如用户主机、服务器等）和网络设备（如Hub），也可以用于连接交换机、路由器以及可同时收发Tagged帧和Untagged帧的语音终端、AP。
它可以允许多个VLAN的帧带Tag通过，且允许从该类接口发出的帧根据需要配置某些VLAN的帧带Tag（即不剥除Tag）、某些VLAN的帧不带Tag（即剥除Tag）。

Hybrid接口和Trunk接口在很多应用场景下可以通用，但在某些应用场景下，必须使用Hybrid接口。比如一个接口连接不同VLAN网段的场景中，因为一个接口需要给多个Untagged报文添加Tag，所以必须使用Hybrid接口。


#### 缺省VLAN

缺省VLAN又称PVID（Port Default VLAN ID）。前面提到，设备处理的数据帧都带Tag，当设备收到Untagged帧时，就需要给该帧添加Tag，添加什么Tag，就由接口上的缺省VLAN决定。

接口收发数据帧时，对Tag的添加或剥除过程。

对于Access接口，缺省VLAN就是它允许通过的VLAN，修改缺省VLAN即可更改接口允许通过的VLAN。
对于Trunk接口和Hybrid接口，一个接口可以允许多个VLAN通过，但是只能有一个缺省VLAN。接口的缺省VLAN和允许通过的VLAN需要分别配置，互不影响

| 接口类型 | 对接收不带Tag的报文处理                                                                                                                    | 对接收带Tag的报文处理                                                                                 | 发送帧处理过程                                                                                                                                                |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Access接口 | 接收该报文，并打上缺省的VLAN ID。                                                                                                       | 当VLAN ID与缺省VLAN ID相同时，接收该报文。当VLAN ID与缺省VLAN ID不同时，丢弃该报文。 | 先剥离帧的PVID Tag，然后再发送。                                                                                                                         |
| Trunk接口 | 打上缺省的VLAN ID，当缺省VLAN ID在允许通过的VLAN ID列表里时，接收该报文。打上缺省的VLAN ID，当缺省VLAN ID不在允许通过的VLAN ID列表里时，丢弃该报文。 | 当VLAN ID在接口允许通过的VLAN ID列表里时，接收该报文。当VLAN ID不在接口允许通过的VLAN ID列表里时，丢弃该报文。 | 当VLAN ID与缺省VLAN ID相同，且是该接口允许通过的VLAN ID时，去掉Tag，发送该报文。当VLAN ID与缺省VLAN ID不同，且是该接口允许通过的VLAN ID时，保持原有Tag，发送该报文。 |
| Hybrid接口 | 打上缺省的VLAN ID，当缺省VLAN ID在允许通过的VLAN ID列表里时，接收该报文。打上缺省的VLAN ID，当缺省VLAN ID不在允许通过的VLAN ID列表里时，丢弃该报文。 | 当VLAN ID在接口允许通过的VLAN ID列表里时，接收该报文。当VLAN ID不在接口允许通过的VLAN ID列表里时，丢弃该报文。 | 当VLAN ID是该接口允许通过的VLAN ID时，发送该报文。可以通过命令设置发送时是否携带Tag。                                              |

- 当接收到不带VLAN标签的数据帧时，Access接口、Trunk接口、Hybrid接口都会给数据帧打上VLAN标签，但Trunk接口、Hybrid接口会根据数据帧的VID是否为其允许通过的VLAN来判断是否接收，而Access接口则无条件接收。

- 当接收到带VLAN标签的数据帧时，Access接口、Trunk接口、Hybrid接口都会根据数据帧的VID是否为其允许通过的VLAN（Access接口允许通过的VLAN就是缺省VLAN）来判断是否接收。

- 当发送数据帧时：
	- Access接口直接剥离数据帧中的VLAN标签。
	- Trunk接口只有在数据帧中的VID与接口的PVID相等时才会剥离数据帧中的VLAN标签。
	- Hybrid接口会根据接口上的配置判断是否剥离数据帧中的VLAN标签。

因此，Access接口发出的数据帧肯定不带Tag，Trunk接口发出的数据帧只有一个VLAN的数据帧不带Tag，其他都带VLAN标签，Hybrid接口发出的数据帧可根据需要设置某些VLAN的数据帧带Tag，某些VLAN的数据帧不带Tag。

### VLAN 通信

#### VLAN内互访
同一VLAN内用户互访（简称VLAN内互访）会经过如下三个环节。

1. 用户主机的报文转发

	源主机在发起通信之前，会将自己的IP与目的主机的IP进行比较，如果两者位于同一网段，会获取目的主机的MAC地址，并将其作为目的MAC地址封装进报文；如果两者位于不同网段，源主机会将报文递交给网关，获取网关的MAC地址，并将其作为目的MAC地址封装进报文。

2. 设备内部的以太网交换

- 如果目的MAC地址+VID匹配自己的MAC表且三层转发标志置位，则进行三层交换，会根据报文的目的IP地址查找三层转发表项，如果没有找到会将报文上送CPU，由CPU查找路由表实现三层转发。

- 如果目的MAC地址+VID匹配自己的MAC表但三层转发标志未置位，则进行二层交换，会直接将报文根据MAC表的出接口发出去。

- 如果目的MAC地址+VID没有匹配自己的MAC表，则进行二层交换，此时会向所有允许VID通过的接口广播该报文，以获取目的主机的MAC地址。

3. 设备之间交互时，VLAN标签的添加和剥离

	设备内部的以太网交换都是带Tag的，为了与不同设备进行成功交互，设备需要根据接口的设置添加或剥除Tag。不同接口VLAN标签添加和剥离情况不同。

从以太网交换原理可以看出，划分VLAN后，广播报文只在同一VLAN内二层转发，因此同一VLAN内的用户可以直接二层互访。
根据属于同一VLAN的主机是否连接在不同的设备，VLAN内互访有两种场景：同设备VLAN内互访和跨设备VLAN内互访。

#### VLAN间互访

划分VLAN后，由于广播报文只在同VLAN内转发，所以不同VLAN的用户间不能二层互访，这样能起到隔离广播的作用。但实际应用中，不同VLAN的用户又常有互访的需求，此时就需要实现不同VLAN的用户互访，简称VLAN间互访。

同VLAN间互访一样，VLAN间互访也会经过用户主机的报文转发、设备内部的以太网交换、设备之间交互时VLAN标签的添加和剥离三个环节。同样，根据以太网交换原理，广播报文只在同一VLAN内转发，不同VLAN内的用户则不能直接二层互访，需要借助三层路由技术或VLAN转换技术才能实现互访。

#### 一些其他的场景
- 跨设备VLAN间互访
- 同设备VLAN间互访
- VLAN间互访技
- 跨设备VLAN内互访
- 同设备VLAN内互访


### 常见的划分方式
1. 基于接口的划分方式：就是静态的把指定的接口划分到对应的VLAN内，那么它就固定在这个VLAN下了。车内最常用的一种。
2. 基于MAC地址划分VLAN：它只看用户的MAC地址，不把接口固定在某个VLAN下，当该接口收到一个源MAC为匹配的，就动态划分到对应的VLAN内。
3. 基于子网形式划分VLAN：
	它只看用户的IP子网形式，比如规定一个192.168.1.0/24的网段划分到VLAN 20，那么配置了该网段的PC连接的接口就会动态划分到VLAN 20。
4. 基于协议划分：这种比较特殊，它能基于IPV4、IPV6、二层以太网的形式来划分，用的比较少


## 协议标准

虚拟局域网（VLAN）的实现主要依赖于IEEE 802.1Q标准，但它也涉及其他相关的协议和RFC。以下是与VLAN相关的主要协议标准和RFC：

### IEEE 标准
#### IEEE 802.1Q Virtual LANs

该标准定义了在以太网帧中插入VLAN标签的机制，以及VLAN的标识和数据隔离方法。

主要内容: 
- Tag Protocol Identifier (TPID)
- Priority Code Point (PCP)
- Drop Eligible Indicator (DEI)
- VLAN Identifier (VID)


#### IEEE 802.1p:
Traffic Class Expediting and Dynamic Multicast Filtering

该标准定义了VLAN帧中的优先级字段，用于服务质量（QoS）的实现。

主要内容: 
- 优先级标记
- 服务质量管理

#### IEEE 802.1ad:
标题: Provider Bridges (Q-in-Q)
描述: 该标准定义了服务提供商桥接技术，通过在帧中嵌套多个VLAN标签来实现二级VLAN标识。
主要内容: Q-in-Q技术，双层VLAN标记。

#### IEEE 802.1AB:
Station and Media Access Control Connectivity Discovery (LLDP)

该标准定义了链路层发现协议（LLDP），用于发现和管理网络拓扑。

主要内容: 
设备邻居信息的发现和管理。

作用：
- 限制广播域：广播域被限制在一个VLAN内，节省了带宽，提高了网络处理能力。
- 增强局域网的安全性：不同VLAN内的报文在传输时是相互隔离的，即一个VLAN内的用户不能和其它VLAN内的用户直接通信。
- 提高了网络的健壮性：故障被限制在一个VLAN内，本VLAN内的故障不会影响其他VLAN的正常工作。
- 灵活构建虚拟工作组：用VLAN可以划分不同的用户到不同的工作组，同一工作组的用户也不必局限于某一固定的物理范围，网络构建和维护更方便灵活。

#### 相关RFCs
##### RFC 5517:
Cisco Systems' Private VLANs: Scalable Security in a Multi-Client Environment

该RFC描述了私有VLAN（PVLAN）的概念和实现方法，用于进一步增强VLAN的安全性和隔离性。

主要内容: 
- 社区PVLAN
- 隔离PVLAN
- 主PVLAN的配置和应用

##### RFC 4545:
Definitions of Managed Objects for Virtual LAN (VLAN) Bridge Management

该RFC定义了用于管理VLAN桥接设备的管理信息库（MIB）

主要内容: 
- VLAN桥接设备的管理对象和操作方法。

##### RFC 4363:
Definitions of Managed Objects for Bridges with Traffic Classes, Multicast Filtering, and Virtual LAN Extensions

该RFC扩展了用于VLAN和多播过滤的桥接管理对象的定义。

主要内容: 
- 支持VLAN和多播过滤的桥接设备的管理对象

##### RFC 4675:
RADIUS Attributes for Virtual LAN and Priority Support

该RFC定义了用于RADIUS协议的VLAN和优先级支持的属性。

主要内容:
- RADIUS服务器和客户端之间的VLAN和优先级信息交换。


