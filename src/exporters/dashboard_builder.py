"""Overview dashboard sheet builder for the Market Overview Excel."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from src.exporters.base import (
    DARK_BLUE,
    GRAY,
    HDR_FILL,
    HDR_FONT,
    LIGHT_BLUE,
    LINE_WIDTH_HEAVY,
    LINE_WIDTH_MEDIUM,
    LINK_FONT,
    SECTION_FILL,
    SECTION_FONT,
    THIN_BORDER,
    apply_axis_labels,
    apply_chart_gridlines,
    apply_x_axis_tick_interval,
    apply_y_axis_padding,
    pct_color_font,
    style_cell,
    style_line_series,
)

# Sheet name mapping for index tickers
INDEX_SHEET_NAMES: dict[str, str] = {
    "^GSPC": "SP500",
    "^IXIC": "NASDAQ",
    "^RUT": "Russell2000",
    "^DJI": "DOW",
    "KOSPI": "KOSPI",
    "KOSDAQ": "KOSDAQ",
}


def _compute_period_return(df: pd.DataFrame, days: int) -> float | None:
    """Compute percentage return over a given number of trading days.

    Args:
        df: OHLCV DataFrame with Close column.
        days: Approximate trading days to look back.

    Returns:
        Percentage return or None if insufficient data.
    """
    if len(df) < days + 1 or "Close" not in df.columns:
        return None
    current = float(df["Close"].iloc[-1])
    past = float(df["Close"].iloc[-days - 1])
    if past == 0:
        return None
    return round((current / past - 1) * 100, 2)


def _compute_ytd_return(df: pd.DataFrame) -> float | None:
    """Compute YTD return from the first trading day of the year.

    Args:
        df: OHLCV DataFrame.

    Returns:
        YTD percentage return or None.
    """
    if df.empty or "Close" not in df.columns:
        return None
    current = float(df["Close"].iloc[-1])
    current_year = df.index[-1].year
    year_data = df[df.index.year == current_year]
    if year_data.empty:
        return None
    first_close = float(year_data["Close"].iloc[0])
    if first_close == 0:
        return None
    return round((current / first_close - 1) * 100, 2)


def build_overview_sheet(
    wb: Workbook,
    index_data: dict[str, dict[str, Any]],
    period_label: str,
) -> None:
    """Build the Overview sheet with summary table and normalized performance chart.

    Args:
        wb: Workbook instance (active sheet will be used).
        index_data: Dict keyed by ticker with keys:
            - name: display name
            - market: "US" or "KR"
            - ohlcv: DataFrame
            - current: current price/value
        period_label: Display label for the analysis period.
    """
    ws = wb.active
    ws.title = "Overview"

    # Title
    ws.merge_cells("A1:L1")
    title_cell = ws.cell(row=1, column=1, value="Market Overview Dashboard")
    title_cell.font = Font(bold=True, size=16, color=DARK_BLUE)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 35

    # Subtitle: date + period
    ws.merge_cells("A2:L2")
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    ws.cell(
        row=2, column=1,
        value=f"Generated: {date_str}  |  Chart Period: {period_label}",
    ).font = Font(size=10, color=GRAY)
    ws.cell(row=2, column=1).alignment = Alignment(horizontal="center")
    ws.row_dimensions[2].height = 20

    # Headers
    headers = [
        ("No", 5), ("Market", 8), ("Index", 16), ("Current", 14),
        ("1D%", 8), ("1W%", 8), ("1M%", 8), ("3M%", 8),
        ("6M%", 8), ("YTD%", 8), ("Trend", 10), ("Detail", 8),
    ]
    for col_idx, (header, width) in enumerate(headers, 1):
        style_cell(ws, 4, col_idx, header, font=HDR_FONT, fill=HDR_FILL,
                   alignment=Alignment(horizontal="center"))
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Data rows
    # Filter out VIX from main table (it gets a special row)
    ordered_tickers = [t for t in index_data if t != "^VIX"]
    vix_ticker = "^VIX" if "^VIX" in index_data else None

    row = 5
    for i, ticker in enumerate(ordered_tickers):
        info = index_data[ticker]
        df = info["ohlcv"]
        current = info.get("current", 0)
        name = info["name"]
        market = info["market"]

        # Compute returns
        ret_1d = _compute_period_return(df, 1)
        ret_1w = _compute_period_return(df, 5)
        ret_1m = _compute_period_return(df, 21)
        ret_3m = _compute_period_return(df, 63)
        ret_6m = _compute_period_return(df, 126)
        ret_ytd = _compute_ytd_return(df)

        # Trend: based on 1M and 3M
        if ret_1m is not None and ret_3m is not None:
            if ret_1m > 0 and ret_3m > 0:
                trend = "Uptrend"
            elif ret_1m < 0 and ret_3m < 0:
                trend = "Downtrend"
            else:
                trend = "Mixed"
        else:
            trend = "N/A"

        style_cell(ws, row, 1, i + 1, alignment=Alignment(horizontal="center"))
        style_cell(ws, row, 2, market, alignment=Alignment(horizontal="center"))
        style_cell(ws, row, 3, name, font=Font(bold=True, size=10))
        style_cell(ws, row, 4, current, num_fmt="#,##0.00")

        # Return columns with color
        for col_idx, ret_val in [(5, ret_1d), (6, ret_1w), (7, ret_1m),
                                  (8, ret_3m), (9, ret_6m), (10, ret_ytd)]:
            if ret_val is not None:
                style_cell(ws, row, col_idx, ret_val / 100,
                           font=pct_color_font(ret_val),
                           num_fmt="0.00%",
                           alignment=Alignment(horizontal="center"))
            else:
                style_cell(ws, row, col_idx, "N/A",
                           alignment=Alignment(horizontal="center"))

        # Trend
        trend_color = "548235" if trend == "Uptrend" else ("C00000" if trend == "Downtrend" else GRAY)
        style_cell(ws, row, 11, trend,
                   font=Font(bold=True, color=trend_color, size=10),
                   alignment=Alignment(horizontal="center"))

        # Detail link
        sheet_name = INDEX_SHEET_NAMES.get(ticker, ticker.replace("^", ""))
        link_cell = style_cell(ws, row, 12, "Go >>", font=LINK_FONT,
                               alignment=Alignment(horizontal="center"))
        link_cell.hyperlink = f"#'{sheet_name}'!A1"

        row += 1

    # VIX row (special)
    if vix_ticker and vix_ticker in index_data:
        vix_info = index_data[vix_ticker]
        vix_current = vix_info.get("current", 0)
        vix_df = vix_info["ohlcv"]

        row += 1
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        style_cell(ws, row, 1, "VIX", font=SECTION_FONT, fill=SECTION_FILL)
        ws.cell(row=row, column=2).fill = SECTION_FILL
        ws.cell(row=row, column=2).border = THIN_BORDER
        style_cell(ws, row, 3, "Fear & Greed Index", font=SECTION_FONT, fill=SECTION_FILL)
        for c in range(4, 13):
            ws.cell(row=row, column=c).fill = SECTION_FILL
            ws.cell(row=row, column=c).border = THIN_BORDER
        row += 1

        style_cell(ws, row, 1, "", alignment=Alignment(horizontal="center"))
        style_cell(ws, row, 2, "US", alignment=Alignment(horizontal="center"))
        style_cell(ws, row, 3, "VIX (Volatility Index)", font=Font(bold=True, size=10))
        style_cell(ws, row, 4, vix_current, num_fmt="#,##0.00")

        vix_ret_1d = _compute_period_return(vix_df, 1)
        if vix_ret_1d is not None:
            style_cell(ws, row, 5, vix_ret_1d / 100,
                       font=pct_color_font(-vix_ret_1d),  # Inverted color
                       num_fmt="0.00%",
                       alignment=Alignment(horizontal="center"))

        # VIX level interpretation
        if vix_current >= 30:
            vix_label = "High Fear"
        elif vix_current >= 20:
            vix_label = "Elevated"
        elif vix_current <= 12:
            vix_label = "Complacent"
        else:
            vix_label = "Normal"
        style_cell(ws, row, 11, vix_label,
                   font=Font(bold=True, size=10),
                   alignment=Alignment(horizontal="center"))
        row += 1

    # ===== Normalized Performance Chart =====
    chart_start_row = row + 2

    ws.merge_cells(start_row=chart_start_row, start_column=1,
                   end_row=chart_start_row, end_column=12)
    style_cell(ws, chart_start_row, 1, "Normalized Performance Comparison (Base=100)",
               font=SECTION_FONT, fill=SECTION_FILL)
    for c in range(2, 13):
        ws.cell(row=chart_start_row, column=c).fill = SECTION_FILL
        ws.cell(row=chart_start_row, column=c).border = THIN_BORDER
    chart_start_row += 1

    # Write chart data
    chart_data_row = chart_start_row + 1

    # Find the common date range
    all_dfs = {t: index_data[t]["ohlcv"] for t in ordered_tickers
               if not index_data[t]["ohlcv"].empty}
    if all_dfs:
        # Use the shortest DataFrame's date range
        min_len = min(len(df) for df in all_dfs.values())
        ref_ticker = list(all_dfs.keys())[0]
        ref_dates = all_dfs[ref_ticker].index[-min_len:]

        # Header row
        style_cell(ws, chart_data_row, 1, "Date", font=HDR_FONT, fill=HDR_FILL,
                   alignment=Alignment(horizontal="center"))
        for j, ticker in enumerate(ordered_tickers):
            if ticker in all_dfs:
                style_cell(ws, chart_data_row, 2 + j,
                           index_data[ticker]["name"],
                           font=HDR_FONT, fill=HDR_FILL,
                           alignment=Alignment(horizontal="center"))

        # Data rows (normalized to 100)
        norm_global_min = float("inf")
        norm_global_max = float("-inf")
        for i in range(min_len):
            data_row = chart_data_row + 1 + i
            dt = ref_dates[i]
            date_val = dt.tz_localize(None) if hasattr(dt, 'tz_localize') and dt.tzinfo else dt
            ws.cell(row=data_row, column=1, value=date_val).number_format = "YYYY-MM-DD"

            for j, ticker in enumerate(ordered_tickers):
                if ticker not in all_dfs:
                    continue
                df = all_dfs[ticker]
                close_series = df["Close"].iloc[-min_len:]
                base = float(close_series.iloc[0])
                if base > 0:
                    normalized = float(close_series.iloc[i]) / base * 100
                    ws.cell(row=data_row, column=2 + j, value=round(normalized, 2))
                    norm_global_min = min(norm_global_min, normalized)
                    norm_global_max = max(norm_global_max, normalized)

        data_end_row = chart_data_row + min_len

        # Create chart
        chart = LineChart()
        chart.title = "Normalized Performance (Base = 100)"
        chart.style = 10
        chart.width = 32
        chart.height = 16
        chart.legend.position = "b"
        apply_chart_gridlines(chart)
        apply_axis_labels(chart, x_title="Date", y_title="Normalized Value",
                          y_numfmt="0.00", x_numfmt="yyyy-mm")
        if norm_global_min < float("inf"):
            apply_y_axis_padding(chart, norm_global_min, norm_global_max)
        apply_x_axis_tick_interval(chart, min_len)

        dates_ref = Reference(ws, min_col=1, min_row=chart_data_row + 1,
                              max_row=data_end_row)

        colors = ["2F5496", "ED7D31", "70AD47", "FFC000", "7030A0", "44546A"]
        active_cols = [j for j, t in enumerate(ordered_tickers) if t in all_dfs]

        for idx, j in enumerate(active_cols):
            data_ref = Reference(ws, min_col=2 + j, min_row=chart_data_row,
                                 max_row=data_end_row)
            chart.add_data(data_ref, titles_from_data=True)
            chart.set_categories(dates_ref)
            style_line_series(chart.series[idx],
                              colors[idx % len(colors)], LINE_WIDTH_HEAVY)

        norm_chart_row = data_end_row + 2
        ws.add_chart(chart, f"A{norm_chart_row}")

        # ===== Individual Index Mini-Charts (3x2 grid) =====
        mini_section_row = norm_chart_row + 17  # below the normalized chart
        ws.merge_cells(start_row=mini_section_row, start_column=1,
                       end_row=mini_section_row, end_column=12)
        style_cell(ws, mini_section_row, 1,
                   "Individual Index Trends",
                   font=SECTION_FONT, fill=SECTION_FILL)
        for c in range(2, 13):
            ws.cell(row=mini_section_row, column=c).fill = SECTION_FILL
            ws.cell(row=mini_section_row, column=c).border = THIN_BORDER

        # Write individual close-price data in columns N onwards
        # (N=14, O=15, P=16, Q=17, R=18, S=19 for up to 6 indices)
        mini_data_start_col = 14
        mini_header_row = mini_section_row + 1

        # Date column for mini charts
        style_cell(ws, mini_header_row, mini_data_start_col - 1, "Date",
                   font=HDR_FONT, fill=HDR_FILL,
                   alignment=Alignment(horizontal="center"))
        for i in range(min_len):
            r = mini_header_row + 1 + i
            dt = ref_dates[i]
            date_val = dt.tz_localize(None) if hasattr(dt, 'tz_localize') and dt.tzinfo else dt
            ws.cell(row=r, column=mini_data_start_col - 1,
                    value=date_val).number_format = "YYYY-MM-DD"

        # Write each index close prices as separate columns
        mini_date_ref = Reference(ws, min_col=mini_data_start_col - 1,
                                  min_row=mini_header_row + 1,
                                  max_row=mini_header_row + min_len)

        # Grid layout: 3 columns x 2 rows
        # Row 1: SP500, NASDAQ, Russell2000
        # Row 2: DOW, KOSPI, KOSDAQ
        grid_order = ["^GSPC", "^IXIC", "^RUT", "^DJI", "KOSPI", "KOSDAQ"]
        grid_names = {
            "^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^RUT": "Russell 2000",
            "^DJI": "DOW", "KOSPI": "KOSPI", "KOSDAQ": "KOSDAQ",
        }
        mini_chart_w = 10.5
        mini_chart_h = 9

        for g_idx, ticker in enumerate(grid_order):
            if ticker not in all_dfs:
                continue
            df = all_dfs[ticker]
            col_num = mini_data_start_col + g_idx
            display = grid_names.get(ticker, ticker)

            # Write header
            style_cell(ws, mini_header_row, col_num, display,
                       font=HDR_FONT, fill=HDR_FILL,
                       alignment=Alignment(horizontal="center"))
            # Write close prices
            close_series = df["Close"].iloc[-min_len:]
            for i in range(min_len):
                ws.cell(row=mini_header_row + 1 + i,
                        column=col_num,
                        value=round(float(close_series.iloc[i]), 2))

            mini_data_end = mini_header_row + min_len

            # Create mini chart
            mini = LineChart()
            mini.title = display
            mini.style = 10
            mini.width = mini_chart_w
            mini.height = mini_chart_h
            mini.legend = None
            apply_chart_gridlines(mini)
            apply_axis_labels(mini, y_numfmt="#,##0.00",
                              x_numfmt="yy-mm")
            apply_y_axis_padding(mini, float(close_series.min()),
                                 float(close_series.max()))
            apply_x_axis_tick_interval(mini, min_len)
            mini.x_axis.tickLblPos = "low"

            data_ref = Reference(ws, min_col=col_num,
                                 min_row=mini_header_row,
                                 max_row=mini_data_end)
            mini.add_data(data_ref, titles_from_data=True)
            mini.set_categories(mini_date_ref)
            style_line_series(mini.series[0],
                              colors[g_idx % len(colors)], LINE_WIDTH_MEDIUM)

            # Calculate grid position (3 cols x 2 rows)
            grid_col = g_idx % 3   # 0, 1, 2
            grid_row = g_idx // 3  # 0 or 1
            # Anchor column: A=1, roughly col 1 + grid_col * ~7 cols
            anchor_col_letters = ["A", "E", "I"]
            anchor_row = mini_section_row + 2 + grid_row * 15
            anchor = f"{anchor_col_letters[grid_col]}{anchor_row}"
            ws.add_chart(mini, anchor)

    ws.freeze_panes = "A5"
    ws.sheet_properties.tabColor = DARK_BLUE
