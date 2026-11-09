"""Load and parse csv data."""

from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pandas import DataFrame, concat
from plotly.express import bar, line, pie, scatter, treemap
from plotly.graph_objs import Figure

from spreadsheet_items import DATA_SHEET_NAME, OPTION_COLUMNS, Column

MIN_PIE_CHART_PERCENT = 0.005
CHART_HEIGHT = 700
TOP_VENDER_LIMIT = 15
PAPER_BG_COLOR = "#141922"
PLOT_BG_COLOR = "#1c232e"
DEFAULT_MARGIN = {"t": 60, "b": 40, "l": 60, "r": 20}
PIE_MARGIN = {"t": 80, "b": 20, "l": 50, "r": 50}

UTILITY_CATEGORIES = ["Gas", "Eletric", "Water/Sewage", "Trash", "Internet"]
FOOD_CATEGORIES = ["Food", "Takeout"]
CAR_CATEGORIES = ["Car/Gas", "Trailer"]
HOUSE_EXCLUDED_CATEGORIES = ["Tools"]
STORE_VENDERS = [
    "Home Depot",
    "Amazon",
    "Kroger",
    "Lowes",
    "Menards",
    "Walmart",
    "Sams",
    "Costco",
    "Game Stores",
    "Kohl's",
    "Harbor Freight Tools",
    "Microcenter",
]
SUBSCRIPTION_VENDERS = [
    "Spotify",
    "Peacock TV",
    "USMobile",
    "Net10",
    "Netflix",
    "Diseny Plus",
    "Anthropic",
]
CHART_ITEMS: list[tuple[Column, list[str]]] = [
    (Column.CATEGORY, UTILITY_CATEGORIES),
    (Column.CATEGORY, FOOD_CATEGORIES),
    (Column.CATEGORY, CAR_CATEGORIES),
    (Column.CATEGORY, HOUSE_EXCLUDED_CATEGORIES),
    (Column.VENDER, STORE_VENDERS),
    (Column.VENDER, SUBSCRIPTION_VENDERS),
]


class DataLoader:
    """Load workbook data and generate plots."""

    def __init__(self, workbook_path: Path, redact_values: bool = False) -> None:
        """Create new DataLoader instance."""
        self.workbook_path = workbook_path
        self.redact_values = redact_values
        self.df = DataFrame()
        self.options: dict[Column, list[str]] = {}

    def load_data(self) -> None:
        """Load data and dropdown options from workbook path."""
        xls = pd.ExcelFile(self.workbook_path)
        self.df = _load_dataframe(xls)
        self.options = _load_options(xls, self.df)
        _warn_missing_chart_items(self.options)

    def get_plots(self) -> list[Figure]:
        """Generate list of plots based on loaded data."""
        return [
            _monthly_net_bar_graph(
                self.df,
                Column.PAYMENT_TYPE,
                self.options[Column.PAYMENT_TYPE],
                "Monthly Net",
                self.redact_values,
            ),
            _treemap(
                self.df,
                Column.PROJECT,
                self.options[Column.PROJECT],
                Column.CATEGORY,
                HOUSE_EXCLUDED_CATEGORIES,
                "Total Spent On House",
                "House Project Total",
                self.redact_values,
            ),
            _monthly_line_graph(
                self.df,
                Column.CATEGORY,
                UTILITY_CATEGORIES,
                "Utility Cost",
                self.redact_values,
            ),
            _monthly_line_graph(
                self.df,
                Column.CATEGORY,
                FOOD_CATEGORIES,
                "Food Costs",
                self.redact_values,
            ),
            _monthly_line_graph(
                self.df,
                Column.CATEGORY,
                CAR_CATEGORIES,
                "Car & Trailer Costs",
                self.redact_values,
            ),
            _monthly_stacked_bar_graph(
                self.df,
                Column.VENDER,
                STORE_VENDERS,
                "Stores",
                self.redact_values,
            ),
            _monthly_line_graph(
                self.df,
                Column.VENDER,
                SUBSCRIPTION_VENDERS,
                "Subscriptions",
                self.redact_values,
            ),
            _monthly_stacked_bar_graph(
                self.df,
                Column.PROJECT,
                self.options[Column.PROJECT],
                "House Projects",
                self.redact_values,
            ),
            _monthly_stacked_bar_graph(
                self.df,
                Column.CATEGORY,
                self.options[Column.CATEGORY],
                "Monthly Spending By Category",
                self.redact_values,
            ),
            _monthly_income_expenses_graph(self.df, "Income vs Expenses", self.redact_values),
            _cumulative_net_graph(self.df, "Cumulative Net Position", self.redact_values),
            _top_vender_bar_graph(
                self.df,
                self.options[Column.VENDER],
                "Top Venders",
                self.redact_values,
            ),
            _seasonality_graph(self.df, "Average Spend By Month", self.redact_values),
            _year_over_year_graph(self.df, "Year Over Year Comparison", self.redact_values),
            _project_timeline_graph(self.df, "Project Timeline"),
            _transaction_scatter_graph(self.df, "Transaction History", self.redact_values),
        ]

    def get_vender_pie_charts(self) -> list[Figure]:
        """Plot displaying vender pie charts."""
        return _yearly_pie_charts(
            self.df,
            Column.VENDER,
            self.options[Column.VENDER],
            self.redact_values,
        )

    def get_payment_type_pie_charts(self) -> list[Figure]:
        """Plot displaying payment pie charts."""
        return _yearly_pie_charts(
            self.df,
            Column.PAYMENT_TYPE,
            self.options[Column.PAYMENT_TYPE],
            self.redact_values,
        )

    def get_project_pie_charts(self) -> list[Figure]:
        """Plot displaying project pie charts."""
        return _yearly_pie_charts(
            self.df,
            Column.PROJECT,
            self.options[Column.PROJECT],
            self.redact_values,
        )

    def get_category_pie_charts(self) -> list[Figure]:
        """Plot displaying category pie charts."""
        return _yearly_pie_charts(
            self.df,
            Column.CATEGORY,
            self.options[Column.CATEGORY],
            self.redact_values,
        )

    def get_stats(self) -> list[tuple[str, str]]:
        """Generate titles and stats values within a list."""
        stats: list[tuple[str, str]] = [
            ("Amount Spent on tools", f"${_sum_tools(self.df)}"),
            ("Average Monthly Spend", f"${_avg_monthly_spend(self.df)}"),
            ("Largest Single Purchase This Year", _largest_purchase(self.df)),
            ("Months With Negative Net", str(_months_negative_net(self.df))),
        ]
        savings = _savings_rate(self.df)
        if savings is not None:
            stats.append((f"Savings Rate ({savings[0]})", f"{savings[1] * 100:.1f}%"))
        return stats


def _sum_tools(df: DataFrame) -> float:
    tools_rows = df[df[Column.CATEGORY].str.contains("tools", case=False, na=False)]
    total = cast("float", tools_rows[Column.AMOUNT].sum())
    return round(abs(total), 2)


def _avg_monthly_spend(df: DataFrame) -> float:
    work = _add_date_columns(df)
    monthly = cast(
        "DataFrame",
        work.loc[work[Column.AMOUNT] < 0].groupby("MonthDate", as_index=False)[Column.AMOUNT].sum(),
    )
    if monthly.empty:
        return 0.0
    return round(cast("float", monthly[Column.AMOUNT].abs().sum()) / len(monthly), 2)


def _largest_purchase(df: DataFrame) -> str:
    work = _add_date_columns(df)
    purchases = work.loc[work[Column.AMOUNT] < 0]
    years = sorted({int(y) for y in purchases["Year"].dropna().unique()})
    if not years:
        return "None"
    purchases = purchases.loc[purchases["Year"] == years[-1]]
    if purchases.empty:
        return "None"
    row = purchases.loc[purchases[Column.AMOUNT].idxmin()]
    date_label = cast("pd.Timestamp", row["Date"]).strftime("%b %Y")
    vender = row[Column.VENDER] if pd.notna(row[Column.VENDER]) else "Unknown"
    return f"${abs(cast('float', row[Column.AMOUNT]))} - {vender} ({date_label})"


def _months_negative_net(df: DataFrame) -> int:
    work = _add_date_columns(df)
    monthly = cast(
        "DataFrame",
        work.groupby("MonthDate", as_index=False)[Column.AMOUNT].sum(),
    )
    return int((monthly[Column.AMOUNT] < 0).sum())


def _savings_rate(df: DataFrame) -> tuple[int, float] | None:
    work = _add_date_columns(df)
    years = sorted({int(y) for y in work["Year"].dropna().unique()})
    if not years:
        return None
    year = years[-1]
    year_df = work.loc[work["Year"] == year]
    income = float(year_df.loc[year_df[Column.AMOUNT] > 0, Column.AMOUNT].sum())
    if income <= 0:
        return None
    net = float(year_df[Column.AMOUNT].sum())
    return year, net / income


def _prepare_filtered_df(
    df: DataFrame,
    column: Column,
    sort_items: list[str],
) -> DataFrame:
    filtered = df.loc[df[column].isin(sort_items)].copy()
    filtered["Date"] = pd.to_datetime(filtered[Column.SHEET_NAME], format="%y%m%d", errors="coerce")
    filtered["MonthDate"] = filtered["Date"].dt.to_period("M").dt.to_timestamp()
    return filtered


def _add_date_columns(df: DataFrame) -> DataFrame:
    work = df.copy()
    work["Date"] = pd.to_datetime(work[Column.SHEET_NAME], format="%y%m%d", errors="coerce")
    work["MonthDate"] = work["Date"].dt.to_period("M").dt.to_timestamp()
    work["Year"] = work["Date"].dt.year
    return work


def _finish_figure(
    fig: Figure,
    redact_values: bool,
    margin: dict[str, int] = DEFAULT_MARGIN,
) -> Figure:
    fig.update_layout(
        height=CHART_HEIGHT,
        paper_bgcolor=PAPER_BG_COLOR,
        plot_bgcolor=PLOT_BG_COLOR,
        margin=margin,
    )
    if redact_values:
        fig.update_yaxes(showticklabels=False)
    return fig


def _monthly_net_bar_graph(
    df: DataFrame,
    column: Column,
    sort_items: list[str],
    title: str,
    redact_values: bool,
) -> Figure:
    filtered = _prepare_filtered_df(df, column, sort_items)
    grouped = cast(
        "DataFrame",
        filtered.groupby("MonthDate", as_index=False).agg(Amount=(Column.AMOUNT, "sum")),
    ).sort_values("MonthDate")
    grouped["Amount"] = grouped[Column.AMOUNT].round(2)
    grouped["Color"] = np.where(grouped["Amount"] >= 0, "Positive", "Negative")
    fig = bar(
        grouped,
        x="MonthDate",
        y="Amount",
        color="Color",
        title=title,
        template="plotly_dark",
        labels={"MonthDate": "Date", "Amount": "Net Dollars"},
        color_discrete_map={"Positive": "#3fb950", "Negative": "#f85149"},
    )
    fig.update_traces(hovertemplate="Date: %{x|%b %Y}<br>Net: %{y}<extra></extra>")
    fig.update_layout(legend_title_text="")

    return _finish_figure(fig, redact_values)


def _treemap(  # noqa: PLR0917
    df: DataFrame,
    column: Column,
    sort_items: list[str],
    exclude_column: Column,
    exclude_items: list[str],
    title: str,
    root_title: str,
    redact_values: bool,
) -> Figure:
    filtered = df.loc[df[column].isin(sort_items) & ~df[exclude_column].isin(exclude_items)]
    grouped = (
        filtered.groupby(column, as_index=False)[Column.AMOUNT]
        .sum()
        .assign(
            Amount=lambda d: d[Column.AMOUNT].abs().round(2),
            Parent=root_title,
            Label=lambda d: d[column],
        )
    )

    fig = treemap(
        grouped,
        path=["Parent", "Label"],
        values="Amount",
        title=title,
        template="plotly_dark",
    )
    fig.update_traces(hovertemplate="Category: %{label}<br>Total: %{value}<extra></extra>")

    return _finish_figure(fig, redact_values)


def _monthly_stacked_bar_graph(
    df: DataFrame,
    column: Column,
    sort_items: list[str],
    title: str,
    redact_values: bool,
) -> Figure:
    filtered = _prepare_filtered_df(df, column, sort_items)
    filtered["Item"] = filtered[column]

    grouped = cast(
        "DataFrame",
        filtered.groupby(["MonthDate", "Item"], as_index=False).agg(Amount=(Column.AMOUNT, "sum")),
    ).sort_values("MonthDate")
    grouped["Amount"] = grouped[Column.AMOUNT].abs().round(2)

    fig = bar(
        grouped,
        x="MonthDate",
        y="Amount",
        color="Item",
        title=title,
        template="plotly_dark",
        labels={"MonthDate": "Date", "Amount": "Dollars", "Item": "Category"},
    )
    fig.update_traces(
        hovertemplate=("Item: %{fullData.name}<br>Date: %{x|%b %Y}<br>Amount: %{y}<extra></extra>"),
    )
    fig.update_layout(barmode="stack")

    return _finish_figure(fig, redact_values)


def _monthly_line_graph(
    df: DataFrame,
    column: Column,
    sort_items: list[str],
    title: str,
    redact_values: bool,
) -> Figure:
    filtered = _prepare_filtered_df(df, column, sort_items)
    filtered["Item"] = filtered[column]
    grouped = cast(
        "DataFrame",
        filtered.groupby(["MonthDate", "Item"], as_index=False).agg(Amount=(Column.AMOUNT, "sum")),
    ).sort_values("MonthDate")
    grouped["Amount"] = grouped[Column.AMOUNT].abs().round(2)
    fig = line(
        grouped,
        x="MonthDate",
        y="Amount",
        color="Item",
        title=title,
        template="plotly_dark",
        labels={"MonthDate": "Date", "Amount": "Dollars", "Item": "Category"},
    )
    fig.update_traces(
        hovertemplate=("Item: %{fullData.name}<br>Date: %{x|%b %Y}<br>Amount: %{y}<extra></extra>"),
    )
    return _finish_figure(fig, redact_values)


def _monthly_income_expenses_graph(
    df: DataFrame,
    title: str,
    redact_values: bool,
) -> Figure:
    work = _add_date_columns(df)
    income = cast(
        "DataFrame",
        work.loc[work[Column.AMOUNT] > 0]
        .groupby("MonthDate", as_index=False)[Column.AMOUNT]
        .sum()
        .assign(Amount=lambda d: d[Column.AMOUNT].round(2)),
    )
    income["Item"] = "Income"
    expenses = cast(
        "DataFrame",
        work.loc[work[Column.AMOUNT] < 0]
        .groupby("MonthDate", as_index=False)[Column.AMOUNT]
        .sum()
        .assign(Amount=lambda d: d[Column.AMOUNT].abs().round(2)),
    )
    expenses["Item"] = "Expenses"
    combined = cast("DataFrame", concat([income, expenses]).sort_values("MonthDate"))
    fig = line(
        combined,
        x="MonthDate",
        y="Amount",
        color="Item",
        title=title,
        template="plotly_dark",
        labels={"MonthDate": "Date", "Amount": "Dollars", "Item": "Type"},
    )
    fig.update_traces(
        hovertemplate="Type: %{fullData.name}<br>Date: %{x|%b %Y}<br>Amount: %{y}<extra></extra>",
    )
    return _finish_figure(fig, redact_values)


def _cumulative_net_graph(
    df: DataFrame,
    title: str,
    redact_values: bool,
) -> Figure:
    work = _add_date_columns(df)
    grouped = cast(
        "DataFrame",
        work.groupby("MonthDate", as_index=False)[Column.AMOUNT].sum(),
    ).sort_values("MonthDate")
    grouped["Amount"] = grouped[Column.AMOUNT].cumsum().round(2)
    fig = line(
        grouped,
        x="MonthDate",
        y="Amount",
        title=title,
        template="plotly_dark",
        labels={"MonthDate": "Date", "Amount": "Net Dollars"},
    )
    fig.update_traces(hovertemplate="Date: %{x|%b %Y}<br>Cumulative Net: %{y}<extra></extra>")
    return _finish_figure(fig, redact_values)


def _top_vender_bar_graph(
    df: DataFrame,
    options: list[str],
    title: str,
    redact_values: bool,
) -> Figure:
    work = df.loc[(df[Column.AMOUNT] < 0) & df[Column.VENDER].notna()]
    if options:
        work = work.loc[work[Column.VENDER].isin(options)]
    grouped = cast(
        "DataFrame",
        work.groupby(Column.VENDER, as_index=False)[Column.AMOUNT]
        .sum()
        .assign(Amount=lambda d: d[Column.AMOUNT].abs().round(2)),
    )
    top = grouped.sort_values("Amount", ascending=False).head(TOP_VENDER_LIMIT)
    fig = bar(
        top,
        x="Amount",
        y=Column.VENDER,
        orientation="h",
        title=title,
        template="plotly_dark",
        labels={"Amount": "Dollars", Column.VENDER: "Vender"},
    )
    fig.update_traces(hovertemplate="Vender: %{y}<br>Total: %{x}<extra></extra>")
    fig = _finish_figure(fig, redact_values=False)
    if redact_values:
        fig.update_xaxes(showticklabels=False)
    return fig


def _seasonality_graph(
    df: DataFrame,
    title: str,
    redact_values: bool,
) -> Figure:
    work = _add_date_columns(df)
    work = work.loc[work[Column.AMOUNT] < 0]
    monthly = cast(
        "DataFrame",
        work.groupby("MonthDate", as_index=False)[Column.AMOUNT]
        .sum()
        .assign(Amount=lambda d: d[Column.AMOUNT].abs().round(2)),
    )
    monthly["MonthOfYear"] = monthly["MonthDate"].dt.month
    grouped = cast(
        "DataFrame",
        monthly.groupby("MonthOfYear", as_index=False)["Amount"].mean(),
    ).sort_values("MonthOfYear")
    grouped["Amount"] = grouped["Amount"].round(2)
    grouped["Month"] = [
        pd.Period(year=2000, month=int(m), freq="M").strftime("%b") for m in grouped["MonthOfYear"]
    ]
    fig = bar(
        grouped,
        x="Month",
        y="Amount",
        title=title,
        template="plotly_dark",
        labels={"Month": "Month", "Amount": "Average Dollars"},
    )
    fig.update_traces(hovertemplate="Month: %{x}<br>Average Spend: %{y}<extra></extra>")
    return _finish_figure(fig, redact_values)


def _year_over_year_graph(
    df: DataFrame,
    title: str,
    redact_values: bool,
) -> Figure:
    work = _add_date_columns(df)
    work = work.loc[work[Column.AMOUNT] < 0]
    years = sorted({int(y) for y in work["Year"].dropna().unique()})
    work = work.loc[work["Year"].isin(years[-2:])]
    if not work.empty:
        work["Year"] = work["Year"].astype(int)
    monthly = cast(
        "DataFrame",
        work.groupby(["Year", "MonthDate"], as_index=False)[Column.AMOUNT]
        .sum()
        .assign(Amount=lambda d: d[Column.AMOUNT].abs().round(2)),
    )
    monthly["Month"] = monthly["MonthDate"].dt.month
    grouped = cast(
        "DataFrame",
        monthly.groupby(["Month", "Year"], as_index=False)["Amount"].sum(),
    ).sort_values(["Month", "Year"])
    grouped["Year"] = grouped["Year"].astype(str)
    fig = bar(
        grouped,
        x="Month",
        y="Amount",
        color="Year",
        title=title,
        template="plotly_dark",
        labels={"Month": "Month", "Amount": "Dollars", "Year": "Year"},
    )
    fig.update_traces(
        hovertemplate="Year: %{fullData.name}<br>Month: %{x}<br>Amount: %{y}<extra></extra>",
    )
    fig.update_layout(barmode="group")
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=[pd.Period(year=2000, month=m, freq="M").strftime("%b") for m in range(1, 13)],
    )
    return _finish_figure(fig, redact_values)


def _project_timeline_graph(df: DataFrame, title: str) -> Figure:
    work = _add_date_columns(df)
    work = work.loc[(work[Column.AMOUNT] < 0) & work[Column.PROJECT].notna()]
    grouped = cast(
        "DataFrame",
        work.groupby(Column.PROJECT, as_index=False).agg(
            Start=("MonthDate", "min"),
            End=("MonthDate", "max"),
            Amount=(Column.AMOUNT, "sum"),
        ),
    ).sort_values("Start")
    grouped["Amount"] = grouped["Amount"].abs().round(2)
    fig = go.Figure()
    for project, start, end, amount in grouped.itertuples(index=False, name=None):
        # Snap bars to whole months: first day of first active month through
        # the day after the last day of the last active month.
        bar_end = end + pd.offsets.MonthEnd(0) + pd.Timedelta(days=1)
        duration = (end.year - start.year) * 12 + end.month - start.month + 1
        fig.add_trace(
            go.Bar(
                orientation="h",
                y=[project],
                x=[bar_end],
                x0=[start],
                name=str(project),
                customdata=[(start, end, amount, duration)],
                hovertemplate=(
                    "Project: %{y}<br>Start: %{customdata[0]:%b %Y}<br>"
                    "End: %{customdata[1]:%b %Y}<br>"
                    "Duration: %{customdata[3]} mo<br>"
                    "Total: $%{customdata[2]:,.0f}<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        title=title,
        template="plotly_dark",
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="",
    )
    return _finish_figure(fig, redact_values=False)


def _transaction_scatter_graph(
    df: DataFrame,
    title: str,
    redact_values: bool,
) -> Figure:
    work = _add_date_columns(df)
    work = work.loc[work[Column.AMOUNT] < 0].dropna(subset=["Date"])
    work["Amount"] = work[Column.AMOUNT].abs().round(2)
    fig = scatter(
        work,
        x="Date",
        y="Amount",
        title=title,
        template="plotly_dark",
        labels={"Date": "Date", "Amount": "Amount ($) - Log Scale"},
    )
    fig.update_yaxes(type="log")
    fig.update_traces(
        customdata=list(
            zip(work[Column.VENDER].fillna(""), work[Column.CATEGORY].fillna(""), strict=True)
        ),
        marker={"size": 5, "opacity": 0.5},
        hovertemplate=(
            "Date: %{x|%b %d, %Y}<br>Amount: $%{y:.2f}<br>"
            "Vender: %{customdata[0]}<br>Category: %{customdata[1]}<extra></extra>"
        ),
    )
    return _finish_figure(fig, redact_values)


def _yearly_pie_charts(
    df: DataFrame,
    column: Column,
    options: list[str],
    redact_values: bool,
) -> list[Figure]:
    df = df.copy()
    df["Date"] = pd.to_datetime(df[Column.SHEET_NAME], format="%y%m%d", errors="coerce")
    df["Year"] = df["Date"].dt.year
    figures: list[Figure] = []

    for year, year_df in df.dropna(subset=["Year"]).groupby("Year"):
        grouped = cast("DataFrame", year_df.groupby(column, as_index=False)[Column.AMOUNT].sum())
        if options:
            grouped = grouped.loc[grouped[column].isin(options)]
        if grouped.empty:
            continue

        grouped["Amount"] = grouped[Column.AMOUNT].abs().round(2)
        total = grouped["Amount"].sum()
        percentages = grouped["Amount"] / total
        text = [
            label if pct >= MIN_PIE_CHART_PERCENT else ""
            for label, pct in zip(grouped[column], percentages, strict=False)
        ]
        year_int = int(cast("int", year))
        fig = pie(
            grouped,
            names=column,
            values="Amount",
            title=f"{column.value} - {year_int}",
            template="plotly_dark",
        )
        fig.update_traces(
            textinfo="text",
            text=text,
            hovertemplate=(
                "%{label}<br>Amount: $%{value:.2f}<br>Percent: %{percent}<extra></extra>"
            ),
        )
        fig.update_layout(uniformtext_minsize=10, uniformtext_mode="hide")
        figures.append(_finish_figure(fig, redact_values, margin=PIE_MARGIN))

    return figures


def _load_dataframe(xls: pd.ExcelFile) -> DataFrame:
    numeric_sheet_names = [s for s in xls.sheet_names if str(s).isdigit()]
    if not numeric_sheet_names:
        print("No numeric sheets found.")  # noqa: T201
        return pd.DataFrame()
    print(  # noqa: T201
        f"{len(numeric_sheet_names)} sheets spanning from "
        f"{min(numeric_sheet_names)}-{max(numeric_sheet_names)}",
    )

    dfs: list[DataFrame] = []
    for name in numeric_sheet_names:
        df = cast("DataFrame", xls.parse(name))
        # Normalize column names (prevents subtle bugs later)
        df.columns = [str(c).strip() for c in df.columns]
        # Add sheet name column
        df[Column.SHEET_NAME.value] = name
        dfs.append(df)

    return concat(dfs, ignore_index=True)


def _load_options(xls: pd.ExcelFile, df: DataFrame) -> dict[Column, list[str]]:
    data_df = DataFrame()
    if DATA_SHEET_NAME in xls.sheet_names:
        data_df = cast("DataFrame", xls.parse(DATA_SHEET_NAME))
        data_df.columns = [str(c).strip() for c in data_df.columns]
    else:
        print(f"No '{DATA_SHEET_NAME}' sheet found, using values from monthly sheets.")  # noqa: T201

    options: dict[Column, list[str]] = {}
    for column in OPTION_COLUMNS:
        if column in data_df.columns:
            values = data_df[column].dropna().astype(str).str.strip()
            options[column] = list(dict.fromkeys(v for v in values if v))
        elif column in df.columns:
            if not data_df.empty:
                print(f"No '{column}' column in '{DATA_SHEET_NAME}' sheet, using sheet values.")  # noqa: T201
            values = df[column].dropna().astype(str).str.strip()
            options[column] = sorted({v for v in values if v})
        else:
            options[column] = []
    return options


def _warn_missing_chart_items(options: dict[Column, list[str]]) -> None:
    for column, items in CHART_ITEMS:
        for item in items:
            if item not in options.get(column, []):
                print(f"Warning: chart item '{item}' not found in '{column}' options.")  # noqa: T201
