# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project overview

Budget Visualizer is a small Python app. It reads a personal budget Excel workbook, loads it with pandas, and serves a Dash page of Plotly charts (line, stacked bar, net bar, treemap, and yearly pie charts). With `--build` it can also export that page as a static-site zip through `dash2html`.

## Layout

| Path | Purpose |
| --- | --- |
| `app.py` | Entry point. Parses CLI args, builds the Dash layout (stats section plus plot sections), runs the server or the `dash2html` export. |
| `data_loader.py` | `DataLoader` class: loads the workbook into one DataFrame and builds every Plotly figure. Chart helpers are private module functions (`_monthly_line_graph`, `_monthly_stacked_bar_graph`, `_monthly_net_bar_graph`, `_treemap`, `_yearly_pie_charts`). |
| `spreadsheet_items.py` | `StrEnum`s for workbook columns and the allowed values of each dropdown column (`Vender`, `PaymentType`, `Category`, `Project`), plus `get_options()`. |
| `Assets/ExampleBudget.xlsx` | AI-generated synthetic workbook, safe to commit and use for testing. |
| `Assets/Budget.xlsx` | The owner's real budget. Git-ignored and **must never be committed**. |
| `Assets/styles.css` | Dark-theme page styles (`scroll-container`, `section`, `title-bar`, `grid-container`, `stat-pill`, ...). |
| `Dev/run.sh`, `Dev/run.bat` | Convenience launchers pointing at `Assets/Budget.xlsx`. |
| `Docs/Images/` | Screenshots of the example plots, referenced from `README.md`. |

## Setup and running

Uses [uv](https://docs.astral.sh/uv/) with Python 3.13 (`.python-version`, `requires-python >=3.13`).

```bash
uv sync                                                  # install deps
uv run app.py --file Assets/ExampleBudget.xlsx           # dev server at http://127.0.0.1:8050 (debug=True)
uv run app.py --file Assets/ExampleBudget.xlsx --build   # dash2html export on port 8050
```

In `--build` mode, open `http://127.0.0.1:8050/` first, then `http://127.0.0.1:8050/download_zip` to download `static_site.zip`.

Use `Assets/ExampleBudget.xlsx` for all testing. Don't read or print the contents of `Assets/Budget.xlsx`.

## Workbook format

- Only sheets whose names are all digits are loaded. The name is a `YYMMDD` date (e.g. `250131`) and is parsed with `format="%y%m%d"`. Other sheets, such as a `Data` sheet of dropdown lists, are ignored.
- Expected columns: `Entry`, `Amount`, `Vender`, `Payment Type`, `Category`, `Project`. Header whitespace is stripped. The loader adds `Sheet Name`.
- `Amount` is signed: expenses are negative and income is positive. Most charts plot `abs()`; the "Monthly Net" chart keeps the sign.

## Coding conventions

- Ruff with `select = ["ALL"]`, line length 100, double quotes (see `pyproject.toml`). Pyright runs in `standard` mode. Ruff and pyright are not project dependencies: run them through the editor extensions, or ad hoc with `uvx ruff check .`, `uvx ruff format .`, and `uvx pyright`.
- Every module and public function has a one-line docstring. Private helpers are prefixed with `_` and have no docstring.
- Full type hints everywhere. Filter lists are typed `list[Vender | PaymentType | Category | Project]`.
- Reference columns through the `Column` enum (`df[Column.AMOUNT]`), not string literals. The exceptions are derived columns such as `"Date"`, `"MonthDate"`, `"Item"`, and `"Year"`.
- Figures use `template="plotly_dark"`, set a custom `hovertemplate`, and call `_apply_redaction(fig, redact_values)` before being returned.
- `print` is allowed only with `# noqa: T201`.
- There is no test suite. To verify a change, run the app against the example workbook and check that it starts without errors.

## Common tasks

- **New vendor, category, project, or payment type:** add a member to the matching enum in `spreadsheet_items.py`. The value must match the workbook text exactly, including existing misspellings such as `"Eletric"`, `"Goverment"`, `"Widthhold"`, and `"Diseny Plus"`; fixing them would break matching against the workbook. If cSpell flags a new word, add it to `.vscode/settings.json`.
- **New chart:** add a figure to `DataLoader.get_plots()`, reusing an existing `_monthly_*` or `_treemap` helper where one fits. Add a new private helper only for a new chart type.
- **New page section:** add a `_create_plot_section(...)` or `_create_stats_section(...)` call to `app.layout` in `app.py`.
- **New stat:** add a `(label, value)` tuple to `DataLoader.get_stats()`.

## Known quirks

- **The stylesheet doesn't load on Linux.** Dash serves the lowercase `assets/` folder by default, but the CSS is in `Assets/`. On a case-sensitive filesystem `styles.css` is never loaded unless `Dash(__name__, assets_folder="Assets")` is set or the folder is renamed.
- `WORKBOOK_NAME` and `open_browser()` in `app.py` are unused.
- `REDACT_VALUES` in `app.py` is a hard-coded toggle, not a CLI flag. It hides y-axis tick labels so screenshots can be shared.
- "Vender" is the project's spelling throughout the code and the workbook. Keep it consistent.

## Git

- `main` is the primary branch. Work on feature branches and merge through PRs.
- Never commit `Assets/Budget.xlsx` or any other real financial data.
