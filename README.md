
# Budget Visualizer

Quick python project that:
- Grabs budget workbook data
- Parses data using Pandas
- Generate webpage of data using Dash
- Allows for Plotly plots and useful labels.

# Setup

1. Install [UV](https://docs.astral.sh/uv/getting-started/installation/)
2. Open terminal and run `uv sync`
3. AGENTS.md file provided for agentic workflows

# Command Structure

`uv run app.py [--file Path_To_Excel_file.xlsx] [--build] [--redact]`

- `--file` path of excel file to parse (defaults to `assets/ExampleBudget.xlsx`)
- `--build` create zip file of html page to download
- `--redact` hide y-axis value labels so the page can be shared as screenshots

# Provided Synthetic Example

Example File: `uv run app.py`

Custom file name: `uv run app.py --file 'assets/Budget.xlsx`

Modify dev/run scripts (linux or windows)

# Example Budget Provided

Example Budget provided was AI generated to avoid personal information but still provide a plausible data log.

![Example car trailer costs plot](Docs/Images/car-trailer-costs.png)

![Example category plot](Docs/Images/category.png)

![Example monthly category spending plot](Docs/Images/category-monthly.png)

![Example cumulative net plot](Docs/Images/cumulative-net.png)

![Example food costs plot](Docs/Images/food-costs.png)

![Example house projects plot](Docs/Images/house-projects.png)

![Example income vs expenses plot](Docs/Images/income-expenses.png)

![Example monthly net plot](Docs/Images/monthly-net.png)

![Example payment-type plot](Docs/Images/payment-type.png)

![Example project plot](Docs/Images/project.png)

![Example project timeline plot](Docs/Images/project-timeline.png)

![Example average spend by month plot](Docs/Images/seasonality.png)

![Example stats](Docs/Images/stats.png)

![Example stores plot](Docs/Images/stores.png)

![Example subscriptions plot](Docs/Images/subscriptions.png)

![Example top venders plot](Docs/Images/top-venders.png)

![Example total spent on house plot](Docs/Images/total-spent-on-house.png)

![Example transaction history plot](Docs/Images/transactions.png)

![Example utility cost plot](Docs/Images/utility-cost.png)

![Example vender plot](Docs/Images/vender.png)

![Example year over year plot](Docs/Images/year-over-year.png)
