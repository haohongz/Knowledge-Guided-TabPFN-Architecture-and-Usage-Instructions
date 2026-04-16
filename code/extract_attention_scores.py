"""
任务一补充：提取 Attention Score
Hook 抓取 Q 和 K，手动计算 softmax(QK^T/√d)

运行方式（Great Lakes 集群）：
  conda activate ~/tabpfn_env
  python Task1_extract_attention_scores.py
"""
import torch
import torch.nn.functional as F
from tabpfn import TabPFNClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"训练集: {X_train.shape}  测试集: {X_test.shape}", flush=True)

print("加载模型...", flush=True)
model = TabPFNClassifier()
model.fit(X_train, y_train)
print("模型加载完成", flush=True)

saved_qk = {}

def make_qk_hook(name):
    def hook_fn(module, input, output):
        if isinstance(output, torch.Tensor):
            saved_qk[name] = output.detach().clone()
    return hook_fn

hooks = []
for name, module in model.model_.named_modules():
    if 'q_projection' in name or 'k_projection' in name:
        hooks.append(module.register_forward_hook(make_qk_hook(name)))

print("开始预测...", flush=True)
y_pred = model.predict(X_test)
print(f"准确率: {(y_pred == y_test).mean():.4f}", flush=True)

for h in hooks:
    h.remove()

# 分析前3个Block的attention score
for block_idx in range(3):
    print(f"\n{'='*60}")
    print(f"Block {block_idx}")

    # Feature Attention
    q_name = f"blocks.{block_idx}.per_sample_attention_between_features.q_projection"
    k_name = f"blocks.{block_idx}.per_sample_attention_between_features.k_projection"
    if q_name in saved_qk and k_name in saved_qk:
        Q = saved_qk[q_name]
        K = saved_qk[k_name]
        d = Q.shape[-1]
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (d ** 0.5)
        attn = F.softmax(scores, dim=-1)
        print(f"\n  Feature Attention:")
        print(f"    Q: {list(Q.shape)}, K: {list(K.shape)}")
        print(f"    Score: {list(attn.shape)}")
        a = attn[0].detach().numpy()
        print(f"    第1个样本的attention矩阵:")
        for i in range(min(a.shape[0], 6)):
            row = [f"{v:.4f}" for v in a[i][:6]]
            print(f"      特征{i}: [{', '.join(row)}]")

    # Sample Attention
    q_name = f"blocks.{block_idx}.per_column_attention_between_cells.q_projection"
    k_name = f"blocks.{block_idx}.per_column_attention_between_cells.k_projection"
    if q_name in saved_qk and k_name in saved_qk:
        Q = saved_qk[q_name]
        K = saved_qk[k_name]
        d = Q.shape[-1]
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (d ** 0.5)
        attn = F.softmax(scores, dim=-1)
        print(f"\n  Sample Attention:")
        print(f"    Q: {list(Q.shape)}, K: {list(K.shape)}")
        print(f"    Score: {list(attn.shape)}")
        print(f"    K比Q少 {Q.shape[-2]-K.shape[-2]} 个样本（因果mask）")
        a = attn[0].detach().numpy()
        print(f"    第1个特征列，最后3个query对前5个key的attention:")
        for i in range(max(0, a.shape[0]-3), a.shape[0]):
            row = [f"{v:.4f}" for v in a[i][:5]]
            print(f"      样本{i}: [{', '.join(row)} ...]")

print(f"\n共捕获 {len(saved_qk)} 个Q/K张量")
