---
title: Pulsar2 与 M57 芯片能力调研
tags: [ai, npu, axera, pulsar2, m57, toolchain]
---

# Pulsar2 与 M57 芯片能力调研

> 数据来源：`pulsar2-docs.readthedocs.io/zh-cn/latest`（2026-06-23 抓取）
> 涉及页面：`pulsar2/introduction.html`、`appendix/op_support_list_m57.html`、`user_guides_quick/quick_start_m57.html`、`appendix/build_llm.html`

## 1. 背景

Pulsar2 是爱芯元智自研的"转换 + 量化 + 编译 + 异构"四合一神经网络编译器，目标平台涵盖 AX6 / M7 / M5 三个系列：

- AX6 系列：AX615
- M7 系列：AX630C、AX637、AX620Q
- M5 系列：AX650A、AX650N、M76H、M57H
- 车载平台：M76H 等

文档按芯片划分章节：Section 4（AX650）、Section 5（AX620E）、Section 6（AX615）、**Section 7（M57）**。

## 2. M57 在 Pulsar2 中的定位

M57 属于 M5 系列，与 M76H 同列。Section 7 章节仅覆盖通用 ONNX → axmodel 流程（示例模型 MobileNetv2），**未提供 LLM 编译入口**。

### M57 NPU 工作模式

- 通过 `pulsar2 build` 的 `--npu_mode` 参数指定，取值 `{NPU1, NPU2, NPU3}`
- 章节示例使用 `NPU1`
- 与 AX620E / AX630C 类似，需根据 AI-ISP 是否启用划分工况

### M57 工具链命令

- `pulsar2 build`：ONNX → axmodel 转换
- `pulsar2 run`：模型转换后仿真运行
- `pulsar2 version`：版本查询

## 3. M57 NPU 算子支持总览

支持的 ONNX opset_version 大于等于 11。算子能力分四类：

| 标记 | 含义 |
|---|---|
| 无限制 | 当前实现支持，参数空间未受约束 |
| 暂不支持 | 当前版本未实现，但 NPU 理论上能支持，后续可能补上 |
| 不支持 | 硬件/架构上无法实现该属性 |
| 属性受限 | 部分 attr 不支持或只能取特定值 |

### 完整支持（无限制）的关键算子

LLM / 视觉主流结构所需算子基本齐全：

- **基础运算**：Abs / Add / Sub / Mul / Div / Neg / Pow / Where / Min / Max / Cast / Clip / Equal / Greater / Less / Xor / Not
- **矩阵与卷积**：MatMul / Conv / ConvTranspose / DepthToSpace / SpaceToDepth / Gemm（部分 attr 受限）
- **归一化**：LayerNormalization / RMSNormalization / GroupNormalization / InstanceNormalization / BatchNormalization / LpNormalization / LogSoftmax
- **激活**：Relu / LeakyRelu / Silu / Swish / Gelu / Mish / HardSigmoid / HardSwish / Elu / Sigmoid / Tanh / Softplus / Erf / Exp
- **池化**：AveragePool / MaxPool / GlobalAveragePool / GlobalMaxPool
- **形状与索引**：Reshape / Flatten / Transpose / Squeeze / Unsqueeze / Slice / Gather / GatherElements / GatherND / ScatterElements / ScatterND / Tile / Topk / Expand / Concat / Split / Identity
- **规约**：ReduceMean / ReduceMax / ReduceMin / ReduceSum / ReduceL2
- **Transformer 专用**：RotaryEmbedding（无限制）、RoiAlign、SpatialTransformer、GridSample、Bevpool
- **循环网络**：LSTM（支持 bidirectional / reverse / forward，部分高级 attr 不支持）

### 对 LLM 关键算子的限制

以下限制在跑 LLM 类模型时需要重点注意：

| 算子 | 限制 | 影响 |
|---|---|---|
| Gemm | `alpha` / `beta` 暂不支持 | 需把 α / β 折叠到权重 |
| LSTM | `activation_alpha` / `activation_beta` / `activations` / `clip` / `input_forget` / `P` 暂不支持；`sequence_lens` 不支持；`layout` 只支持 0 | RNN 家族可用但有限 |
| Pow | exponent 只支持 initializer 标量形式，不支持 elemwise | attention 中的指数运算需绕开 |
| Gather | indices 暂时只支持 1 维 | embedding lookup 需 reshape |
| LayerNormalization | axis 暂时只支持 -1（最后一维） | LLM 的 pre/post norm 通常就是最后一维，OK |
| LpNormalization | axis 只支持 -1；p 只支持 1 或 2 | 受限 |
| Resize | mode 支持 `nearest` / `linear`；nearest_mode 只支持 `round_prefer_ceil` | 上采样受限 |
| ConvTranspose | dilations 暂时只能为 1；output_shape 暂不支持；DepthWise 效率低 | 上采样卷积需注意 |
| BatchNormalization | `momentum` / `training_mode` 不支持 | 推理 OK，训练不行 |
| PRelu | 4D 输入下 channel 在第二维，slope shape 受限 | 受限 |
| Reduce* | `noop_with_empty_axes` 暂不支持 | 需显式传 axes |
| CumSum | `exclusive` / `reverse` 暂时仅支持 0 | 受限 |
| ArgMax / ArgMin | `select_last_index` 只支持设为 0 | OK |

### Cast 类型支持

`to` 仅支持：`uint8 / int8 / uint16 / int16 / uint32 / int32 / float32`，不支持 `float16` / `bfloat16` 直接 cast。

## 4. M57 模型编译流程

### 典型配置文件（MobileNetv2）

```json
{
  "model_type": "ONNX",
  "npu_mode": "NPU1",
  "quant": {
    "input_configs": [
      {
        "tensor_name": "input",
        "calibration_dataset": "./dataset/imagenet-32-images.tar",
        "calibration_size": 32,
        "calibration_mean": [103.939, 116.779, 123.68],
        "calibration_std": [58.0, 58.0, 58.0]
      }
    ],
    "calibration_method": "MinMax",
    "precision_analysis": false
  },
  "input_processors": [
    {
      "tensor_name": "input",
      "tensor_format": "BGR",
      "src_format": "BGR",
      "src_dtype": "U8",
      "src_layout": "NHWC",
      "csc_mode": "NoCSC"
    }
  ],
  "compiler": {
    "check": 0
  }
}
```

### 编译产物

```
output/
├── build_context.json
├── compiled.axmodel          # 最终板上运行模型
├── compiler/                 # 编译器后端中间结果及 debug 信息
│   └── subgraph_npu_0/
├── debug/                    # 前端图优化中间结果及 debug 信息
└── quant/
    ├── quant_axmodel.data
    ├── quant_axmodel.json    # 量化配置信息
    └── quant_axmodel.onnx    # 量化后的模型（QuantAxModel）
```

### 编译耗时参考

- 主机：Intel Xeon Gold 6336Y @ 2.40GHz / Memory 32G
- MobileNetv2 全流程：约 12s
- 编译后端流程：tiling → build op → DDR swap → EU 调度（onepass / greedy / heuristic）

### 模型信息查询

```bash
onnx inspect -m -n -t output/compiled.axmodel
```

`-m / -n / -t` 分别查看 meta / node / tensor 信息。

### Netron 可视化

`.axmodel` 基于 ONNX 模型存储格式开发，将后缀改为 `.axmodel.onnx` 后可直接用 Netron 打开。

## 5. M57 与 LLM 能力 —— 关键结论

**官方文档明确：M57 没有 LLM 编译路径。**

### 文档原话

> 本章节适用于平台 **AX650A / AX650N / AX8850**（SDK 大于等于 v3.6.2）、**AX630C**（SDK 大于等于 v3.0.0）

### `pulsar2 llm_build --chip` 可选值

`{AX620E, AX650, LAMBERT}` —— **M57 不在可选 chip 列表中**。

### 已验证 LLM 模型（全部面向 AX650 / AX620E）

Qwen3、Qwen2.5、DeepSeek-R1-Distill、MiniCPM4、InternVL2_5、InternVL3、ChatGLM3、OpenBuddy、SmolLM2、Llama3.2、Gemma2、Phi2、Phi3、TinyLlama。

### 板端运行依赖

`ax-llm` 项目提供 `axllm run`（交互式）/ `axllm serve`（OpenAI 兼容 HTTP 服务）两条命令，文档示例全部以 AX650 开发板为载体。

### `pulsar2 llm_build` 关键参数

- `--chip {AX620E, AX650, LAMBERT}`
- `--npu_mode {NPU1, NPU2, NPU3}`
- `--prefill_len` / `--kv_cache_len` / `--last_kv_cache_len`：prefill 与 KV cache 配置
- `--hidden_state_type {fp16, bf16, fp32}`（默认 bf16）
- `--weight_type {fp16, bf16, fp32, s8, s4, fp8_e5m2, fp8_e4m3}`（默认 s8）
- `--post_weight_type {bf16, s8, fp8_e5m2, fp8_e4m3}`（默认 s8）
- `--tensor_parallel_size` / `--parallel`：张量并行与构建并行
- `--check_level 0|1|2`：run / layer_check / cal

## 6. LAMBERT 备注

`pulsar2 llm_build --chip` 中出现的 `LAMBERT` 选项在官方文档中无对应 `quick_start_lambert.html` 页面（404）。文档未展开说明其与 M57 的关系。**建议向爱芯 FAE 确认**是否为：

- M57 后续型号代号
- 车载平台代号
- 内部代号未公开文档

无法基于现有公开文档进一步判断。

## 7. 算子能力 —— 落地 LLM 的差距分析

虽然 `--chip` 不支持 M57，但从算子清单看 M57 理论上具备 LLM 编译所需大部分 op：

- RotaryEmbedding / RMSNormalization / LayerNormalization / Softmax ✅
- MatMul / Gemm ✅（Gemm 需折 α/β）
- Reshape / Transpose / Gather / Concat / Split ✅（Gather indices 需 reshape）
- Slice / Tile / Expand ✅
- Silu / Gelu ✅

**差距 / 不确定项**：
1. 官方未提供端到端 LLM 编译配置（prefill / KV cache 切分、tensor parallel 等参数模板）
2. 板端推理引擎（`ax-llm`）是否在 M57 SDK 中提供 —— 文档无说明
3. 量化策略（`--weight_type s4`）在 M57 上的精度损失未验证
4. Beam search / sampling 参数（temperature / top_k / top_p）模板未提供

## 8. 参考链接

- Pulsar2 文档首页：https://pulsar2-docs.readthedocs.io/zh-cn/latest/index.html
- M57 算子清单：https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/op_support_list_m57.html
- M57 快速上手：https://pulsar2-docs.readthedocs.io/zh-cn/latest/user_guides_quick/quick_start_m57.html
- LLM 编译：https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/build_llm.html
- ax-llm 项目：https://github.com/AXERA-TECH/ax-llm
- ax-llm-build 项目：https://github.com/AXERA-TECH/ax-llm-build