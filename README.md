
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

`uv run app.py [--file Path_To_Excel_file.xlsx] [--build]`

- `--file` path of excel file to parse (defaults to `assets/ExampleBudget.xlsx`)
- `--build` create zip file of html page to download

# Provided Synthetic Example

Example File: `uv run app.py`

Custom file name: `uv run app.py --file 'assets/Budget.xlsx`

Modify dev/run scripts (linux or windows)

# Example Budget Provided

Example Budget provided was AI generated to avoid personal information but still provide a plausible data log.

![Example car trailer costs plot](Docs/Images/car-trailer-costs.png)

![Example category plot](Docs/Images/category.png)

![Example food costs plot](Docs/Images/food-costs.png)

![Example house projects plot](Docs/Images/house-projects.png)

![Example image plot](Docs/Images/image.png)

![Example payment-type plot](Docs/Images/payment-type.png)

![Example project plot](Docs/Images/project.png)

![Example stores plot](Docs/Images/stores.png)

![Example subscriptions plot](Docs/Images/subscriptions.png)

![Example total spent on house plot](Docs/Images/total-spent-on-house.png)

![Example utility cost plot](Docs/Images/utility-cost.png)

![Example vender plot](Docs/Images/vender.png)
