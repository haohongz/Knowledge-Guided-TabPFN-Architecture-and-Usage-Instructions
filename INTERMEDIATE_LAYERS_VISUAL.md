# TabPFNv2 中间层图解

> Haohong Zhang | University of Michigan | KECC Research Group
>
> 从黑箱到白箱：每一层的输入、输出、含义

---

## 1. 黑箱 vs 白箱

### 现在（黑箱）：只看到输入和输出

<p align="center">
<svg viewBox="0 0 800 120" xmlns="http://www.w3.org/2000/svg" width="700">
  <rect x="20" y="30" width="160" height="60" rx="12" fill="#E3F2FD" stroke="#1565C0" stroke-width="2"/>
  <text x="100" y="65" text-anchor="middle" font-size="15" font-weight="600" fill="#1565C0">CSV 表格</text>
  <line x1="180" y1="60" x2="300" y2="60" stroke="#999" stroke-width="2" marker-end="url(#a1)"/>
  <rect x="300" y="20" width="200" height="80" rx="12" fill="#2d2d2d" stroke="#666" stroke-width="2"/>
  <text x="400" y="55" text-anchor="middle" font-size="18" font-weight="700" fill="#fff">???</text>
  <text x="400" y="80" text-anchor="middle" font-size="12" fill="#aaa">看不到里面</text>
  <line x1="500" y1="60" x2="620" y2="60" stroke="#999" stroke-width="2" marker-end="url(#a1)"/>
  <rect x="620" y="30" width="160" height="60" rx="12" fill="#E8F5E9" stroke="#2E7D32" stroke-width="2"/>
  <text x="700" y="65" text-anchor="middle" font-size="15" font-weight="600" fill="#2E7D32">预测结果</text>
  <defs><marker id="a1" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#999"/></marker></defs>
</svg>
</p>

### 目标（白箱）：每一步都能看到

<p align="center">
<svg viewBox="0 0 800 140" xmlns="http://www.w3.org/2000/svg" width="750">
  <rect x="10" y="40" width="100" height="50" rx="8" fill="#E3F2FD" stroke="#1565C0" stroke-width="2"/>
  <text x="60" y="70" text-anchor="middle" font-size="12" font-weight="600" fill="#1565C0">CSV</text>
  <line x1="110" y1="65" x2="140" y2="65" stroke="#1565C0" stroke-width="2" marker-end="url(#a2)"/>
  <rect x="140" y="40" width="100" height="50" rx="8" fill="#FFF3E0" stroke="#E65100" stroke-width="2"/>
  <text x="190" y="62" text-anchor="middle" font-size="11" font-weight="600" fill="#E65100">Encoder</text>
  <text x="190" y="78" text-anchor="middle" font-size="9" fill="#E65100">能看到 ✓</text>
  <line x1="240" y1="65" x2="270" y2="65" stroke="#1565C0" stroke-width="2" marker-end="url(#a2)"/>
  <rect x="270" y="40" width="100" height="50" rx="8" fill="#E8F5E9" stroke="#2E7D32" stroke-width="2"/>
  <text x="320" y="62" text-anchor="middle" font-size="11" font-weight="600" fill="#2E7D32">第1层</text>
  <text x="320" y="78" text-anchor="middle" font-size="9" fill="#2E7D32">能看到 ✓</text>
  <line x1="370" y1="65" x2="400" y2="65" stroke="#1565C0" stroke-width="2" marker-end="url(#a2)"/>
  <rect x="400" y="40" width="100" height="50" rx="8" fill="#E8F5E9" stroke="#2E7D32" stroke-width="2"/>
  <text x="450" y="62" text-anchor="middle" font-size="11" font-weight="600" fill="#2E7D32">第2层</text>
  <text x="450" y="78" text-anchor="middle" font-size="9" fill="#2E7D32">能看到 ✓</text>
  <line x1="500" y1="65" x2="520" y2="65" stroke="#1565C0" stroke-width="2"/>
  <text x="535" y="70" text-anchor="middle" font-size="14" fill="#666">...</text>
  <line x1="550" y1="65" x2="570" y2="65" stroke="#1565C0" stroke-width="2" marker-end="url(#a2)"/>
  <rect x="570" y="40" width="100" height="50" rx="8" fill="#E8F5E9" stroke="#2E7D32" stroke-width="2"/>
  <text x="620" y="62" text-anchor="middle" font-size="11" font-weight="600" fill="#2E7D32">第12层</text>
  <text x="620" y="78" text-anchor="middle" font-size="9" fill="#2E7D32">能看到 ✓</text>
  <line x1="670" y1="65" x2="700" y2="65" stroke="#1565C0" stroke-width="2" marker-end="url(#a2)"/>
  <rect x="700" y="40" width="80" height="50" rx="8" fill="#F3E5F5" stroke="#7B1FA2" stroke-width="2"/>
  <text x="740" y="70" text-anchor="middle" font-size="11" font-weight="600" fill="#7B1FA2">预测</text>
  <defs><marker id="a2" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#1565C0"/></marker></defs>
</svg>
</p>

**为什么必须这样做？**

刘老师原话："你需要整个流程，不能对你来说还是个黑箱，那我们就没法改进这方法了。"

| 原因 | 解释 |
|------|------|
| 为了改模型 | Knowledge-Guided TabPFN 需要把知识注入某一层，你得知道注入到哪 |
| 为了定位问题 | 预测错了，错在哪一步？encoder？第5层？输出头？ |
| 为了验证理解 | 能算出中间层 = 真的懂了。不能算 = 只是会调包 |

---

## 2. 完整12层架构

<p align="center">
<svg viewBox="0 0 800 820" xmlns="http://www.w3.org/2000/svg" width="700">
  <rect x="250" y="10" width="300" height="50" rx="12" fill="#E3F2FD" stroke="#1565C0" stroke-width="2"/>
  <text x="400" y="32" text-anchor="middle" font-size="13" font-weight="700" fill="#1565C0">输入表格</text>
  <text x="400" y="48" text-anchor="middle" font-size="10" fill="#1565C0">(150个样本, 4个特征) → 纯数字</text>
  <line x1="400" y1="60" x2="400" y2="90" stroke="#333" stroke-width="2" marker-end="url(#b1)"/>
  <rect x="250" y="90" width="300" height="50" rx="12" fill="#FFF3E0" stroke="#E65100" stroke-width="2"/>
  <text x="400" y="112" text-anchor="middle" font-size="13" font-weight="700" fill="#E65100">Encoder（编码器）</text>
  <text x="400" y="128" text-anchor="middle" font-size="10" fill="#E65100">每个数字 → 256维向量</text>
  <line x1="400" y1="140" x2="400" y2="170" stroke="#333" stroke-width="2" marker-end="url(#b1)"/>
  <rect x="590" y="95" width="195" height="40" rx="8" fill="#f5f5f5" stroke="#ccc" stroke-width="1"/>
  <text x="688" y="112" text-anchor="middle" font-size="10" fill="#666">shape: (1, 150, 4, 256)</text>
  <text x="688" y="126" text-anchor="middle" font-size="9" fill="#999">batch, 样本, 特征, 向量维度</text>
  <rect x="150" y="170" width="500" height="170" rx="16" fill="white" stroke="#2E7D32" stroke-width="2.5"/>
  <text x="400" y="195" text-anchor="middle" font-size="14" font-weight="700" fill="#2E7D32">第 1 层（Layer 1）</text>
  <rect x="175" y="210" width="145" height="55" rx="10" fill="#FFEBEE" stroke="#C62828" stroke-width="1.5"/>
  <text x="248" y="233" text-anchor="middle" font-size="11" font-weight="600" fill="#C62828">① Row-wise</text>
  <text x="248" y="250" text-anchor="middle" font-size="9" fill="#C62828">特征之间交互</text>
  <line x1="320" y1="237" x2="345" y2="237" stroke="#333" stroke-width="1.5" marker-end="url(#b2)"/>
  <rect x="345" y="210" width="145" height="55" rx="10" fill="#E8EAF6" stroke="#283593" stroke-width="1.5"/>
  <text x="418" y="233" text-anchor="middle" font-size="11" font-weight="600" fill="#283593">② Col-wise</text>
  <text x="418" y="250" text-anchor="middle" font-size="9" fill="#283593">样本之间交互</text>
  <line x1="490" y1="237" x2="510" y2="237" stroke="#333" stroke-width="1.5" marker-end="url(#b2)"/>
  <rect x="510" y="210" width="115" height="55" rx="10" fill="#E0F2F1" stroke="#00695C" stroke-width="1.5"/>
  <text x="568" y="233" text-anchor="middle" font-size="11" font-weight="600" fill="#00695C">③ MLP</text>
  <text x="568" y="250" text-anchor="middle" font-size="9" fill="#00695C">非线性变换</text>
  <text x="400" y="320" text-anchor="middle" font-size="10" fill="#888">每个子层后都有 LayerNorm + 残差连接</text>
  <line x1="400" y1="340" x2="400" y2="365" stroke="#333" stroke-width="2" marker-end="url(#b1)"/>
  <rect x="150" y="365" width="500" height="80" rx="16" fill="white" stroke="#2E7D32" stroke-width="2" stroke-dasharray="8,4"/>
  <text x="400" y="395" text-anchor="middle" font-size="14" font-weight="700" fill="#2E7D32">第 2 层（结构完全一样）</text>
  <text x="400" y="418" text-anchor="middle" font-size="11" fill="#666">① Row-wise → ② Col-wise → ③ MLP</text>
  <line x1="400" y1="445" x2="400" y2="470" stroke="#333" stroke-width="2" stroke-dasharray="6,4"/>
  <text x="400" y="495" text-anchor="middle" font-size="20" fill="#999">⋮</text>
  <text x="400" y="520" text-anchor="middle" font-size="11" fill="#999">第 3 ~ 11 层（结构完全一样）</text>
  <line x1="400" y1="535" x2="400" y2="560" stroke="#333" stroke-width="2" stroke-dasharray="6,4"/>
  <rect x="150" y="560" width="500" height="80" rx="16" fill="white" stroke="#2E7D32" stroke-width="2.5"/>
  <text x="400" y="590" text-anchor="middle" font-size="14" font-weight="700" fill="#2E7D32">第 12 层</text>
  <text x="400" y="613" text-anchor="middle" font-size="11" fill="#666">① Row-wise → ② Col-wise → ③ MLP</text>
  <line x1="400" y1="640" x2="400" y2="670" stroke="#333" stroke-width="2" marker-end="url(#b1)"/>
  <rect x="250" y="670" width="300" height="50" rx="12" fill="#F3E5F5" stroke="#7B1FA2" stroke-width="2"/>
  <text x="400" y="692" text-anchor="middle" font-size="13" font-weight="700" fill="#7B1FA2">输出头（Output Head）</text>
  <text x="400" y="708" text-anchor="middle" font-size="10" fill="#7B1FA2">向量 → 类别概率</text>
  <line x1="400" y1="720" x2="400" y2="750" stroke="#333" stroke-width="2" marker-end="url(#b1)"/>
  <rect x="280" y="750" width="240" height="45" rx="12" fill="#E8F5E9" stroke="#2E7D32" stroke-width="2"/>
  <text x="400" y="778" text-anchor="middle" font-size="13" font-weight="700" fill="#2E7D32">预测: [0.007, 0.993]</text>
  <defs>
    <marker id="b1" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#333"/></marker>
    <marker id="b2" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#333"/></marker>
  </defs>
</svg>
</p>

**结构说明：**

- 12层结构**完全一样**，每层都包含 3 个子层
- 子层① Row-wise Attention：特征之间交互
- 子层② Column-wise Attention：样本之间交互
- 子层③ MLP：非线性变换
- 每个子层后都有 LayerNorm + 残差连接
- 总共：12层 × 3子层 = **36步操作**

**虽然结构一样，但每层学到的东西不一样：**

```
第1层之后:  age 向量只知道"我是63，旁边有 bp=145"
第3层之后:  age 向量知道"age+bmi 组合能判断健康风险"
第6层之后:  age 向量知道"整个数据集 age 分布，63 偏大"
第12层之后: age 向量融合了所有特征和所有样本 → 足够预测了
```

---

## 3. 子层①：Row-wise Attention（特征之间）

<p align="center">
<svg viewBox="0 0 800 280" xmlns="http://www.w3.org/2000/svg" width="700">
  <text x="60" y="30" font-size="12" font-weight="600" fill="#333">同一行的特征互相看：</text>
  <rect x="60" y="50" width="100" height="40" rx="6" fill="#FFCDD2" stroke="#C62828" stroke-width="2"/>
  <text x="110" y="75" text-anchor="middle" font-size="11" font-weight="600" fill="#C62828">age=63</text>
  <rect x="180" y="50" width="100" height="40" rx="6" fill="#FFCDD2" stroke="#C62828" stroke-width="2"/>
  <text x="230" y="75" text-anchor="middle" font-size="11" font-weight="600" fill="#C62828">bp=145</text>
  <rect x="300" y="50" width="100" height="40" rx="6" fill="#FFCDD2" stroke="#C62828" stroke-width="2"/>
  <text x="350" y="75" text-anchor="middle" font-size="11" font-weight="600" fill="#C62828">chol=233</text>
  <rect x="420" y="50" width="100" height="40" rx="6" fill="#FFCDD2" stroke="#C62828" stroke-width="2"/>
  <text x="470" y="75" text-anchor="middle" font-size="11" font-weight="600" fill="#C62828">bmi=28.5</text>
  <line x1="160" y1="70" x2="180" y2="70" stroke="#C62828" stroke-width="2" marker-end="url(#c1)" marker-start="url(#c2)"/>
  <line x1="280" y1="70" x2="300" y2="70" stroke="#C62828" stroke-width="2" marker-end="url(#c1)" marker-start="url(#c2)"/>
  <line x1="400" y1="70" x2="420" y2="70" stroke="#C62828" stroke-width="2" marker-end="url(#c1)" marker-start="url(#c2)"/>
  <path d="M 110 50 Q 290 0 470 50" fill="none" stroke="#C62828" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#c1)"/>
  <text x="290" y="18" text-anchor="middle" font-size="10" fill="#C62828">age 和 bmi 也能互相看</text>
  <rect x="60" y="120" width="460" height="40" rx="8" fill="#FFF8E1" stroke="#FFB300" stroke-width="1"/>
  <text x="290" y="145" text-anchor="middle" font-size="12" fill="#333">含义："年龄和血压有什么关系？BMI和胆固醇有什么关联？"</text>
  <text x="60" y="195" font-size="12" font-weight="600" fill="#999">不同行的特征在这一步不交互：</text>
  <rect x="60" y="210" width="100" height="35" rx="6" fill="#eee" stroke="#ccc" stroke-width="1"/>
  <text x="110" y="232" text-anchor="middle" font-size="10" fill="#999">病人2的age</text>
  <rect x="180" y="210" width="100" height="35" rx="6" fill="#eee" stroke="#ccc" stroke-width="1"/>
  <text x="230" y="232" text-anchor="middle" font-size="10" fill="#999">病人3的age</text>
  <text x="340" y="232" font-size="11" fill="#999">← 这些在下一步（Col-wise）才交互</text>
  <defs>
    <marker id="c1" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#C62828"/></marker>
    <marker id="c2" markerWidth="8" markerHeight="6" refX="1" refY="3" orient="auto-start-reverse"><polygon points="0 0, 8 3, 0 6" fill="#C62828"/></marker>
  </defs>
</svg>
</p>

---

## 4. 子层②：Column-wise Attention（样本之间）

<p align="center">
<svg viewBox="0 0 800 240" xmlns="http://www.w3.org/2000/svg" width="700">
  <text x="60" y="30" font-size="12" font-weight="600" fill="#333">同一列的样本互相看（需要 transpose）：</text>
  <rect x="100" y="50" width="120" height="35" rx="6" fill="#C5CAE9" stroke="#283593" stroke-width="2"/>
  <text x="160" y="72" text-anchor="middle" font-size="11" font-weight="600" fill="#283593">病人A: age=63</text>
  <rect x="100" y="100" width="120" height="35" rx="6" fill="#C5CAE9" stroke="#283593" stroke-width="2"/>
  <text x="160" y="122" text-anchor="middle" font-size="11" font-weight="600" fill="#283593">病人B: age=37</text>
  <rect x="100" y="150" width="120" height="35" rx="6" fill="#C5CAE9" stroke="#283593" stroke-width="2"/>
  <text x="160" y="172" text-anchor="middle" font-size="11" font-weight="600" fill="#283593">病人C: age=41</text>
  <line x1="160" y1="85" x2="160" y2="100" stroke="#283593" stroke-width="2" marker-end="url(#d1)" marker-start="url(#d2)"/>
  <line x1="160" y1="135" x2="160" y2="150" stroke="#283593" stroke-width="2" marker-end="url(#d1)" marker-start="url(#d2)"/>
  <path d="M 100 67 Q 50 117 100 167" fill="none" stroke="#283593" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#d1)"/>
  <rect x="300" y="70" width="420" height="100" rx="12" fill="#f8f9fb" stroke="#ddd" stroke-width="1"/>
  <text x="510" y="95" text-anchor="middle" font-size="12" font-weight="600" fill="#283593">实现方式：transpose(1, 2)</text>
  <text x="510" y="118" text-anchor="middle" font-size="11" fill="#333">原始: (batch, 150个样本, 4个特征, 256维)</text>
  <text x="510" y="138" text-anchor="middle" font-size="11" fill="#333">转置: (batch, 4个特征, 150个样本, 256维)</text>
  <text x="510" y="158" text-anchor="middle" font-size="10" fill="#888">→ 现在 attention 沿样本维度做 → 做完再转回来</text>
  <rect x="300" y="185" width="420" height="35" rx="8" fill="#FFF8E1" stroke="#FFB300" stroke-width="1"/>
  <text x="510" y="207" text-anchor="middle" font-size="12" fill="#333">含义："这个病人的年龄跟其他病人比怎么样？"</text>
  <defs>
    <marker id="d1" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#283593"/></marker>
    <marker id="d2" markerWidth="8" markerHeight="6" refX="1" refY="3" orient="auto-start-reverse"><polygon points="0 0, 8 3, 0 6" fill="#283593"/></marker>
  </defs>
</svg>
</p>

---

## 5. 数据如何在每层变化

以 "age=63" 这个 cell 为例，追踪它的向量怎么一步步演化：

<p align="center">
<svg viewBox="0 0 800 480" xmlns="http://www.w3.org/2000/svg" width="750">
  <rect x="30" y="10" width="120" height="40" rx="8" fill="#E3F2FD" stroke="#1565C0" stroke-width="2"/>
  <text x="90" y="35" text-anchor="middle" font-size="12" font-weight="600" fill="#1565C0">原始输入</text>
  <text x="200" y="25" font-size="11" fill="#333">age = 63</text>
  <text x="200" y="42" font-size="10" fill="#888">就是一个数字，没有任何上下文</text>
  <line x1="90" y1="50" x2="90" y2="75" stroke="#333" stroke-width="1.5" marker-end="url(#e1)"/>
  <rect x="30" y="75" width="120" height="40" rx="8" fill="#FFF3E0" stroke="#E65100" stroke-width="2"/>
  <text x="90" y="100" text-anchor="middle" font-size="12" font-weight="600" fill="#E65100">Encoder后</text>
  <text x="200" y="88" font-size="11" fill="#333">[0.12, -0.34, 0.56, ..., 0.08]   (256维向量)</text>
  <text x="200" y="107" font-size="10" fill="#888">知道"我是63"，但不知道旁边有什么</text>
  <line x1="90" y1="115" x2="90" y2="145" stroke="#333" stroke-width="1.5" marker-end="url(#e1)"/>
  <rect x="30" y="145" width="120" height="40" rx="8" fill="#FFEBEE" stroke="#C62828" stroke-width="2"/>
  <text x="90" y="165" text-anchor="middle" font-size="11" font-weight="600" fill="#C62828">L1 Row Attn</text>
  <text x="200" y="158" font-size="11" fill="#333">[0.18, -0.22, 0.71, ..., 0.15]   (256维，值变了)</text>
  <text x="200" y="177" font-size="10" fill="#888">现在知道"我是63，旁边有 bp=145, chol=233, bmi=28.5"</text>
  <line x1="90" y1="185" x2="90" y2="215" stroke="#333" stroke-width="1.5" marker-end="url(#e1)"/>
  <rect x="30" y="215" width="120" height="40" rx="8" fill="#E8EAF6" stroke="#283593" stroke-width="2"/>
  <text x="90" y="235" text-anchor="middle" font-size="11" font-weight="600" fill="#283593">L1 Col Attn</text>
  <text x="200" y="228" font-size="11" fill="#333">[0.25, -0.10, 0.63, ..., 0.22]   (256维，值又变了)</text>
  <text x="200" y="247" font-size="10" fill="#888">还知道"其他病人的 age 大多在 37~71 之间，63 偏大"</text>
  <line x1="90" y1="255" x2="90" y2="285" stroke="#333" stroke-width="1.5" marker-end="url(#e1)"/>
  <rect x="30" y="285" width="120" height="40" rx="8" fill="#E0F2F1" stroke="#00695C" stroke-width="2"/>
  <text x="90" y="310" text-anchor="middle" font-size="12" font-weight="600" fill="#00695C">L1 MLP</text>
  <text x="200" y="298" font-size="11" fill="#333">[0.31, -0.05, 0.58, ..., 0.28]   (256维)</text>
  <text x="200" y="317" font-size="10" fill="#888">非线性变换，增强表达能力</text>
  <line x1="90" y1="325" x2="90" y2="345" stroke="#333" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="90" y="363" text-anchor="middle" font-size="14" fill="#999">⋮</text>
  <text x="200" y="363" font-size="10" fill="#999">第2~11层继续重复，信息越来越丰富</text>
  <line x1="90" y1="373" x2="90" y2="393" stroke="#333" stroke-width="1.5" stroke-dasharray="4,3"/>
  <rect x="30" y="393" width="120" height="40" rx="8" fill="#2E7D32" stroke="#1B5E20" stroke-width="2"/>
  <text x="90" y="418" text-anchor="middle" font-size="12" font-weight="700" fill="white">第12层输出</text>
  <text x="200" y="406" font-size="11" fill="#333">[0.92, -0.03, 0.41, ..., 0.77]   (256维)</text>
  <text x="200" y="425" font-size="10" fill="#888">融合了所有特征+所有样本的完整信息 → 足够预测了</text>
  <line x1="90" y1="433" x2="90" y2="455" stroke="#333" stroke-width="1.5" marker-end="url(#e1)"/>
  <rect x="30" y="455" width="120" height="30" rx="8" fill="#F3E5F5" stroke="#7B1FA2" stroke-width="2"/>
  <text x="90" y="475" text-anchor="middle" font-size="12" font-weight="700" fill="#7B1FA2">输出头</text>
  <text x="200" y="475" font-size="11" fill="#333">[0.007, 0.993]  →  99.3% 有病</text>
  <defs><marker id="e1" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#333"/></marker></defs>
</svg>
</p>

**关键观察：** Shape 从头到尾都是 (1, 150, 4, 256)，**不会变化**。变化的是向量里的数值——每过一层，数值就更新一次，包含更多信息。

---

## 6. Attention 内部：Q、K、V 是什么

<p align="center">
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" width="750">
  <rect x="30" y="30" width="160" height="35" rx="6" fill="#C5CAE9" stroke="#283593" stroke-width="1.5"/>
  <text x="110" y="52" text-anchor="middle" font-size="11" font-weight="600" fill="#283593">病人A: age向量</text>
  <rect x="30" y="80" width="160" height="35" rx="6" fill="#C5CAE9" stroke="#283593" stroke-width="1.5"/>
  <text x="110" y="102" text-anchor="middle" font-size="11" font-weight="600" fill="#283593">病人B: age向量</text>
  <rect x="30" y="130" width="160" height="35" rx="6" fill="#C5CAE9" stroke="#283593" stroke-width="1.5"/>
  <text x="110" y="152" text-anchor="middle" font-size="11" font-weight="600" fill="#283593">病人C: age向量</text>
  <line x1="190" y1="47" x2="250" y2="47" stroke="#333" stroke-width="1" marker-end="url(#f1)"/>
  <line x1="190" y1="47" x2="250" y2="97" stroke="#333" stroke-width="1" marker-end="url(#f1)"/>
  <line x1="190" y1="47" x2="250" y2="147" stroke="#333" stroke-width="1" marker-end="url(#f1)"/>
  <rect x="250" y="30" width="50" height="30" rx="6" fill="#FFCDD2" stroke="#C62828" stroke-width="1.5"/>
  <text x="275" y="50" text-anchor="middle" font-size="11" font-weight="700" fill="#C62828">Q_A</text>
  <rect x="310" y="30" width="50" height="30" rx="6" fill="#C8E6C9" stroke="#2E7D32" stroke-width="1.5"/>
  <text x="335" y="50" text-anchor="middle" font-size="11" font-weight="700" fill="#2E7D32">K_A</text>
  <rect x="370" y="30" width="50" height="30" rx="6" fill="#BBDEFB" stroke="#1565C0" stroke-width="1.5"/>
  <text x="395" y="50" text-anchor="middle" font-size="11" font-weight="700" fill="#1565C0">V_A</text>
  <rect x="310" y="82" width="50" height="30" rx="6" fill="#C8E6C9" stroke="#2E7D32" stroke-width="1.5"/>
  <text x="335" y="102" text-anchor="middle" font-size="11" font-weight="700" fill="#2E7D32">K_B</text>
  <rect x="370" y="82" width="50" height="30" rx="6" fill="#BBDEFB" stroke="#1565C0" stroke-width="1.5"/>
  <text x="395" y="102" text-anchor="middle" font-size="11" font-weight="700" fill="#1565C0">V_B</text>
  <rect x="310" y="132" width="50" height="30" rx="6" fill="#C8E6C9" stroke="#2E7D32" stroke-width="1.5"/>
  <text x="335" y="152" text-anchor="middle" font-size="11" font-weight="700" fill="#2E7D32">K_C</text>
  <rect x="370" y="132" width="50" height="30" rx="6" fill="#BBDEFB" stroke="#1565C0" stroke-width="1.5"/>
  <text x="395" y="152" text-anchor="middle" font-size="11" font-weight="700" fill="#1565C0">V_C</text>
  <text x="460" y="50" font-size="10" fill="#C62828">Q = "我想找什么信息？"</text>
  <text x="460" y="102" font-size="10" fill="#2E7D32">K = "我有什么信息？"</text>
  <text x="460" y="152" font-size="10" fill="#1565C0">V = "我的具体内容是什么？"</text>
  <rect x="30" y="200" width="740" height="80" rx="12" fill="#FFF8E1" stroke="#FFB300" stroke-width="1.5"/>
  <text x="400" y="222" text-anchor="middle" font-size="12" font-weight="700" fill="#E65100">第二步：Q_A 和所有 K 做匹配 → 算 Attention 权重</text>
  <text x="400" y="245" text-anchor="middle" font-size="11" fill="#333">Q_A · K_A = 0.9（最像自己）  Q_A · K_B = 0.3  Q_A · K_C = 0.7</text>
  <text x="400" y="268" text-anchor="middle" font-size="11" fill="#333">softmax → 权重 = [0.55, 0.10, 0.35]    ← 加起来=1</text>
  <rect x="30" y="300" width="740" height="80" rx="12" fill="#E8F5E9" stroke="#2E7D32" stroke-width="1.5"/>
  <text x="400" y="322" text-anchor="middle" font-size="12" font-weight="700" fill="#2E7D32">第三步：用权重对 V 加权求和 → 新向量</text>
  <text x="400" y="348" text-anchor="middle" font-size="12" fill="#333">A的新向量 = 0.55 × V_A + 0.10 × V_B + 0.35 × V_C</text>
  <text x="400" y="370" text-anchor="middle" font-size="11" fill="#888">= 融合了自己55%的信息 + B的10% + C的35%</text>
  <defs><marker id="f1" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#333"/></marker></defs>
</svg>
</p>

**图书馆类比：**

| 概念 | 类比 |
|------|------|
| Q（Query） | 你去图书馆要查的问题："我想找关于糖尿病的书" |
| K（Key） | 每本书封面上的关键词 |
| V（Value） | 每本书的实际内容 |
| Attention 权重 | 你该花多少时间读每本书 |

---

## 7. 怎么提取中间层：PyTorch Hook

<p align="center">
<svg viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg" width="750">
  <text x="30" y="25" font-size="12" font-weight="700" fill="#C62828">没有 Hook（中间结果丢失）：</text>
  <rect x="30" y="40" width="80" height="35" rx="6" fill="#E3F2FD" stroke="#1565C0" stroke-width="1.5"/>
  <text x="70" y="62" text-anchor="middle" font-size="10" fill="#1565C0">输入</text>
  <line x1="110" y1="57" x2="140" y2="57" stroke="#333" stroke-width="1.5" marker-end="url(#g1)"/>
  <rect x="140" y="40" width="80" height="35" rx="6" fill="#eee" stroke="#999" stroke-width="1.5"/>
  <text x="180" y="62" text-anchor="middle" font-size="10" fill="#666">第1层</text>
  <text x="180" y="90" font-size="9" fill="#C62828">↓ 丢掉了</text>
  <line x1="220" y1="57" x2="250" y2="57" stroke="#333" stroke-width="1.5" marker-end="url(#g1)"/>
  <rect x="250" y="40" width="80" height="35" rx="6" fill="#eee" stroke="#999" stroke-width="1.5"/>
  <text x="290" y="62" text-anchor="middle" font-size="10" fill="#666">第2层</text>
  <text x="290" y="90" font-size="9" fill="#C62828">↓ 丢掉了</text>
  <line x1="330" y1="57" x2="350" y2="57" stroke="#333" stroke-width="1.5"/>
  <text x="370" y="62" font-size="12" fill="#999">...</text>
  <line x1="390" y1="57" x2="410" y2="57" stroke="#333" stroke-width="1.5" marker-end="url(#g1)"/>
  <rect x="410" y="40" width="80" height="35" rx="6" fill="#E8F5E9" stroke="#2E7D32" stroke-width="1.5"/>
  <text x="450" y="62" text-anchor="middle" font-size="10" fill="#2E7D32">输出</text>
  <text x="30" y="135" font-size="12" font-weight="700" fill="#2E7D32">有 Hook（中间结果全保留）：</text>
  <rect x="30" y="150" width="80" height="35" rx="6" fill="#E3F2FD" stroke="#1565C0" stroke-width="1.5"/>
  <text x="70" y="172" text-anchor="middle" font-size="10" fill="#1565C0">输入</text>
  <line x1="110" y1="167" x2="140" y2="167" stroke="#333" stroke-width="1.5" marker-end="url(#g1)"/>
  <rect x="140" y="150" width="80" height="35" rx="6" fill="#C8E6C9" stroke="#2E7D32" stroke-width="1.5"/>
  <text x="180" y="172" text-anchor="middle" font-size="10" fill="#2E7D32">第1层</text>
  <text x="180" y="198" font-size="9" fill="#2E7D32">↓ 存起来 ✓</text>
  <line x1="220" y1="167" x2="250" y2="167" stroke="#333" stroke-width="1.5" marker-end="url(#g1)"/>
  <rect x="250" y="150" width="80" height="35" rx="6" fill="#C8E6C9" stroke="#2E7D32" stroke-width="1.5"/>
  <text x="290" y="172" text-anchor="middle" font-size="10" fill="#2E7D32">第2层</text>
  <text x="290" y="198" font-size="9" fill="#2E7D32">↓ 存起来 ✓</text>
  <line x1="330" y1="167" x2="350" y2="167" stroke="#333" stroke-width="1.5"/>
  <text x="370" y="172" font-size="12" fill="#999">...</text>
  <line x1="390" y1="167" x2="410" y2="167" stroke="#333" stroke-width="1.5" marker-end="url(#g1)"/>
  <rect x="410" y="150" width="80" height="35" rx="6" fill="#E8F5E9" stroke="#2E7D32" stroke-width="1.5"/>
  <text x="450" y="172" text-anchor="middle" font-size="10" fill="#2E7D32">输出</text>
  <defs><marker id="g1" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#333"/></marker></defs>
</svg>
</p>

**提取代码：**

```python
import torch
from tabpfn import TabPFNClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# 准备数据
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 加载模型
model = TabPFNClassifier()
model.fit(X_train, y_train)

# 定义 hook：每当某层算完，把输出存到字典里
saved = {}

def make_hook(name):
    def hook_fn(module, input, output):
        if isinstance(output, torch.Tensor):
            saved[name] = {
                "shape": list(output.shape),
                "min": output.min().item(),
                "max": output.max().item(),
                "mean": output.mean().item(),
                "first_5": output.flatten()[:5].tolist(),
            }
    return hook_fn

# 给每一层装上 hook
hooks = []
for name, module in model.model_.named_modules():
    if name:
        hooks.append(module.register_forward_hook(make_hook(name)))

# 正常跑预测，hook 自动收集中间结果
y_pred = model.predict(X_test)

# 移除 hooks
for h in hooks:
    h.remove()

# 打印每一层的中间结果
for name, info in saved.items():
    print(f"\n层: {name}")
    print(f"  Shape: {info['shape']}")
    print(f"  范围: [{info['min']:.4f}, {info['max']:.4f}]")
    print(f"  均值: {info['mean']:.4f}")
    print(f"  前5个值: {[round(v, 4) for v in info['first_5']]}")
```

---

## 8. 研究路线图

<p align="center">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" width="750">
  <rect x="30" y="20" width="220" height="55" rx="12" fill="#FFCDD2" stroke="#C62828" stroke-width="2"/>
  <text x="140" y="42" text-anchor="middle" font-size="12" font-weight="700" fill="#C62828">第一步（现在）</text>
  <text x="140" y="60" text-anchor="middle" font-size="10" fill="#C62828">提取每层的中间输出</text>
  <line x1="250" y1="47" x2="290" y2="47" stroke="#333" stroke-width="2" marker-end="url(#h1)"/>
  <rect x="290" y="20" width="220" height="55" rx="12" fill="#FFF3E0" stroke="#E65100" stroke-width="2"/>
  <text x="400" y="42" text-anchor="middle" font-size="12" font-weight="700" fill="#E65100">第二步</text>
  <text x="400" y="60" text-anchor="middle" font-size="10" fill="#E65100">理解每层在做什么</text>
  <line x1="510" y1="47" x2="550" y2="47" stroke="#333" stroke-width="2" marker-end="url(#h1)"/>
  <rect x="550" y="20" width="220" height="55" rx="12" fill="#E8F5E9" stroke="#2E7D32" stroke-width="2"/>
  <text x="660" y="42" text-anchor="middle" font-size="12" font-weight="700" fill="#2E7D32">第三步</text>
  <text x="660" y="60" text-anchor="middle" font-size="10" fill="#2E7D32">找到注入知识的位置</text>
  <line x1="660" y1="75" x2="660" y2="110" stroke="#333" stroke-width="2" marker-end="url(#h1)"/>
  <rect x="550" y="110" width="220" height="55" rx="12" fill="#F3E5F5" stroke="#7B1FA2" stroke-width="2"/>
  <text x="660" y="132" text-anchor="middle" font-size="12" font-weight="700" fill="#7B1FA2">第四步</text>
  <text x="660" y="150" text-anchor="middle" font-size="10" fill="#7B1FA2">实现 Knowledge-Guided TabPFN</text>
  <rect x="30" y="200" width="740" height="80" rx="12" fill="#f8f9fb" stroke="#ddd" stroke-width="1"/>
  <text x="400" y="225" text-anchor="middle" font-size="12" font-weight="600" fill="#333">具体例子：想把 TARTE 的知识（768维）注入 TabPFN</text>
  <text x="400" y="248" text-anchor="middle" font-size="11" fill="#666">→ 提取中间层后发现每层是256维 → 需要投影矩阵 768→256</text>
  <text x="400" y="268" text-anchor="middle" font-size="11" fill="#666">→ 对比不同注入位置（第1层 vs 第6层 vs 第12层）→ 选最好的方案</text>
  <defs><marker id="h1" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#333"/></marker></defs>
</svg>
</p>

---

## 9. 总结

| 问题 | 回答 |
|------|------|
| 中间层是什么？ | 数据从"原始数字"变成"预测概率"过程中，每一步的向量表示 |
| 12层每层一样吗？ | 结构一样（都是 Row-Attn + Col-Attn + MLP），学到的不一样（越深越抽象） |
| 一层里有几个子层？ | 3个：Row-wise Attention、Column-wise Attention、MLP |
| 总共多少步？ | 12层 × 3子层 = 36步，加上 encoder 和输出头 |
| 怎么提取？ | 用 PyTorch Hook，装一个"监听器"自动保存每层输出 |
| 为什么要提取？ | 为了改模型。不知道中间在算什么，就不知道改哪里 |
| 刘老师要求的程度？ | 能打印12层每层的输出 shape 和数值 |

**一句话总结：** 看中间变量不是目的，是手段。目的是让你能改这个模型。
