import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_hynix_peg():
    # SK海力士在韩交所的代码
    symbol = "000660.KS"
    try:
        hynix = yf.Ticker(symbol)
        info = hynix.info
        
        # 尝试直接获取 Yahoo Finance 计算好的 PEG
        peg_ratio = info.get('pegRatio')
        trailing_pe = info.get('trailingPE')
        forward_pe = info.get('forwardPE')
        
        # 提取用于手动计算的备用指标 (如 earnings growth)
        earnings_growth = info.get('earningsGrowth')
        
        # 如果直接获取不到 PEG，尝试通过 PE 和 Growth 手动计算
        if not peg_ratio and trailing_pe and earnings_growth:
            # earnings_growth 通常是小数形式，如 0.25 代表 25%
            # PEG 计算时分母使用百分比的绝对值，即 25
            peg_ratio = trailing_pe / (earnings_growth * 100)
            
        # 构建数据字典
        data = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Symbol": symbol,
            "PEG_Ratio": round(peg_ratio, 3) if peg_ratio else "N/A",
            "Trailing_PE": round(trailing_pe, 3) if trailing_pe else "N/A",
            "Forward_PE": round(forward_pe, 3) if forward_pe else "N/A",
            "Earnings_Growth": f"{round(earnings_growth * 100, 2)}%" if earnings_growth else "N/A"
        }
        
        return data

    except Exception as e:
        print(f"数据获取失败: {e}")
        return None

if __name__ == "__main__":
    result = fetch_hynix_peg()
    if result:
        # 使用 Pandas 格式化输出，方便后续对接数据库或 CSV 日志
        df = pd.DataFrame([result])
        print("=== SK Hynix 估值监控 ===")
        print(df.to_string(index=False))
