"""Main app control."""

import argparse
import os
import webbrowser
from pathlib import Path
from threading import Timer

from dash import Dash, dcc, html
from dash2html import dash2html
from plotly.graph_objs import Figure

from data_loader import DataLoader

DEFAULT_WORKBOOK = Path(__file__).parent / "assets" / "ExampleBudget.xlsx"
REDACT_VALUES = False
PORT = 8050
BROWSER_OPEN_DELAY_SECONDS = 1.0


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
    args = parser.parse_args()
    workbook_path: Path = args.file
    create_build = args.build

    data_loader = DataLoader(workbook_path, REDACT_VALUES)
    data_loader.load_data()
    app = Dash(__name__)
    app.layout = html.Div(
        [
            _create_stats_section("Stats", data_loader.get_stats()),
            _create_plot_section("Plots", data_loader.get_plots()),
            _create_plot_section("Yearly Vender Summary", data_loader.get_vender_pie_charts()),
            _create_plot_section("Yearly Category Summary", data_loader.get_category_pie_charts()),
            _create_plot_section(
                "Yearly Payment Summary",
                data_loader.get_payment_type_pie_charts(),
            ),
            _create_plot_section("Yearly Project Summary", data_loader.get_project_pie_charts()),
        ],
        className="scroll-container",
    )
    # Debug reloader re-runs this script in a child process; only open from the parent
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        Timer(BROWSER_OPEN_DELAY_SECONDS, open_browser).start()

    if create_build:
        app.run_server = app.run  # pyright: ignore[reportAttributeAccessIssue]
        dash2html(app, port=PORT)
    else:
        app.run(debug=True, port=PORT)


def _create_plot_section(title: str, plots: list[Figure]) -> html.Div:
    return html.Div(
        [
            html.Div(title, className="title-bar"),
            html.Div(
                [dcc.Graph(figure=fig, className="graph") for fig in plots],
                className="grid-container",
            ),
        ],
        className="section",
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
    )


def open_browser() -> None:
    """Auto open browser."""
    webbrowser.open(f"http://127.0.0.1:{PORT}/")


if __name__ == "__main__":
    run_app()
