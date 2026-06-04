---
type: source
source-type: slide
title: "王志宏_从原型到生产：LazyLLM的三阶段架构演化实践"
path: slides/王志宏_从原型到生产：LazyLLM的三阶段架构演化实践.pdf
source-md5: 7f3a17b2349007e22bdeda2496f13fc0
size: 8940 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 王志宏_从原型到生产：LazyLLM的三阶段架构演化实践

> Ingested from `slides/王志宏_从原型到生产：LazyLLM的三阶段架构演化实践.pdf` via `lit parse` on 2026-06-04.
> Source file: 8.73 MB.

## Page 1

_(no text content on this page)_

## Page 2

_(no text content on this page)_

## Page 3

_(no text content on this page)_

## Page 4

_(no text content on this page)_

## Page 5

_(no text content on this page)_

## Page 6

LazyLLM 的三阶段架构演化实践
商汤科技 大装置事业群 研发总监 王志宏

## Page 7

       背景：为什么大模型应用框架需要重新设计
       01
       功能优先 - 以模块化体系构建 Agent 的“构件库”
       02
目录     易用为本 - 从架构抽象到开发者体验
       03
       性能致胜 - 从Python 到 C++ 混合编程的架构跃迁
       04
       架构演进的原则与经验总结
       05

## Page 8

 目录
以大模型为核心的AI技术取得突破，推动从通用生成能力到行业特定能力的全     褒贬不一的评价
面升级。大模型引领的AI风潮正席卷全球，推动各行业迈入智能化新阶段。
目前纯大模型及微调无法满足实际的场景需求，AI Agent俨然成为2025年最中
心的产品议题。相关数据显示，整体AI Agent 市场规模在2025年将达到73.8亿美
元，到2030年达到470亿美元。
优秀的开源工具
应用开发框架
LangChain / AutoGen / AutoGPT /
LangGraph / …
RAG开发框架
LLamaIndex / RagFlow / …
拖拽编排平台      在实际案例方面，AI Agent能作用于各种广泛领域，包括电商、财管等多种领域，
Dify / Flowise / Coze /…       根据相关调研，九成公司都对 AI Agent 有计划和需求，大约 51% 的受访者已在
     生产中使用，78% 的受访者积极计划尽快将代理投入生产。

## Page 9

从 Demo 到生产的落地鸿沟

Ø  系统响应要快    快      准     Ø  召回内容要准
Ø  问题定位要快                 Ø  回答结果要对
Ø  更新部署要快                 Ø  权限管理要清
                企业对应用
Ø  用户数量要多       的核心需求     Ø  系统运行要稳
Ø  数据规模要大                 Ø  系统升级要平
Ø  应用范围要广    众      稳     Ø  监控日志要全

## Page 10

    用可演进的方式构建一个框架，而不是“一次性工程”








       需求驱动                 分层清晰
从真实业务需求出发，而非预设最终形态，  通过合理分层隔离复杂度，使各层职责明
  让框架始终服务实际应用场景。      确、可独立演进、可随时替换和优化。









       架构开放        适度设计
保持模块可插拔、可扩展，让不同业务和 避免超前抽象与复杂封装，以最小必要方
   未来能力能够自然融入体系。   案起步，确保后续可持续演化与优化。

## Page 11

       背景：为什么大模型应用框架需要重新设计
       01
       功能优先 - 以模块化体系构建 Agent 的“构件库”
       02
目录     易用为本 - 从架构抽象到开发者体验
       03
       性能致胜 - 从Python 到 C++ 混合编程的架构跃迁
       04
       架构演进的原则与经验总结
       05

## Page 12

    大模型开发者的需求是什么？
    开发者的需求，就是最高效率地满足用户的需求
           知识库（企业智库）     智能写作（报告/合同/总结）
希望快速、准确地从海量文档中获取答案，用     用户希望 AI 根据模板 + 背景资料自动生成高
   于内部知识库、政策查询、产品说明等     质量文本，如周报、标书、企划案、合同草稿。



            智能客服 / 智能工单     智慧问答（含互联网搜索）
用户希望降低人工客服成本，让 AI 处理咨询、     用户希望比自己去搜索引擎搜索能得到更准确、
    售后、FAQ，并能自动生成/流转工单。     更直接、更系统的回答


         ChatBI（自然语言分析数据）     智能质检与审核（文本/代码/文档）
用户不懂 SQL 也能分析业务数据，让 AI 自动     用户需要 AI 自动检测错误、补全描述、给修改建
          读库、生成图表、解释指标变化。     议，例如质量审核、代码 review、文档校验。

## Page 13

    知识库技术拆解










      文档解析               模型调用                检索召回           流程编排
 将多格式原始资料结构化抽取，完    统一管理本地与在线大模型的推理    基于向量、关键词或混合检索，从知     将解析、检索、生成等步骤按任务逻
成分片、清洗、向量化前的预处理，    接口，支持参数控制、重试和流式    识库中精准找到相关内容，为生成回     辑组合，实现可配置、可扩展、可监
  为后续检索奠定高质量基础      输出，确保生成过程稳定高效。       答提供可靠且可追溯的证据。      控的端到端 RAG 工作流。

## Page 14

其他技术拆解







•   模型调用
•   Prompt
•   数据库
•   工具调用
•   工具集
•   召回检索
•   … …

## Page 15

  LazyLLM功能架构
   解析    RAG     生成         审核  ChatBI  搜索问答   … …       应用层
   服务                       数据流
   模型    文本解析    模型调用   工具调用    召回检索    重排序    数据库调用     功能层
平台
MCP 模型调用管理 工具管理 检索管理 文档管理 数据库管理 资源层
工具
         训推框架接入         工具接入    知识库            关系型       适配层
                            数据库接入     数据库接入

       推理框架    训练框架     本地工具集   文档      向量     关系型       基础层
                            数据库     数据库        数据库

         部署的中间件         云服务     用户应用    框架组件

## Page 16

LazyLLM功能架构设计原则


模块化：架构可控                               适配层：替换灵活

Ø 模块边界清晰透明，使整体结构更易理解与统一管理，降低系统复杂度。     Ø 通过适配层隔离差异，使底层模型或能力替换时无需影响上层逻辑。
Ø 依赖关系明确可控，有助于在技术快速演化中保持架构稳定与一致。       Ø 支持按业务需求快速切换实现方案，保证系统持续演进的灵活度。
Ø 各模块职责单一可追踪，提升问题定位效率并减少维护成本风险。        Ø 新增能力可平滑接入，减少接入成本并缩短整体功能交付周期。
Ø 架构变化可逐层推进，避免全局重构带来的成本与不可控性。          Ø 降低耦合带来未来扩展空间，使系统能持续适配不同技术环境。



资源层：复用增强                               功能层：编排随心

Ø 通用资源模块沉淀为能力库，实现跨项目、多场景高复用率。          Ø 功能模块颗粒度清晰，可按任务需求自由组合生成不同算法应用。
Ø 减少重复造轮子，显著降低人力投入并提升整体交付效率。           Ø 支持复杂任务的多步骤编排，使业务逻辑更灵活且调整成本更低。
Ø 统一的资源标准提升协作一致性，让团队在大型项目中更稳定协同。       Ø 可在不改动核心能力的前提下优化流程，实现快速响应变化需求。
Ø 抽象出的共享资源可长期维护升级，形成持续积累的核心资产。         Ø 便于工作流算法接入与替换，构建多样化、可实验性的流程体系。

## Page 17

       背景：为什么大模型应用框架需要重新设计
       01
       功能优先 - 以模块化体系构建 Agent 的“构件库”
       02
目录     易用为本 - 从架构抽象到开发者体验
       03
       性能致胜 - 从Python 到 C++ 混合编程的架构跃迁
       04
       架构演进的原则与经验总结
       05

## Page 18

为什么易用性是重中之重

    开发低效               调试困难

• 新人难理解框架结构，入门周期显著拉长   • 错误难定位，排查过程高度依赖尝试
• 认知负荷高，感觉是对的，一写就错了    • 问题不易复现，调试周期不可控
• 协作依赖经验传递，交接成本持续走高    • 链路缺乏可观测性，复杂流程难以跟踪
• 部署流程复杂，经常因环境差异反复折腾   • 性能瓶颈不透明，无法快速确认卡点


•   新能力接入牵动全面，改动范围难控制   •  环境切换需手工适配，大幅拖慢上线效率
•   缺少统一扩展点，定制策略实现成本高   •  更换模型或技术栈时需重写大量逻辑
•   常见场景无法配置完成，需要重复造轮子  •  基础设施变化导致系统难以跨平台复用
•   模块耦合度高，扩展功能易破坏原有逻辑  •  缺乏抽象层，使企业级扩张成本倍增
        扩展受限               迁移艰难

## Page 19

  如何提高开发者的开发体验

设计目标： 让算法研究员和开发者能够能够从繁杂的工程实现中解脱出来，从而专注算法和数据

对于初级开发者，LazyLLM彻底简化             对于资深的专家，LazyLLM提供
了AI应用的构建过程。他们无需再考               了极高的灵活性，为开发者提供
虑如何将任务调度到不同的IaaS平台              了无限的可能性。其模块化设计
上，不必了解API服务的构建细节，      低门槛      支持高度的定制与扩展，使用户
也无需在微调模型时选择框架或切分        高上限     能够轻松集成自有算法、行业领
模型，更不需要掌握任何Web开发知               先的生产工具以及最新的技术成
识。通过预置的组件和简单的拼接操                果，从而快速构建适配多样化需
作，初级开发者便能轻松构建出具备                求的强大应用。
生产价值的工具。
      提高框架的易用性!

## Page 20

低门槛： 文档要全，中英双语  How？
                Ø 代码里面不写文档级注释，在程序执行时动态添加文档
                Ø 通过环境变量控制中文文档或英文文档的添加
                Ø 在编译文档前，通过AST将文档插入到代码文件中
                Ø 先插入文档，再发布制品，以便IDE能正确读取文档
                Trouble：
                               __doc__' of 'method' objects is not writable
                AttributeError: attribute '__doc__' of builtin_function_or_method’
                           objects is not writable
                Solution: C++混合编程！
                namespace py = pybind11;
                void addDocStr(py::object obj, std::string docs) {
                   PyObject* ptr = obj.ptr();
                   if (Py_TYPE(ptr) == &PyCFunction_Type) {
                       auto f = reinterpret_cast<PyCFunctionObject*>(ptr);
                       f->m_ml->ml_doc = strdup(docs.c_str());
                   } else if (Py_TYPE(ptr) == &PyInstanceMethod_Type) {
                       auto im = reinterpret_cast<PyInstanceMethodObject*>(ptr);
                       if (Py_TYPE(im->func) == &PyCFunction_Type) {
                           auto f = reinterpret_cast<PyCFunctionObject*>(im->func);
                       }   f->m_ml->ml_doc = strdup(docs.c_str());
                   } else if (Py_TYPE(ptr) == &PyMethod_Type) {
               }   }   if (Py_TYPE(m->im_func) == &PyFunction_Type) { ... }

## Page 21

         低门槛：     代码要好读，好写
                                                                     1.    from langchain_core.runnables import RunnableParallel
                 在langchain中，| 左边应                                   2.
1. def get_name():        该是一个重载了__or__的                             3.    get_name = lambda x: {"name": x}
2.     return {"name": "张三"}        Runnable对象                       4.    chain = get_name | RunnableParallel({
3.                                                                   5.      "greet": (lambda d: f"你好，{d['name']}"),
4. chain = get_name | {"name": lambda x: f"你好，{x['name']}"}          6.      "shout": (lambda d: d["name"].upper()),
                                                                     7.    })
                 1                                                           2

1.     from langchain.prompts import PromptTemplate                  1.     from langchain.prompts import PromptTemplate
2.     from langchain_openai import ChatOpenAI                       2.     from langchain_openai import ChatOpenAI
3.     from langchain_core.runnables import RunnableParallel         3.     from langchain_core.runnables import RunnableLambda
4.                                                                   4.
5.           prompt1 = PromptTemplate.from_template("你好，{name}")     5.     prompt = PromptTemplate.from_template("翻译成英文：{text}")
6.           prompt2 = PromptTemplate.from_template("再见，{name}")     6.     llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
7.        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)     7.     post_process = RunnableLambda(lambda x: x.upper())
8.     chain = RunnableParallel({     PromptTemplate 需要输入 {"name":   8.          ChatOpenAI输出的是
9.           "greet": prompt1 | llm,  "张三"} 才能替换模板。传 "张三"，           9.     chain = prompt | llm | post_process AIMessage对象，不是纯文本，
10.          "bye": prompt2 | llm     RunnableParallel 会把这个字符串直      10.    print(chain.invoke({"text": "你好"})) 中间需要
11.    })        接交给 prompt1 和 prompt2，它们                                        加 attrgetter("content") 提取
12.              找不到 name 这个 key，报错。
13.    print(chain.invoke("张三"))
                 3                                                           4

## Page 22

     低门槛：     代码要好读，好写
     import lazyllm
     from lazyllm import pipeline, parallel, bind, SentenceSplitter, Document, Retriever, Reranker, OnlineEmbeddingModule
1.   prompt = (‘You will play the role of an AI Q&A assistant and complete a dialogue task. In this task, you need ‘
2.   'to provide your answer based on the given context and question.')
     documents.create_node_group(name=“sentences”, transform=SentenceSplitter, chunk_size=1024, chunk_overlap=100)
3.   documents = Document(dataset_path=“rag_master”, embed=lazyllm.TrainableModule("bge-large-zh-v1.5"), manager=False)
4.   with pipeline() as ppl:     跨模块参数传递怎么做？
5.   with parallel().sum as prl:
6.   prl.retriever1 = Retriever(documents, group_name=“sentences”, similarity="cosine", topk=3)
7.   prl.retriever2 = Retriever(documents, “CoarseChunk”, "bm25_chinese", 0.003, topk=3)
8.   ppl.reranker = Reranker(‘ModuleReranker‘, ...)
9.   ppl.formatter = (lambda nodes, query: dict(context_str=nodes, query=query))
10.  ppl.llm = lazyllm.TrainableModule("internlm2-chat-7b").prompt(lazyllm.ChatPrompter(prompt, extro_keys=["context_str"]))
11.  web = lazyllm.WebModule(ppl)

## Page 23

    低门槛：代码要好读，好写之参数跨模块传输
        LangChain                                                   LlamaIndex
Runnable 链式机制对参数随意传输没有自动化能力，LCEL的                          •                                     定义了Component组件与图式工作流，支持
数据流设计就是严格的“上一步输出→下一步输入”。跨模块传                                    定义组件之间的连接关系以及流通数据
参只推荐使用RunnablePassthrough.assign 在保留原输入的                   •    定义过程较为繁琐，调试成本极高
同时追加新字段
                                                                links.append(Link("input", "query_trans", src_key="query",
# 任何后续节点都能用x["user_id"]                                         dest_key="query"))
chain=RunnablePassthrough.assign(user_id=RunnableLambda(        links.append(Link("input", "query_trans",
        lambda x: x[“token”].split(“.”)[0])) |                  src_key="chat_history", dest_key="chat_history"))
        RunnableLambda(lambda x: {“greet”: f“你好，                links.append(Link("query_trans", "sub_query", src_key="query",
                                                                dest_key="query"))
        {x['user_id']}", **x})                                  links.append(Link("sub_query", "retriever", src_key="query",
print(chain.invoke({"token": "42.xxx"}))                        dest_key="input"))
# => {'token': '42.xxx', 'user_id': '42', 'greet': '你好，         links.append(Link("retriever", "llm", dest_key="nodes"))
42'}    LangGraph                                               links.append(Link("input", "llm", src_key="stream",
                                                                dest_key="stream"))
                                                                links.append(Link("query_trans", "llm", src_key="query",
        显示建模，专门用来定义有状态工作流                                       dest_key="query"))
                                                                links.append(Link("input", "output_parser", src_key="stream",
•       add_node(), set_entry_point() ...                       dest_key="stream"))
                                                                … …

## Page 24

低门槛：代码要好读，好写之参数跨模块传输
1. 借鉴c++的参数绑定机制        2. 在python中仿写bind
#include <functional>                  Ø 定义了“单例”的Placeholder，并实例化出_1到_10
using namespace std::placeholders;     Ø 定义了Bind，仿写了C++的bind机制
int f(int a, int b, int c);
auto g = std::bind(f, _2, 10, _1);     Ø 额外增加了kw的bind方式
int main(int argc, char **argv) {
     g(1, 2); /* -> f(2, 10, 1) */     Ø 定义了Metaclass，方便类将bind认为是自己
}                                      Ø 将bind，以及_1至_10放到builtins中，方便使用
3. 后置使用，优化阅读体验
with pipeline() as ppl:
with parallel().sum as ppl.prl:
     prl.retriever1 = Retriever(documents, group_name=“sentences”, similarity=“cosine”, topk=3)
     prl.retriever2 = Retriever(documents, “CoarseChunk”, "bm25_chinese", 0.003, topk=3)
ppl.reranker = bind（Reranker(‘ModuleReranker‘, ...), _1, query=ppl.input)
ppl.reranker = Reranker(‘ModuleReranker‘, ...) | bind(_1, query=ppl.input)
ppl.formatter = bind（lambda nodes, query: dict(context_str=nodes, query=query), query=ppl.input)
ppl.formatter = (lambda nodes, query: dict(context_str=nodes, query=query)) | bind(query=ppl.input)
ppl.llm = lazyllm.TrainableModule("internlm2-chat-7b").prompt(lazyllm.ChatPrompter(prompt, extro_keys=["context_str"]))

## Page 25

低门槛：部署要简单
能不能把代码写在一起，一键起服务，然后自动连接使用呢？
m = lazyllm.TrainableModule('m-7b', 'path').mode('finetune').trainset(data)
m.update() # 微调 + 部署 + 评测
m.start() # 仅部署
m(’你好’)   # 推理

LazyLLM Module：训练 + 部署 + 推理 + 评测 一站式使用，外加缓存和监控

    共享使用        连部署好的模型        Model Map

有时候，我们希望多个模块使用同一个模型，                 有时候，公司已经有部署好的vllm模型，或者            有时候，我们希望有人部署好模型时候就直接
减少部署的次数。                              其他的模型，需要直接连接。但部署方式不是标           使用，没有人部署，我们就自己重新部署一个。
m = lazyllm.TrainableModule('m-7b’)  准的OpenAI格式。        m = lazyllm.TrainableModule('m-7b’)
m2 = m.share()        m = lazyllm.TrainableModule(model                我们会自动查找用户配置的模型部署清单，如
通过share，实现了多个对象共享一个模型推理     ).deploy_method(url=url)                   果查到匹配的模型就直接进行连接；否则就重
服务，但各自能设置自己的提示词和后处理逻                 通过传入url，实现了连接一个部署好的模型。      新启动一个推理服务进行连接。
辑。        TrianableModule自动判断模型的输出格式。

## Page 26

 高上限：扩展要灵活

开放架构：指系统的结构允许外部能力以可控、低成本的方式接入、替换、扩展，而无需大规模重构。

 Extensible     Replaceable      Composable       Pluggable
可扩展             可替换              可组合              可插拔
未来新增功能不需要对核     底层能力（大模型、数据      不同模块像积木一样自由      在统一的使用协议下，第
心代码做大量改动，而是     库、检索引擎）更好技术      组合和衔接，动态编排出      三方插件或用户自定义模
“外挂式”接入。        选型时，不影响上层逻辑。     新流程，作用于其他模块。     块能安全接入系统。
开放架构不是指的开放源代码，而是让系统对未来开放。

## Page 27

高上限：扩展要灵活之 ORM – 让架构更开放
    ORM：Object Relational Mapping
    LazyLLM          本地
在线服务                 数据库
                     在线              …
本地模型    模型服务  数据库服务  数据库
                     文档
    Prompt    推理服务   数据库
                     向量
                     数据库
    微调服务      API服务

                                 MindIE

## Page 28

     高上限：扩展要灵活之     知识库存储ORM示例
     store_conf 参数一键配置
     内存/持久化 灵活选择
 -   新增类型轻量化适配

class LazyLLMStoreBase(ABC):
 capability: StoreCapability
 need_embedding: bool = True
 supports_index_registration: bool = False
 @abstractmethod
 def connect(self, *args, **kwargs)
 @abstractmethod
 def upsert(self, collection_name: str, data: List[dict]) -> bool
 @abstractmethod
 def delete(self, collection_name: str, criteria: dict, **kwargs) -> bool
 @abstractmethod
 def get(self, collection_name: str, criteria: dict, **kwargs) -> List[dict]
 @abstractmethod
 def search(self, collection_name: str, query: Optional[str] = None, query_embedding: Optional[Union[dict, List[float]]] = None,
     topk: int = 10, filters: Optional[Dict[str, Union[str, int, List, Set]]] = None, embed_key: Optional[str] = None, **kwargs) -> List[dict]

## Page 29

        高上限：扩展要灵活之      知识库存储ORM示例
store_config = {
  "vector_store": {                                                                 1. 支持同时定义切片与向量的存储类型
        "type": "milvus",
        "kwargs": {
              "uri": os.getenv("MILVUS_URI", "http://127.0.0.1:19530"),
              "index_kwargs":{
                    'index_type': 'FLAT',
        }     }     'metric_type': 'COSINE'                                         2. 每个配置中，仅需定义type与kwargs
  },                                                                                - type: 存储类型
  "segment_store":{
        'type': 'opensearch',                                                       - kwargs: 存储 Client 配置信息（路径、鉴权、索引配
        'kwargs': {                                                                 置等），与原生配置方式差异很小，迁移学习成本低
              'uris': os.getenv("OPENSEARCH_URI", "https://127.0.0.1:9200"),
              'client_kwargs': {
                    "http_compress": True,
                    "use_ssl": True,
                    "verify_certs": False,
                    "user": os.getenv("OPENSEARCH_USER", "admin"),
} }     }     }     "password": os.getenv("OPENSEARCH_PASSWORD", "demo@123"),       3. 使用时仅需把配置参数传入Document
document = lazyllm.Document(dataset_path="./datasets", ..., store_conf=store_config)

## Page 30

    高上限：扩展要灵活

    对于类，继承即注册 对于函数，注册即继承
>>> import lazyllm                          >>> import lazyllm
>>> hasattr(lazyllm.deploy, 'a')            >>> lazyllm.module_register.new_group('mymodules')
False                                       >>> @lazyllm.module_register('mymodules')
>>> class A(lazyllm.LazyLLMDeployBase):     ... def m(input):
...     pass                                ... return f'module m get input: {input}'
...                                         ...
>>> hasattr(lazyllm.deploy, 'a')            >>> lazyllm.mymodules.m()(1)
True                                        'module m get input: 1'
                                            >>> m = lazyllm.mymodules.m()
功能扩展变得自动化、可发现                               >>> m.evalset([1, 2, 3])
并进行统一管理                                     >>> m.eval().eval_result
                                            ['module m get input: 1', 'module m get input: 2', 'module m
                                            get input: 3']

## Page 31

   高上限：迁移要简单
IaaS： 基础设施即服务
它是一种云计算服务形态，通过按需计费的方式，把原本需要自己购买和维护的计算、存储、网络等基础设施，
通过云接口提供给用户使用。
国内主流的IaaS平台：                 国外主流的IaaS平台：
商汤大装置云、字节火山云、阿里云、腾讯云、华为云、…   Amazon AWS EC2、 Microsoft Azure、 Google Cloud Platform 、…
提供调度器的抽象，屏蔽Iaas适配细节：        Sco Launcher
   函数      Launcher         K8s Launcher    算力平台
   命令                       Slurm Launcher

                            Empty Launcher

                             … …

## Page 32

高上限：迁移要简单

LLM      Embedding 文档管理服务 主服务
GateWay        网关

    Embedding


大模型 文档管理


输入  意图识别  召回器  重排器  大模型  输出

## Page 33

      小结：LazyLLM功能架构更新                                应
解析    RAG 生成             审核 ChatBI 搜索问答     … …       用
服务                       数据流                          层 Flow
       功
     文本解析 模型调用 工具调用 召回检索 重排序 数据库调用 能
模型                                                    层
平台                                                    资 Module
MCP   模型调用管理  工具管理       检索管理      文档管理     数据库管理     源
工具                                                    层
  知识库                                                 适 Component
      训推”ORM”        工具接入                   关系型       配
 数据库接入                                      数据库ORM    层 launcher
      推理框架  训练框架     本地工具集   文档    向量         关系型    基础层 算力中心
                         数据库     数据库          数据库

      部署的中间件         云服务     用户应用  框架组件

## Page 34

       背景：为什么大模型应用框架需要重新设计
       01
       功能优先 - 以模块化体系构建 Agent 的“构件库”
       02
目录     易用为本 - 从架构抽象到开发者体验
       03
       性能致胜 - 从Python 到 C++ 混合编程的架构跃迁
       04
       架构演进的原则与经验总结
       05

## Page 35

速度优化的观测指标和重要性

首字延迟（TTFT, Time To First Token）     吞吐量（Throughput）
首字延迟直接决定用户对系统是否“快”的主观感受。            在知识库入库、数据清洗、模型批量处理等场景，
在多步骤、长链路的 Agent 中，中间推理和工具调          影响的是系统整体效率与任务完成速度。吞吐量越
用会放大首字等待，因此是体验感的核心指标。               高，越能支撑大规模后台任务处理。

包加载时间（Package Load Time）           扩展效率（Scaling Efficiency）
开发阶段需要频繁重启、热加载与调试。加载慢会             扩展效率反映硬件从 1 倍扩到 N 倍后，吞吐量的
显著降低迭代速度，影响开发体验和团队效率，              损失情况。当扩容速度低于线性增长时，意味着资
因此是工程效率的重要指标。                      源利用不足，存在调度、通信或依赖瓶颈。

## Page 36

 如何快速识别系统性能瓶颈
 火焰图（perf）：告诉你 CPU 在忙什么    链路追踪（Tracing）：告诉你请求在等什么






• 哪个函数占用最多 CPU 时间？                   请求到底卡在了哪里？
• 谁的计算量最大，是否存在无效计算？              •
• 锁等待是否严重（spin lock / mutex）？    •   编排好的Agent 的哪一步最耗时？
• 热点函数是否可优化（如算法、循环、数据结构）？        •   是否存在串行步骤可通过并行提高吞吐量？
• 调用链是否有异常路径？                    •   是否有大量的空泡需要优化流水线策略？
• 是否花太多时间在 GC、解释器上？              •   包加载、冷启动、离线任务的耗时情况怎么样？
                                 •   不同线程的任务执行情况和顺序是怎么样的？

## Page 37

       建设收益分析表（示例）
        优化项  性能瓶颈描述                               优化手段     预计收益     预计成本   优先级
reading阶段前1/4在 Tracing 显示等待文本解析产生了 优化第三方文本解析服
  等待第三方库解析响           X%的等待时间，但观测文本解析服        务的吞吐量            M%    30人天   低
  应                   务，发展资源利用率仅不到一半
  Transform阶段         Tracing 显示tiktoken 占用 Y%
  （SentenceSplitter）  时间                      提高tiktoken的并行度   N%    1人天    高
  高频调用tiktoken
                      火焰图显示DocNode的构造，填写
  DocNode优化           meta信息，拷贝的时间较长，约占 将DocNode结构挪到c++        O%    15人天   中
                      Z%时间
  Transform等待时间过      Tracing显示不同线程的任务在执      将内置的Transform挪   P%    30人天   中
  长                   行Transform的时候会被GIL阻塞    到C++以提高并行度
  HTML文档解析时，
  BeautifulSoup解析和
  节点后处理的时间较
  长

  … …                 … …                     … …        … …         … …   … …

## Page 38

python系统性能瓶颈的主要原因




解释执行：无法接近机器原生速度                                     GIL（Global Interpreter Lock）：限制多线程并行
P y t h o n 是 解 释 型 语 言 ， 代 码 在 运 行 时 逐 行 解 析 ；     CPython 有全局解释器锁，同一进程内同一时间只能执行一个
C++ 是编译型语言，生成接近机器指令的本地二进制。                          Python 字节码线程。







动态类型和GC：运行时额外开销较大                                   开发群体特点：性能敏感路径易写在 Python 层
Python 的对象都是高层次的 PyObject，携带大量元信息，                  python的开发者普遍更关注开发效率，而不太关注性能，进
运行时有额外的类型检查开销和额外 GC 扫描。                             一步导致性能瓶颈集中在python层。

## Page 39

哪些模块适合用C++重写以提高性能
01     计算密集型模块        03                  海量小对象模块
       Ø 知识库入库时的文档解析（ PDF/Doc/HTML ）、     Ø 知识库解析后，分块会产生无数小Chunk及其
       大批量文本的切分、转换和信息提取                     meta信息
       Ø Embedding 结果的反序列化（向量字符串 →        Ø Embedding的返回值会包含大量的float或string
       Python 对象）                         Ø 日志，监控等
       Ø 工具调用时候的参数提取和校验（正则表达式等）
02     系统紧耦合模块        04                  并行需求强烈模块
       Ø 用于支持多用户场景下，中间结果流式输出的             Ø  知识库场景下大批量文档解析、转换、向量化
       消息队列                                  返回值反序列号等操作的并行化
       Ø 在Server-Worker模式下，用于提高进程间通信      Ø  本地CPU Embedding（非服务化）
       效率以减少Server等待的进程间共享内存              Ø  模型或应用的批量评测过程中，自定义的
                                             Similarity函数

## Page 40

    Python/C++ 混合编程的常见方案
// c_api.c API 定义                // add.cpp                                     #include <Python.h>
#include "c_api.h"               #include <pybind11/pybind11.h>
int c_add(int a, int b) {                                                       static PyObject* add(PyObject* self, PyObject* args) {
    return a + b;                namespace py = pybind11;                          int a, b;
}                                                                                  if (!PyArg_ParseTuple(args, "ii", &a, &b))
                                                                                   return NULL;
// c_api.h API 声明                int add(int a, int b) {                        }  return PyLong_FromLong(a + b);
#ifndef C_API_H                      return a + b;
#define C_API_H                                                                 static PyMethodDef Methods[] = {
int c_add(int a, int b);         }                                                 {"add", add, METH_VARARGS, "Add two integers"},
#endif                                                                          }; {NULL, NULL, 0, NULL}
# add.pxd 声明                     PYBIND11_MODULE(add, m) {
cdef extern from "c_api.h":                                                     static struct PyModuleDef module = {
      int c_add(int a, int b)        m.def("add", &add, "Add two integers");       PyModuleDef_HEAD_INIT,
# add.pyx 定义                     }                                              }; "add", NULL, -1, Methods
from add cimport c_add                                                          PyMODINIT_FUNC PyInit_add(void) {
def add(int a, int b):                                                             return PyModule_Create(&module);
    return c_add(a, b)                                                          }
    Cython                           Pybind11                                       C-Python

    用python写C++的方案                   用C++写python的方案                                 用C写python的方案

## Page 41

    Python/C++ 混合编程的分工实践


    核心层                绑定层                          Python层
    Ø 基础数据结构，关键类定义     Ø 将核心层 API 暴露给 Python    Ø 功能模块与业务逻辑的编排
    Ø 底层资源管理和生命周期管理    Ø 完成跨语言的数据结构映射           Ø 管理应用开发依赖资源的模块
    Ø 高性能组件和计算密集型函数    Ø 处理和映射异常类似和报错栈          Ø Python生态依赖及其适配层
    Ø 调度器、日志、监控（如有）    Ø 将 C++ 错误信息映射到 Python   Ø 工具集


基础数据结构与性能关键路径由 C++ 承担；高层逻辑、配置与扩展能力留给 Python
         实现“高性能内核 + 易用接口”的分层协作模型。

## Page 42

Python/C++ 混合编程的注意事项

    ABI兼容性 1 严格注意ABI的兼容性，请为每个平台、架构、Python 版本发布独立 wheel包。需要
    为上述每个版本独立设置CI Job，保证软件在各个环境上的可靠性。

    异步执行 2 Python 与 C++ 的异步算子必须由同一个 Scheduler 调度，禁止双调度器并行，否
    则会导致执行顺序与依赖关系无法保证。

多线程 3   如果需要在python中开启多线程，在进入C++代码之后，按需释放GIL，并且在回
        到python时将GIL加回来。注意C++不要随便回调python，避免死锁。

    代码调试 4 由于 C++ 在报错时通常只给出崩溃地址，因此开发阶段应启用调试符号（例如使
    用 -g 或保留符号表），以便在崩溃时获得完整且可读的调用栈，提高调试效率。

## Page 43

       背景：为什么大模型应用框架需要重新设计
       01
       功能优先 - 以模块化体系构建 Agent 的“构件库”
       02
目录     易用为本 - 从架构抽象到开发者体验
       03
       性能致胜 - 从Python 到 C++ 混合编程的架构跃迁
       04
       架构演进的原则与经验总结
       05

## Page 44

    用可演进的方式构建一个框架，而不是“一次性工程”








       需求驱动                 分层清晰
从真实业务需求出发，而非预设最终形态，  通过合理分层隔离复杂度，使各层职责明
  让框架始终服务实际应用场景。      确、可独立演进、可随时替换和优化。









       架构开放        适度设计
保持模块可插拔、可扩展，让不同业务和 避免超前抽象与复杂封装，以最小必要方
   未来能力能够自然融入体系。   案起步，确保后续可持续演化与优化。

## Page 45

功能、易用性、性能三者的权衡和取舍
                 框架开发初期
功能 确保“用的起来”      目标：验证价值
                 排序：功能 > 易用性 > 性能



                 框架增长阶段
易用 确保“用的顺畅”      目标：提升用户留存
                 排序：易用性 > 功能 > 性能



                 框架完善阶段
性能 确保“用的飞快”      目标：协助用户落地工业级场景
                 排序：性能 > 易用性 = 功能

## Page 46

  总结和展望
LazyLLM 是一款构建多Agent大模型应用的开发框架，协助开发者
用极低的成本构建复杂的AI应用，并可以持续的迭代优化效果。基
于LazyLLM的AI应用构建流程是：
  原型搭建 → 数据回流 → 迭代优化
用户可以先基于LazyLLM快速跑通应用的原型，再结合场景任务数
据进行bad-case分析，然后对应用中的关键环节进行算法迭代和模
型微调，进而逐步提升整个应用的效果。

目前，LazyLLM 已经在GitHub上开源。欢迎大家试用。
未来，我们会持续提升单机性能，增强多机扩展能力。

Ø 项目地址：https://github.com/LazyAGI/LazyLLM
Ø 项目文档：docs.lazyllm.ai

## Page 47

THANKS

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/王志宏_从原型到生产：LazyLLM的三阶段架构演化实践.pdf]]`
