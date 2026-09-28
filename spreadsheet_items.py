"""Workbook column names and the sheet holding dropdown options."""

from enum import StrEnum


class Column(StrEnum):
    """Column enum type."""

    ENTRY = "Entry"
    AMOUNT = "Amount"
    VENDER = "Vender"
    PAYMENT_TYPE = "Payment Type"
    CATEGORY = "Category"
    PROJECT = "Project"
    SHEET_NAME = "Sheet Name"


OPTION_COLUMNS = (Column.VENDER, Column.PAYMENT_TYPE, Column.CATEGORY, Column.PROJECT)
DATA_SHEET_NAME = "Data"

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
