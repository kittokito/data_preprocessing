import json
import matplotlib.pyplot as plt
import numpy as np 

# jsonlファイルのパス
jsonl_file = "/Users/nomura/Downloads/長野オートメーション/prepare_training_data/training_results/0129_logging.jsonl"

# データを格納するリスト
steps = []
losses = []
eval_steps = []
eval_losses = []
grad_norms = []
learning_rates = []

# jsonlファイルを読み込む
with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        step_info = data.get("global_step/max_steps", None)
        
        if step_info:
            step = int(step_info.split('/')[0])  # "X/513" からXを取得
            if "loss" in data:
                steps.append(step)
                losses.append(data["loss"])
                grad_norms.append(data["grad_norm"])
                learning_rates.append(data["learning_rate"])
            elif "eval_loss" in data:
                eval_steps.append(step)
                eval_losses.append(data["eval_loss"])


# 2x2のプロット配置
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# 左上: Loss & Eval Loss
axs[0, 0].plot(steps, losses, label="Loss", marker="o", linestyle="-")
axs[0, 0].plot(eval_steps, eval_losses, label="Eval Loss", marker="s", linestyle="--", color="red")
axs[0, 0].set_title("Loss and Eval Loss")
axs[0, 0].set_xlabel("Step")
axs[0, 0].set_ylabel("Loss")
axs[0, 0].legend()
axs[0, 0].grid()


# 右上: Grad Norm
axs[0, 1].plot(steps, grad_norms, label="Grad Norm", marker="^", linestyle=":", color="green")
axs[0, 1].set_title("Gradient Norm")
axs[0, 1].set_xlabel("Step")
axs[0, 1].set_ylabel("Grad Norm")
axs[0, 1].legend()
axs[0, 1].grid()

# 左下: Learning Rate
axs[1, 0].plot(steps, learning_rates, label="Learning Rate", marker="x", linestyle="-.", color="purple", alpha=0.6)
axs[1, 0].set_title("Learning Rate")
axs[1, 0].set_xlabel("Step")
axs[1, 0].set_ylabel("Learning Rate")
axs[1, 0].legend()
axs[1, 0].grid()

# 右下: 空白（不要なので削除）
fig.delaxes(axs[1, 1])

# レイアウト調整
plt.tight_layout()
plt.show()
