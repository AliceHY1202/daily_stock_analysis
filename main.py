import traceback
import json
from datetime import datetime

from market_data import get_position_quotes, get_main_index_quotes
from report_generator import analyze_one_stock, summarize_market, build_email_body
from mailer import send_email


def load_holdings(path="holdings.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    try:
        config = load_holdings()

        total_capital = float(config["total_capital"])
        current_cash = float(config["current_cash"])
        positions = config["positions"]
        symbols = [p["symbol"] for p in positions]

        quote_df = get_position_quotes(symbols)
        index_df = get_main_index_quotes()

        quote_map = {}
        for _, row in quote_df.iterrows():
            code = str(row["代码"]).zfill(6)
            quote_map[code] = row.to_dict()

        analyses = []
        for p in positions:
            quote = quote_map.get(p["symbol"], {})
            analyses.append(analyze_one_stock(p, quote))

        market_summary = summarize_market(index_df)
        body = build_email_body(total_capital, current_cash, analyses, market_summary)

        with open("daily_report.txt", "w", encoding="utf-8") as f:
            f.write(body)

        subject = f"A股模拟盘日报 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        send_email(subject, body)

    except Exception as e:
        error_text = traceback.format_exc()
        subject = f"A股模拟盘日报运行失败 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        body = f"程序运行失败：\n\n{str(e)}\n\n{error_text}"
        send_email(subject, body)
        raise


if __name__ == "__main__":
    main()
