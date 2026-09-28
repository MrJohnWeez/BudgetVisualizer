"""Load and parse csv data."""

from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
from pandas import DataFrame, concat
from plotly.express import bar, line, pie, treemap
from plotly.graph_objs import Figure

from spreadsheet_items import DATA_SHEET_NAME, OPTION_COLUMNS, Column

MIN_PIE_CHART_PERCENT = 0.005

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
        return [
            ("Amount Spent on tools", f"${_sum_tools(self.df)}"),
        ]


def _sum_tools(df: DataFrame) -> float:
    tools_rows = df[df[Column.CATEGORY].str.contains("tools", case=False, na=False)]
    total = cast("float", tools_rows[Column.AMOUNT].sum())
    return round(abs(total), 2)


def _prepare_filtered_df(
    df: DataFrame,
    column: Column,
    sort_items: list[str],
) -> DataFrame:
    filtered = df.loc[df[column].isin(sort_items)].copy()
    filtered["Date"] = pd.to_datetime(filtered[Column.SHEET_NAME], format="%y%m%d", errors="coerce")
    filtered["MonthDate"] = filtered["Date"].dt.to_period("M").dt.to_timestamp()
    return filtered


def _apply_redaction(fig: Figure, redact: bool) -> None:
    if redact:
        fig.update_yaxes(showticklabels=False)


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
        color_discrete_map={"Positive": "green", "Negative": "red"},
    )
    fig.update_traces(hovertemplate="Date: %{x|%b %Y}<br>Net: %{y}<extra></extra>")
    fig.update_layout(legend_title_text="")

    _apply_redaction(fig, redact_values)
    return fig


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

    _apply_redaction(fig, redact_values)
    return fig


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

    _apply_redaction(fig, redact_values)
    return fig


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
    _apply_redaction(fig, redact_values)
    return fig


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
        fig.update_layout(
            margin={"t": 80, "b": 20, "l": 50, "r": 50},
            height=700,
            uniformtext_minsize=10,
            uniformtext_mode="hide",
        )
        _apply_redaction(fig, redact_values)
        figures.append(fig)

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
