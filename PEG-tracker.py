import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

def get_naver_data(symbol):
    """专门针对韩股的爬虫补丁，从 Naver Finance 抓取真实的 PE 和 PB"""
    code = symbol.replace('.KS', '')
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    # 伪装成浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Naver 财经页面的固定 ID
        per_tag = soup.select_one('#_per')
        pbr_tag = soup.select_one('#_pbr')
        
        pe_val = float(per_tag.text.replace(',', '')) if per_tag else None
        pb_val = float(pbr_tag.text.replace(',', '')) if pbr_tag else None
        
        return pe_val, pb_val
    except Exception as e:
        print(f"  [!] Naver 补充爬取失败: {e}")
        return None, None

def fetch_valuation(symbol):
    """抓取股票估值数据 (支持雅虎与 Naver 混合补丁)"""
    try:
        print(f"正在获取 {symbol} 的数据...")
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        pb_ratio = info.get('priceToBook')
        trailing_pe = info.get('trailingPE')
        forward_pe = info.get('forwardPE')
        peg_ratio = info.get('pegRatio')
        earnings_growth = info.get('earningsGrowth')
        
        # 💡 【核心黑科技】：如果是韩股且数据缺失，启动 Naver 爬虫打补丁！
        if symbol.endswith('.KS') and (not trailing_pe or not pb_ratio):
            print(f"  -> 检测到韩股基础数据缺失，正在跨站向 Naver Finance 请求补丁...")
            naver_pe, naver_pb = get_naver_data(symbol)
            if naver_pe:
                trailing_pe = naver_pe
                print(f"  -> ✅ 成功从 Naver 补齐 Trailing P/E: {trailing_pe}")
            if naver_pb:
                pb_ratio = naver_pb
                print(f"  -> ✅ 成功从 Naver 补齐 P/B Ratio: {pb_ratio}")

        # 处理 PEG 缺失时的备用计算逻辑
        if not peg_ratio and trailing_pe and earnings_growth:
            peg_ratio = trailing_pe / (earnings_growth * 100)
            
        currency = info.get('currency', 'USD')
            
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
    alerts = []
    if pb and isinstance(pb, (int, float)):
        if pb >= 2.4:
            alerts.append(f"🔴 [{symbol} 危险] P/B = {pb:.2f} 已达周期极限高位，建议清仓保护利润！")
        elif pb >= 2.0:
            alerts.append(f"🟠 [{symbol} 预警] P/B = {pb:.2f} 进入高估值区，建议结合技术面分批止盈。")
            
    if peg and isinstance(peg, (int, float)):
        if peg > 2: 
            alerts.append(f"🟡 [{symbol} 过热] PEG = {peg:.2f}，估值扩张极快，请密切关注行业基本面拐点。")
    return alerts

def save_to_csv(data_list, filename="valuation_log.csv"):
    df = pd.DataFrame(data_list)
    file_exists = os.path.isfile(filename)
    df.to_csv(filename, mode='a', index=False, header=not file_exists)
    print(f"\n✅ 数据已成功存入 {filename}")

if __name__ == "__main__":
    symbols_to_track = ["000660.KS", "MU"] 
    
    all_results = []
    all_alerts = []
    
    print("="*80)
    print(" 周期股估值多维监控系统 (Yahoo + Naver 混合引擎)")
    print("="*80)
    
    for sym in symbols_to_track:
        result_data, current_pb, current_peg = fetch_valuation(sym)
        if result_data:
            all_results.append(result_data)
            alerts = analyze_signals(sym, current_pb, current_peg)
            all_alerts.extend(alerts)
            
    if all_results:
        print("\n📊 【今日数据概览】")
        df = pd.DataFrame(all_results)
        df = df.fillna("N/A") 
        print(df.to_string(index=False))
        
        print("\n💡 【系统策略分析】")
        if all_alerts:
            for alert in all_alerts:
                print(alert)
        else:
            print("🟢 所有监控标的估值均未触及高危预警线。")
        print("="*80)
        
        save_to_csv(all_results)
