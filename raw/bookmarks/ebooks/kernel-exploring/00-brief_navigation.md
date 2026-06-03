# nvdimm初探

最近研究nvdimm，发现这玩意还真有点复杂。

简单记录之。

## 使用手册

写了一半发现得先写个使用手册，这样一来自己做个记录，二来也清楚正常使用流程，三来部分内容可以帮助解释代码。

所以加一个[使用手册](/kernel-exploring/00-brief_navigation/00-brief_user_guide.md)

## 上帝视角

经过了设备模型的洗礼，那就先从总线，驱动和设备角度看看都有些什么。

[上帝视角](/kernel-exploring/00-brief_navigation/01-a_big_picture.md)

## nvdimm_bus

首先创建的是nvdimm_bus设备，而且从树形结构中可以看到它是nvdimm设备树的根。

[nvdimm_bus](/kernel-exploring/00-brief_navigation/02-nvdimm_bus.md)

## nvdimm

在整个设备树中，有一个孤零零的存在:nvdimm。这就是用来表示物理dimm设备的。

[nvdimm](/kernel-exploring/00-brief_navigation/03-nvdimm.md)

## nd_region

接着我们就来看nvdimm_bus下，另一个子树。而这颗子树的根就是nd_region了。

[nd_region](/kernel-exploring/00-brief_navigation/04-nd_region.md)

而在nd_region下，有四个并列的设备：

* [nd_namespace_X](/kernel-exploring/00-brief_navigation/05-namespace.md)
* [nd_btt](https://github.com/RichardWeiYang/kernel_exploring/blob/master/nvdimm/06-btt.md)
* [nd_pfn](https://github.com/RichardWeiYang/kernel_exploring/blob/master/nvdimm/08-pfn.md)
* [nd_dax](/kernel-exploring/00-brief_navigation/07-dax.md)

## dev_dax

在着重描述了namespace和nd_dax后，终于要到整个驱动的最后也就是[dev_dax](/kernel-exploring/00-brief_navigation/07-dax/09-dev_dax.md)。

这是用户使用nd_dax设备的接口。