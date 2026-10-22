import random


def detect_adulteration(food_type):
    """
    Demonstration-only adulteration screening.
    This does not use a trained AI model or laboratory testing.
    """

    food_type = food_type.strip().lower()

SUPPORTED_FOODS = [
    "milk",
    "rice",
    "wheat",
    "oil",
    "honey",
    "sugar",
    "turmeric",
    "chilli powder",
]


def detect_adulteration(food_type):
    """
    Validate a selected food type for the FoodSafe demonstration.

    This function does not run an AI model, analyze an image,
    detect adulteration, or establish food safety.
    """

    if not isinstance(food_type, str):
        food_type = ""

    food_type = " ".join(food_type.strip().lower().split())

    if food_type not in SUPPORTED_FOODS:
        return {
            "food_type": food_type.title() if food_type else "Unknown",
            "status": "Unsupported Food",
            "confidence": None,
            "message": (
                "Select a supported food type to continue. "
                "No adulteration analysis was performed."
            ),
            "is_demo": True,
        }

    return {
        "food_type": food_type.title(),
        "status": "Screening Model Not Configured",
        "confidence": None,
        "message": (
            "The food type was accepted, but no trained AI model "
            "is connected yet. No adulteration prediction was made. "
            "Visual screening alone cannot establish food safety."
        ),
        "is_demo": True,
    }

