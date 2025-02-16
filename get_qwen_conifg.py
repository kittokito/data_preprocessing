#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qwen 2.5 coder 32B の config を取得するサンプルコードです。
Hugging Face の Transformers ライブラリを用いて、指定したモデルの設定をダウンロードします。
"""

import os
from transformers import AutoConfig

# ターミナルで設定した環境変数からトークンを取得
token = os.getenv("HF_TOKEN")
if token is None:
    raise ValueError("HF_TOKEN 環境変数が設定されていません。")

# 正しいリポジトリ名を指定
model_name = "Qwen/Qwen2.5-Coder-32B"

# 認証トークンを渡して config を取得
config = AutoConfig.from_pretrained(model_name, use_auth_token=token)
print(config)

