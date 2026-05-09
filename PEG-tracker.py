import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_hynix_valuation():
    # SK海力士在韩交所的代码
    symbol = "000660.KS"
    
    try:
        print(f"正在获取 {symbol} 的最新估值数据，请稍候...\n")
        hynix = yf.Ticker(symbol)
        info = hynix.info
        
        # --- 1. 提取核心估值指标 ---
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        pb_ratio = info.get('priceToBook')
        trailing_pe = info.get('trailingPE')
        forward_pe = info.get('forwardPE')
        peg_ratio = info.get('pegRatio')
        earnings_growth = info.get('earningsGrowth')
        
        # --- 2. 处理 PEG 缺失时的备用计算逻辑 ---
        if not peg_ratio and trailing_pe and earnings_growth:
            peg_ratio = trailing_pe / (earnings_growth * 100)
            
        # --- 3. 构建结构化数据字典 ---
        data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Symbol": symbol,
            "Price (KRW)": current_price if current_price else "N/A",
            "P/B Ratio": round(pb_ratio, 2) if pb_ratio else "N/A",
            "Trailing P/E": round(trailing_pe, 2) if trailing_pe else "N/A",
            "Forward P/E": round(forward_pe, 2) if forward_pe else "N/A",
            "PEG Ratio": round(peg_ratio, 3) if peg_ratio else "N/A",
            "Expected Growth": f"{round(earnings_growth * 100, 2)}%" if earnings_growth else "N/A"
        }
        
        return data, pb_ratio, peg_ratio

    except Exception as e:
        print(f"数据获取失败，可能由于网络或API限制: {e}")
        return None, None, None

def analyze_signals(pb, peg):
    """
    基于估值指标的自动化分析与预警逻辑
    """
    alerts = []
    
    if pb and isinstance(pb, (int, float)):
        if pb >= 2.4:
            alerts.append("🔴 [危险警报] P/B 已达到极高风险区 (>=2.4)，历史周期顶部特征明显，建议清仓或大幅减仓！")
        elif pb >= 2.0:
            alerts.append("🟠 [减仓预警] P/B 进入高估值区 (>=2.0)，建议结合技术面 (如跌破 EMA20) 分批止盈，或使用期权保护利润。")
        else:
            alerts.append(f"🟢 [估值正常] 当前 P/B 为 {pb}，未触及历史极限高位 (2.0~2.5区间)。")
            
    if peg and isinstance(peg, (int, float)):
        if peg > 1.5: # 假设 1.5 为你设定的高估值 PEG 阈值
            alerts.append(f"🟡 [情绪过热] PEG 达到 {peg}，估值扩张速度快于盈利预期，留意后续增长是否放缓。")
            
    return alerts

if __name__ == "__main__":
    result_data, current_pb, current_peg = fetch_hynix_valuation()
    
    if result_data:
        # 使用 Pandas 打印漂亮的表格
        df = pd.DataFrame([result_data])
        print("="*60)
        print(" SK Hynix (000660.KS) 估值监控看板")
        print("="*60)
        print(df.to_string(index=False))
        print("-" * 60)
        
        # 打印自动化分析建议
        print("【系统策略分析】：")
        alerts = analyze_signals(current_pb, current_peg)
        if alerts:
            for alert in alerts:
                print(alert)
        else:
            print("当前无特殊预警信号。")
        print("="*60)
