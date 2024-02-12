#!/bin/bash
# 激活 Conda 環境
source /home/junting/miniconda3/bin/activate web_crawler

# 執行 Python 腳本
python /home/junting/insider-stock/main.py

# 停用 Conda 環境
conda deactivate

