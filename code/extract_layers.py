"""
任务一：TabPFNv2 中间层提取
用 PyTorch hook 把每一层的中间结果都提取出来

运行方式（Great Lakes 集群）：
  salloc --account=lsa1 --partition=standard --time=01:00:00 --cpus-per-task=4 --mem=8G
  conda activate ~/tabpfn_env
  python Task1_extract_layers.py
"""
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
print(f"训练集: {X_train.shape}  测试集: {X_test.shape}", flush=True)

# ===== 2. 加载模型 =====
print("加载模型...", flush=True)
model = TabPFNClassifier()
model.fit(X_train, y_train)
print("模型加载完成", flush=True)

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

# ===== 4. 跑预测，hook 自动收集 =====
y_pred = model.predict(X_test)

for h in hooks:
    h.remove()

# ===== 5. 打印结果 =====
print("\n" + "=" * 60)
print("TabPFNv2 中间层输出")
print("=" * 60)

for name, info in saved.items():
    print(f"\n层: {name}")
    print(f"  Shape: {info['shape']}")
    print(f"  范围: [{info['min']:.4f}, {info['max']:.4f}]")
    print(f"  均值: {info['mean']:.4f}")
    print(f"  前5个值: {[round(v, 4) for v in info['first_5_values']]}")

print(f"\n共捕获 {len(saved)} 个中间层")
print(f"预测结果: {y_pred[:5]}")
print(f"准确率: {(y_pred == y_test).mean():.4f}")

# ===== 6. 打印模型结构 =====
print("\n" + "=" * 60)
print("模型结构 (named_modules)")
print("=" * 60)
for name, mod in model.model_.named_modules():
    if name:
        print(f"  {name}: {type(mod).__name__}")
