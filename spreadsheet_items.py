"""All possible items within workbook.

Could be dynamically generated from Data sheet at the cost of less strict types
"""

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


class Vender(StrEnum):
    """Vender enum type."""

    HOME_DEPOT = "Home Depot"
    AMAZON = "Amazon"
    KROGER = "Kroger"
    LOWES = "Lowes"
    MENARDS = "Menards"
    WALMART = "Walmart"
    SAMS = "Sams"
    STAPLES = "Staples"
    TARGET = "Target"
    EUFY = "Eufy"
    BANK = "Bank"
    NET10 = "Net10"
    SPOTIFY = "Spotify"
    DUKE_ENERGY = "Duke Energy"
    GCWW = "GCWW"
    ALTAFIBER = "Altafiber"
    GOVERNMENT = "Goverment"
    AAA = "AAA"
    PARENTS = "Parents"
    RUMPKE = "Rumpke"
    UDF = "UDF"
    BP = "BP"
    FAST_FOOD = "Fast Food"
    OTHER = "Other"
    WALGREENS = "Walgreens"
    WIDTHHOLD = "Widthhold"
    PEACOCK_TV = "Peacock TV"
    COSTCO = "Costco"
    US_MOBILE = "USMobile"
    NETFLIX = "Netflix"
    STEAM = "Steam"
    UNITY = "Unity"
    RANDOM_STORES = "Random Stores"
    GAME_STORES = "Game Stores"
    EYE_CARE = "Eye Care"
    KOHLS = "Kohl's"
    HARBOR_FREIGHT_TOOLS = "Harbor Freight Tools"
    BAKER_CABINETS = "Baker Cabinets"
    DISNEY_PLUS = "Diseny Plus"
    CABINETS_COM = "Cabinets com"
    CLOUDFLARE = "Cloudflare"
    PRUSA = "Prusa"
    ANTHROPIC = "Anthropic"


class PaymentType(StrEnum):
    """PaymentType enum type."""

    CAPITALONE_MASTER = "CapitalOne Master"
    GEVISA = "GEVisa"
    ECHECK = "ECheck"
    CHECK = "Check"
    DIRECT_DEPOSIT = "Direct Deposit"
    WIDTHHOLD = "Widthhold"


class Category(StrEnum):
    """Category enum type."""

    HOUSE_IMPROVEMENT = "House/Improvement"
    FOOD = "Food"
    TAKEOUT = "Takeout"
    GAS = "Gas"
    ELECTRIC = "Eletric"
    WATER_SEWAGE = "Water/Sewage"
    INTERNET = "Internet"
    TOOLS = "Tools"
    CAR_GAS = "Car/Gas"
    WANTS = "Wants"
    INSURANCE = "Insurance"
    TAX = "Tax"
    HOUSEHOLD_ITEMS = "Household Items"
    HEALTH = "Health"
    MORTGAGE = "Mortgage"
    SAVINGS = "Savings"
    INCOME = "Income"
    TRASH = "Trash"
    SUBSCRIPTIONS = "Subscriptions"
    APPLIANCES = "Appliances"
    TRAILER = "Trailer"
    CONSUMABLE = "Consumable"
    FURNITURE = "Furniture"
    GIFT = "Gift"
    GAME_DEV = "Game Dev"
    SOCIAL = "Social"
    DONATION = "Donation"
    GAMBLE = "Gamble"
    BONUS = "Bonus"


class Project(StrEnum):
    """Project enum type."""

    HOUSE_PAINT = "House Paint"
    HOUSE_ROOF = "House Roof"
    HOUSE_YARD = "House Yard"
    MAIN_BATHROOM = "Main Bathroom"
    ATTIC_CLEANUP = "Attic Cleanup"
    KITCHEN_REMODEL = "Kitchen Remodel"
    MASTER_BEDROOM_BATH = "Master Bedroom/Bath"
    WINDOWS = "Windows"
    BASEMENT_SINK = "Basement Sink"
    FAMILY_ROOM_CLEANUP = "Family Room Cleanup"
    ROOM_IMPROVEMENT = "Room Improvement"
    SECURITY = "Security"
    ELETRIC = "Eletric"
    BASEMENT_CLEANUP = "Basement Cleanup"
    GUTTER_FIX = "Gutter Fix"
    GARAGE_LIGHTING = "Garage Lighting"
    LIVINGROOM_MOLDING_LIGHTING = "Livingroom Molding Lighting"
    LIVINGROOM_MOLDING = "Livingroom Molding"
    GENERAL_PLUMBING = "General Plumbing"
    BASEMENT_REMODEL = "Basement Remodel"
    FLOORING = "Flooring"
    GARDEN = "Garden"


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


def get_options(column: Column) -> list[str]:
    """Get all options within a column as a list."""
    match column:
        case Column.VENDER:
            return [v.value for v in Vender]
        case Column.PAYMENT_TYPE:
            return [p.value for p in PaymentType]
        case Column.CATEGORY:
            return [c.value for c in Category]
        case Column.PROJECT:
            return [p.value for p in Project]
    return []
