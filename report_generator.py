def to_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def analyze_one_stock(position: dict, quote: dict) -> dict:
    name = position["name"]
    shares = int(position["shares"])
    cost = to_float(position["cost"])

    current_price = to_float(quote.get("最新价", 0))
    pct_change = to_float(quote.get("涨跌幅", 0))
    volume = quote.get("成交量", "N/A")
    turnover = quote.get("换手率", "N/A")

    market_value = current_price * shares
    pnl = (current_price - cost) * shares
    pnl_pct = ((current_price - cost) / cost * 100) if cost > 0 else 0

    advice = "不动"
    op_time = "今天不动"
    qty = 0
    trigger = "暂无"
    reason = "暂无明显优势信号"

    if current_price <= 0:
        advice = "不动"
        op_time = "今天不动"
        qty = 0
        trigger = "行情获取失败"
        reason = "未成功拿到实时价格"
    elif pnl_pct <= -5:
        advice = "止损"
        op_time = "10:30-11:00"
        qty = min(100, shares)
        trigger = "跌破成本5%"
        reason = "控制回撤，避免亏损扩大"
    elif pnl_pct >= 8 and pct_change >= 2:
        advice = "止盈"
        op_time = "14:00-14:30"
        qty = min(100, shares)
        trigger = "盈利超过8%且当日偏强"
        reason = "先锁定部分利润"
    elif pnl_pct >= 3 and pct_change >= 1:
        advice = "减仓"
        op_time = "14:00-14:30"
        qty = min(100, shares)
        trigger = "盈利区间内延续走强"
        reason = "保留底仓同时兑现部分收益"
    elif abs(pnl_pct) < 2 and pct_change > 1.5:
        advice = "持有"
        op_time = "观察到14:30"
        qty = 0
        trigger = "接近成本位但走势转强"
        reason = "先看是否继续放量上攻"
    elif pct_change < -2 and pnl_pct < 0:
        advice = "减仓"
        op_time = "10:30-11:00"
        qty = min(100, shares)
        trigger = "弱势下跌且处于亏损"
        reason = "减小风险暴露"
    else:
        advice = "不动"
        op_time = "今天不动"
        qty = 0
        trigger = "无清晰信号"
        reason = "等待更优买卖点"

    return {
        "name": name,
        "shares": shares,
        "cost": cost,
        "current_price": round(current_price, 3),
        "volume_change": f"涨跌幅{pct_change:.2f}% / 成交量{volume} / 换手率{turnover}",
        "advice": advice,
        "op_time": op_time,
        "qty": qty,
        "trigger": trigger,
        "reason": reason,
        "market_value": market_value,
        "pnl": pnl
    }


def summarize_market(index_df) -> str:
    if index_df is None or index_df.empty:
        return "大盘概括：指数数据暂不可用。"

    info = {}
    for _, row in index_df.iterrows():
        name = row.get("名称", "")
        pct = row.get("涨跌幅", 0)
        try:
            pct = float(pct)
        except Exception:
            pct = 0.0
        info[name] = pct

    sh = info.get("上证指数", 0)
    sz = info.get("深证成指", 0)
    cyb = info.get("创业板指", 0)

    if sh > 0 and sz > 0 and cyb > 0:
        tone = "三大指数同步偏强，短线情绪偏暖。"
    elif sh < 0 and sz < 0 and cyb < 0:
        tone = "三大指数同步走弱，市场情绪偏谨慎。"
    else:
        tone = "指数分化，短线以结构性机会为主。"

    return f"大盘概括：上证{sh:.2f}% / 深成指{sz:.2f}% / 创业板指{cyb:.2f}%。{tone}"


def build_email_body(total_capital: float, current_cash: float, analyses: list[dict], market_summary: str) -> str:
    holding_value = sum(x["market_value"] for x in analyses)
    total_pnl = sum(x["pnl"] for x in analyses)

    lines = []
    lines.append("【模拟账户每日建议】")
    lines.append(f"总资金：{total_capital:.2f}")
    lines.append(f"当前现金：{current_cash:.2f}")
    lines.append(f"持仓市值：{holding_value:.2f}")
    lines.append(f"总浮盈亏：{total_pnl:.2f}")
    lines.append("")

    for i, x in enumerate(analyses, start=1):
        lines.append(f"{i}. 股票名：{x['name']}")
        lines.append(f"持仓：{x['shares']}股")
        lines.append(f"成本：{x['cost']}")
        lines.append(f"现价：{x['current_price']}")
        lines.append(f"成交量变化：{x['volume_change']}")
        lines.append(f"建议：{x['advice']}")
        lines.append(f"操作时间：{x['op_time']}")
        lines.append(f"买卖数量：{x['qty']}股")
        lines.append(f"触发条件：{x['trigger']}")
        lines.append(f"理由：{x['reason']}")
        lines.append("")

    lines.append(market_summary)
    return "\n".join(lines)
