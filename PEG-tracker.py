import yfinance as yf
import pandas as pd
from datetime import datetime
import os # 新增 os 模块用于检查文件

# ... (保留之前写的 fetch_hynix_valuation 和 analyze_signals 函数) ...

def save_to_csv(data, filename="hynix_valuation_log.csv"):
    """将抓取的数据追加到本地 CSV 文件中"""
    df = pd.DataFrame([data])
    # 检查文件是否存在，如果不存在则写入表头，存在则追加且不写表头
    file_exists = os.path.isfile(filename)
    df.to_csv(filename, mode='a', index=False, header=not file_exists)
    print(f"✅ 数据已成功追加到仓库中的 {filename}")

if __name__ == "__main__":
    result_data, current_pb, current_peg = fetch_hynix_valuation()
    
    if result_data:
        # 1. 打印终端看板（方便你在 GitHub Actions 的日志里直接查看结果）
        df = pd.DataFrame([result_data])
        print(df.to_string(index=False))
        
        # 2. 打印预警信号
        alerts = analyze_signals(current_pb, current_peg)
        for alert in alerts:
            print(alert)
            
        # 3. 核心步骤：将数据写入 CSV 文件
        save_to_csv(result_data)
