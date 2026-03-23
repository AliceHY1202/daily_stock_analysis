import akshare as ak
import pandas as pd


def get_all_a_share_quotes():
    df = ak.stock_zh_a_spot_em()
    df["代码"] = df["代码"].astype(str).str.zfill(6)
    return df


def get_position_quotes(symbols: list[str]) -> pd.DataFrame:
    df = get_all_a_share_quotes()
    return df[df["代码"].isin(symbols)].copy()


def get_main_index_quotes() -> pd.DataFrame:
    try:
        idx_df = ak.stock_zh_index_spot_em(symbol="沪深重要指数")
        wanted = ["上证指数", "深证成指", "创业板指"]
        idx_df = idx_df[idx_df["名称"].isin(wanted)].copy()
        return idx_df
    except Exception:
        return pd.DataFrame()
