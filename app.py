"""Main app control."""

import argparse
import os
import webbrowser
from collections.abc import Sequence
from pathlib import Path
from threading import Timer
from typing import Any

from dash import Dash, dcc, html
from dash2html import dash2html
from plotly.graph_objs import Figure

from data_loader import DataLoader

DEFAULT_WORKBOOK = Path(__file__).parent / "assets" / "ExampleBudget.xlsx"
PORT = 8050
BROWSER_OPEN_DELAY_SECONDS = 1.0
# Dash's auto-generated Graph stub types config as a "Config" symbol that
# does not exist in plotly, so keep this Any-typed to satisfy pyright.
GRAPH_CONFIG: Any = {"displaylogo": False, "responsive": True}

YEARLY_SECTION_GETTERS = {
    "Yearly Vender Summary": DataLoader.get_vender_pie_charts,
    "Yearly Category Summary": DataLoader.get_category_pie_charts,
    "Yearly Payment Summary": DataLoader.get_payment_type_pie_charts,
    "Yearly Project Summary": DataLoader.get_project_pie_charts,
}


def run_app() -> None:
    """Run main dash app."""
    parser = argparse.ArgumentParser(description="Budget Visualizer")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_WORKBOOK,
        help="Path to the Excel workbook (default: assets/ExampleBudget.xlsx)",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Create build of html page",
    )
    parser.add_argument(
        "--redact",
        action="store_true",
        help="Hide y-axis value labels so the page can be shared as screenshots",
    )
    args = parser.parse_args()

    data_loader = DataLoader(args.file, args.redact)
    data_loader.load_data()
    app = Dash(__name__, title="Budget Visualizer")
    app.layout = _build_layout(data_loader)
    # Debug reloader re-runs this script in a child process; only open from the parent
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        Timer(BROWSER_OPEN_DELAY_SECONDS, open_browser).start()

    if args.build:
        # dash2html still calls the Dash 2-era run_server API, removed in Dash 4
        app.run_server = app.run  # pyright: ignore[reportAttributeAccessIssue]
        dash2html(app, port=PORT)
    else:
        app.run(debug=True, port=PORT)


def _build_layout(data_loader: DataLoader) -> html.Div:
    sections: list[tuple[str, html.Div]] = [
        ("Stats", _create_stats_section("Stats", data_loader.get_stats())),
        ("Plots", _create_plot_section("Plots", data_loader.get_plots())),
    ]
    sections.extend(
        (title, _create_plot_section(title, getter(data_loader)))
        for title, getter in YEARLY_SECTION_GETTERS.items()
    )
    return html.Div(
        [
            _create_header([title for title, _ in sections]),
            html.Div([section for _, section in sections], className="scroll-container"),
        ],
        className="app",
    )


def _create_header(titles: Sequence[str]) -> html.Div:
    return html.Div(
        [
            html.Span("Budget Visualizer", className="app-title"),
            html.Div(
                [
                    html.A(title, href=f"#{_anchor_id(title)}", className="nav-link")
                    for title in titles
                ],
                className="nav-links",
            ),
        ],
        className="app-header",
    )


def _create_plot_section(title: str, plots: list[Figure]) -> html.Div:
    return html.Div(
        [
            html.Div(title, className="title-bar"),
            html.Div(
                [
                    dcc.Graph(figure=figure, className="graph", config=GRAPH_CONFIG)
                    for figure in plots
                ],
                className="grid-container",
            ),
        ],
        className="section",
        id=_anchor_id(title),
    )


def _stat_pill(label: str, value: str) -> html.Div:
    return html.Div(
        [
            html.Span(f"{label}: ", className="stat-title"),
            html.Span(value, className="stat-value"),
        ],
        className="stat-pill",
    )


def _create_stats_section(title: str, values: list[tuple[str, str]]) -> html.Div:
    return html.Div(
        [
            html.Div(title, className="title-bar"),
            html.Div(
                [_stat_pill(label, value) for label, value in values],
                className="grid-container grid-container-single",
            ),
        ],
        className="section",
        id=_anchor_id(title),
    )


def _anchor_id(title: str) -> str:
    return title.casefold().replace(" ", "-")


def open_browser() -> None:
    """Auto open browser."""
    webbrowser.open(f"http://127.0.0.1:{PORT}/")


if __name__ == "__main__":
    run_app()
