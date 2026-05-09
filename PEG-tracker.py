import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def fetch_valuation(symbol):
    """抓取单个股票的估值数据"""
    try:
        print(f"正在获取 {symbol} 的数据...")
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # 提取核心估值指标
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        pb_ratio = info.get('priceToBook')
        trailing_pe = info.get('trailingPE')
        forward_pe = info.get('forwardPE')
        peg_ratio = info.get('pegRatio')
        earnings_growth = info.get('earningsGrowth')
        
        # 处理 PEG 缺失时的备用计算逻辑
        if not peg_ratio and trailing_pe and earnings_growth:
            peg_ratio = trailing_pe / (earnings_growth * 100)
            
        # 货币单位自适应 (韩股 KRW，美股 USD)
        currency = info.get('currency', 'USD')
            
        # 构建结构化数据字典
        data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Symbol": symbol,
            f"Price ({currency})": current_price if current_price else "N/A",
            "P/B Ratio": round(pb_ratio, 2) if pb_ratio else "N/A",
            "Trailing P/E": round(trailing_pe, 2) if trailing_pe else "N/A",
            "Forward P/E": round(forward_pe, 2) if forward_pe else "N/A",
            "PEG Ratio": round(peg_ratio, 3) if peg_ratio else "N/A",
            "Expected Growth": f"{round(earnings_growth * 100, 2)}%" if earnings_growth else "N/A"
        }
        
        return data, pb_ratio, peg_ratio

    except Exception as e:
        print(f"❌ 获取 {symbol} 数据失败: {e}")
        return None, None, None

def analyze_signals(symbol, pb, peg):
    """基于估值指标的自动化分析与预警逻辑"""
    alerts = []
    
    if pb and isinstance(pb, (int, float)):
        # 存储股通用 P/B 逃顶逻辑
        if pb >= 2.4:
            alerts.append(f"🔴 [{symbol} 危险] P/B = {pb} 已达周期极限高位，建议清仓保护利润！")
        elif pb >= 2.0:
            alerts.append(f"🟠 [{symbol} 预警] P/B = {pb} 进入高估值区，建议结合技术面分批止盈。")
            
    if peg and isinstance(peg, (int, float)):
        if peg > 1.5: 
            alerts.append(f"🟡 [{symbol} 过热] PEG = {peg}，估值扩张极快，请密切关注行业基本面拐点。")
            
    return alerts

def save_to_csv(data_list, filename="valuation_log.csv"):
    """将批量抓取的数据一次性追加到本地 CSV 文件中"""
    df = pd.DataFrame(data_list)
    # 检查文件是否存在
    file_exists = os.path.isfile(filename)
    df.to_csv(filename, mode='a', index=False, header=not file_exists)
    print(f"\n✅ {len(data_list)} 条数据已成功存入 {filename}")

if __name__ == "__main__":
    # 🎯 在这里添加你想跟踪的任何股票代码！
    symbols_to_track = ["000660.KS","005930.KS","MU"] 
    
    all_results = []
    all_alerts = []
    
    print("="*80)
    print(" 周期股估值多维监控系统")
    print("="*80)
    
    # 遍历抓取所有股票
    for sym in symbols_to_track:
        result_data, current_pb, current_peg = fetch_valuation(sym)
        if result_data:
            all_results.append(result_data)
            # 收集这只股票的预警信号
            alerts = analyze_signals(sym, current_pb, current_peg)
            all_alerts.extend(alerts)
            
    # 打印最终数据表格
    if all_results:
        print("\n📊 【今日数据概览】")
        df = pd.DataFrame(all_results)
        # 填充 NaN 为 "N/A" 以防显示错位
        df = df.fillna("N/A") 
        print(df.to_string(index=False))
        
        print("\n💡 【系统策略分析】")
        if all_alerts:
            for alert in all_alerts:
                print(alert)
        else:
            print("🟢 所有监控标的估值均未触及高危预警线。")
        print("="*80)
        
        # 写入 CSV
        save_to_csv(all_results)
