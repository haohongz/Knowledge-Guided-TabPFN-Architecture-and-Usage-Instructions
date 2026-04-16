# TabPFNv2 中间层提取：代码总结与架构解读

## 一、我们做了什么

用 PyTorch 的 hook 机制，在 TabPFNv2 模型的每一层上"装了探针"，让模型在做预测的时候，自动把每一层的中间计算结果保存下来。一共捕获了 **439 个中间层**的输出。

---

## 二、完整代码

```python
import torch
import numpy as np
from tabpfn import TabPFNClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# ===== 1. 准备数据 =====
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"训练集: {X_train.shape}  测试集: {X_test.shape}")
# 输出: 训练集: (120, 4)  测试集: (30, 4)

# ===== 2. 加载模型并 fit =====
model = TabPFNClassifier()
model.fit(X_train, y_train)
# fit 之后才能访问 model.model_（底层的 PyTorch nn.Module）

# ===== 3. 用 hook 提取中间结果 =====
saved = {}

def make_hook(name):
    def hook_fn(module, input, output):
        if isinstance(output, torch.Tensor):
            saved[name] = {
                "shape": list(output.shape),
                "min": output.min().item(),
                "max": output.max().item(),
                "mean": output.mean().item(),
                "first_5_values": output.flatten()[:5].tolist(),
            }
    return hook_fn

hooks = []
for name, module in model.model_.named_modules():
    if name:
        hooks.append(module.register_forward_hook(make_hook(name)))

# ===== 4. 跑一次预测，hook 自动收集 =====
y_pred = model.predict(X_test)

# ===== 5. 移除 hooks =====
for h in hooks:
    h.remove()

# ===== 6. 打印结果 =====
for name, info in saved.items():
    print(f"\n层: {name}")
    print(f"  Shape: {info['shape']}")
    print(f"  范围: [{info['min']:.4f}, {info['max']:.4f}]")
    print(f"  均值: {info['mean']:.4f}")
    print(f"  前5个值: {[round(v, 4) for v in info['first_5_values']]}")

print(f"\n共捕获 {len(saved)} 个中间层")
print(f"准确率: {(y_pred == y_test).mean():.4f}")
```

---

## 三、Hook 是什么？大白话解释

Hook 就是 PyTorch 提供的一个"窃听器"。正常情况下，模型做前向传播时，数据从第一层流到最后一层，中间结果算完就丢了，你看不到。

`register_forward_hook` 的作用是：在某一层算完之后，先别急着往下传，先把结果拷贝一份存到我们的 `saved` 字典里，然后再正常继续。

就像在水管的每个接头处装了一个分流阀，水正常流，但你同时在每个接头接了个小桶，收集了每一段的水样。

---

## 四、TabPFNv2 的架构长什么样

从 hook 捕获的层名来看，TabPFNv2 的结构是这样的：

### 总体结构

```
输入 (X_train + X_test, y_train)
    │
    ▼
 target_embedder ─── 把训练标签编码成向量
    │
    ▼
 [输入 embedding] ─── 把每个特征值变成 192 维向量
    │
    ▼
 feature_positional_embedding ─── 加特征位置编码
    │
    ▼
 add_thinking_rows ─── 插入 64 行思考行 (150→214)
    │
    ▼
 blocks.0  ─── 第1个 Transformer Block (TabPFNBlock)
 blocks.1  ─── 第2个 Transformer Block
 blocks.2  ─── 第3个 Transformer Block
   ...
 blocks.23 ─── 第24个 Transformer Block
    │
    ▼
 output_projection ─── 最终输出头 (Sequential: Linear→GELU→Linear)
    │
    ▼
 预测概率 (只取测试集的 30 个样本)
```

一共 **24 个 Transformer Block**（blocks.0 到 blocks.23），外加一个输出投影层。

### 每个 Block 内部的结构

每个 block（比如 blocks.0）包含两种 attention，**交替执行**：

```
Block 输入
    │
    ▼
┌─────────────────────────────────────────────────┐
│  per_sample_attention_between_features          │
│  类型: AlongRowAttention（Feature Attention）    │
│  对每个样本，在特征之间做 attention              │
│                                                 │
│  q_projection (Linear): 输入 → Q               │
│  k_projection (Linear): 输入 → K               │
│  v_projection (Linear): 输入 → V               │
│  attention score = softmax(QK^T / √d)          │
│  attention output = score × V                   │
│  out_projection (Linear): 拼接后投影输出        │
└─────────────────────────────────────────────────┘
    │
    ▼
 layernorm_mha1 (LowerPrecisionRMSNorm)
    │
    ▼
┌─────────────────────────────────────────────────┐
│  per_column_attention_between_cells             │
│  类型: AlongColumnAttention（Sample Attention）  │
│  对每个特征列，在样本之间做 attention             │
│                                                 │
│  结构同上（Q/K/V 投影 → attention → out）        │
│  ⚠️ K 只包含训练样本，Q 包含所有样本（因果设计） │
└─────────────────────────────────────────────────┘
    │
    ▼
 layernorm_mha2 (LowerPrecisionRMSNorm)
    │
    ▼
┌─────────────────────────────────────────────────┐
│  mlp (Sequential)                               │
│  Linear (192→768) → GELU → Linear (768→192)    │
└─────────────────────────────────────────────────┘
    │
    ▼
 layernorm_mlp (LowerPrecisionRMSNorm)
    │
    ▼
 Block 输出 → 传入下一个 Block
```

### 模型零件清单（named_modules 输出解读）

用 `model.model_.named_modules()` 可以打印出模型的完整零件清单。每一行格式是 `层名: 模块类型`。

**顶层组件（blocks 之前）：**

| 模块名 | 类型 | 作用 |
|--------|------|------|
| `target_embedder` | Linear | 把标签 y 编码成向量。训练样本的标签要喂给模型，让它"知道"训练数据的答案 |
| `add_thinking_rows` | AddThinkingRows | TabPFNv2 特有。在输入中额外插入"思考行"，给模型更多计算空间。这就是为什么 150 个样本变成了 214 个（多出来的 64 行就是 thinking rows） |
| `feature_positional_embedding_embeddings` | Linear | 特征位置编码。让模型知道"这是第1个特征、第2个特征..."，否则模型不知道特征的顺序 |

**每个 Block 里的模块类型：**

| 类型名 | 作用 | 大白话 |
|--------|------|--------|
| `TabPFNBlock` | 一个完整的 Transformer Block | 一个处理单元，24 个串起来 |
| `AlongRowAttention` | Feature Attention | 沿行方向：对每个样本，让特征之间互相看 |
| `AlongColumnAttention` | Sample Attention | 沿列方向：对每个特征，让样本之间互相看 |
| `Linear` | 线性层 y = Wx + b | 最基本的矩阵乘法，Q/K/V 投影都是这个 |
| `LowerPrecisionRMSNorm` | RMS 归一化 | 类似 LayerNorm，但更快。把向量的大小归一化到稳定范围 |
| `GELU` | 激活函数 | 类似 ReLU 但更平滑，引入非线性 |
| `Sequential` | 容器 | 把几个子层按顺序串起来，本身不做计算 |

**MLP 内部拆解：**

```
mlp: Sequential（容器）
  ├── mlp.0: Linear    ← 192 维 → 更高维（扩展，通常 4 倍 = 768 维）
  ├── mlp.1: GELU      ← 激活函数（引入非线性）
  └── mlp.2: Linear    ← 高维 → 192 维（压缩回来）
```

**输出层拆解：**

```
output_projection: Sequential（容器）
  ├── output_projection.0: Linear    ← 192 维 → 384 维
  ├── output_projection.1: GELU      ← 激活函数
  └── output_projection.2: Linear    ← 384 维 → 10 维（10 个类别的 logits）
```

### 这和标准 Transformer 有什么区别？

**标准 Transformer**（比如 BERT）：只有一种 attention，token 之间互相 attend。

**TabPFNv2**：有两种 attention，交替进行——

1. **Feature Attention**（`per_sample_attention_between_features`）：固定一个样本，让它的不同特征之间互相关注。就像看一个病人的化验单，让"血压"、"血糖"、"胆固醇"这几个指标互相交流，发现它们之间的关系。

2. **Sample Attention**（`per_column_attention_between_cells`）：固定一个特征列，让不同样本之间互相关注。就像把所有病人的"血压"放一起比较，找出谁和谁的模式相似。

这就是 TabPFN 论文里说的 **"two-way attention"**（双向注意力），也叫 **PerFeatureEncoderLayer**。

---

## 五、每一层输出的含义（逐层解读）

以 blocks.0（第一个 Block）为例：

### 5.1 Feature Attention 部分

| 层名 | Shape | 含义 |
|------|-------|------|
| `blocks.0.per_sample_attention_between_features.q_projection` | [214, 3, 192] | Query 投影输出 |
| `blocks.0.per_sample_attention_between_features.k_projection` | [214, 3, 192] | Key 投影输出 |
| `blocks.0.per_sample_attention_between_features.v_projection` | [214, 3, 192] | Value 投影输出 |
| `blocks.0.per_sample_attention_between_features.out_projection` | [214, 3, 192] | Attention 加权后经 out 投影 |
| `blocks.0.per_sample_attention_between_features` | [214, 3, 192] | 整个 feature attention 模块输出 |

**Shape 解读 [214, 3, 192]：**
- **214**：总样本数 = 120 训练 + 30 测试 + 64 thinking rows。TabPFN 把训练集和测试集拼在一起处理，并且 `AddThinkingRows` 额外插入了 64 行"思考行"
- **3**：多头注意力的头数（num_heads = 3），或者与特征数相关的维度
- **192**：embedding 维度（每个位置的向量有 192 个数字）

### 5.2 Layer Normalization

| 层名 | Shape | 含义 |
|------|-------|------|
| `blocks.0.layernorm_mha1` | [642, 192] | feature attention 之后的归一化 |

642 = 214 × 3（前两个维度展平了）

### 5.3 Sample Attention 部分

| 层名 | Shape | 含义 |
|------|-------|------|
| `blocks.0.per_column_attention_between_cells.q_projection` | [3, 214, 192] | Query（注意维度顺序变了！） |
| `blocks.0.per_column_attention_between_cells.k_projection` | [3, 184, 192] | Key（只有 184，不是 214） |

**注意 K 的维度是 [3, 184, 192] 而不是 [3, 214, 192]！**
这说明 Sample Attention 中，Key 只来自训练样本（184 个），而 Query 来自所有样本（214 个）。这是 TabPFN 的因果推理设计：测试样本可以"看到"训练样本，但训练样本不能"看到"测试样本。

### 5.4 MLP + 输出

| 层名 | Shape | 含义 |
|------|-------|------|
| `blocks.0.mlp` | [642, 192] | Feed-Forward 网络输出 |
| `blocks.0.layernorm_mlp` | [642, 192] | MLP 后的归一化 |
| `blocks.0` | [1, 214, 3, 192] | 整个 Block 的最终输出 |

### 5.5 最终输出层

经过 24 个 Block 之后：

| 层名 | Shape | 含义 |
|------|-------|------|
| `output_projection.0` | [30, 1, 384] | 第一层投影（384 = 192×2，可能拼接了信息） |
| `output_projection.1` | [30, 1, 384] | 第二层：GELU 激活 |
| `output_projection.2` | [30, 1, 10] | 最终输出 logits |
| `output_projection` | [30, 1, 10] | 同上（整个投影模块的输出） |

- **30**：测试集样本数（只对测试集输出预测）
- **10**：TabPFN 默认最大 10 个类别（Iris 只有 3 类，剩下 7 个位置的 logit 会很小）
- 经过 softmax 之后就变成预测概率

---

## 六、数据流动的完整路径（一句话版）

```
原始表格 (120×4 训练 + 30×4 测试)
  → target_embedder：把训练标签 y 编码成向量
  → 输入 embedding：把每个数字变成 192 维向量
  → feature_positional_embedding：加上特征位置编码
  → add_thinking_rows：插入 64 行"思考行"（150 → 214）
  → 24 层 Block，每层：
      feature attention（AlongRowAttention：特征之间交流）
      → RMSNorm
      → sample attention（AlongColumnAttention：样本之间交流）
      → RMSNorm
      → MLP（Linear → GELU → Linear）
      → RMSNorm
  → output projection（Linear 192→384 → GELU → Linear 384→10）
  → softmax
  → 预测概率（只取测试集的 30 个样本）
```

---

## 七、下一步计划

1. **用更小的 toy 数据重跑**：比如 3 个训练样本、2 个特征、1 个测试样本，这样每个张量的数值都能手动验证
2. **提取 attention score 矩阵**：当前只存了每层的输出，还需要存 softmax 之后的 attention 权重（谁在关注谁）
3. **手算文档**：对着 toy 数据的具体数字，用公式写出 Q=XW_Q, K=XW_K, score=softmax(QK^T/√d) 的每一步
4. **读 nanotabicl 源码（170 行）**：对照这个极简实现，理解 TabICL 的 prior 和训练代码
5. **汇报**：下周四/五之前在群里发手算文档 + 可运行代码

---

## 附录：查看模型结构的代码

```python
from tabpfn import TabPFNClassifier
from sklearn.datasets import load_iris
import torch

X, y = load_iris(return_X_y=True)
model = TabPFNClassifier()
model.fit(X[:120], y[:120])

# 打印所有子模块的名称和类型
for name, mod in model.model_.named_modules():
    if name:
        print(f"  {name}: {type(mod).__name__}")
```
