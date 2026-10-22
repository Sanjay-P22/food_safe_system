from datetime import date, timedelta
from itertools import product as cartesian_product
from decimal import Decimal
import hashlib


IMAGE_MAP = {
    "grains": [
        "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=700&q=80",
    ],
    "fruits": [
        "https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?auto=format&fit=crop&w=700&q=80",
    ],
    "vegetables": [
        "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?auto=format&fit=crop&w=700&q=80",
    ],
    "dairy": [
        "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=700&q=80",
    ],
    "bakery": [
        "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1585478259715-876acc5be8eb?auto=format&fit=crop&w=700&q=80",
    ],
    "meat": [
        "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=700&q=80",
    ],
    "seafood": [
        "https://images.unsplash.com/photo-1510130387422-82bed34b37e9?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=700&q=80",
    ],
    "eggs": [
        "https://images.unsplash.com/photo-1506976785307-8732e854ad03?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1518569656558-1f25e69d93d7?auto=format&fit=crop&w=700&q=80",
    ],
    "oils": [
        "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=700&q=80",
    ],
    "snacks": [
        "https://images.unsplash.com/photo-1621939514649-280e2aa7e6b9?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1566478989037-eec170784d0b?auto=format&fit=crop&w=700&q=80",
    ],
    "beverages": [
        "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1600271886742-f049cd451bba?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1513558161293-cdaf765edfd7?auto=format&fit=crop&w=700&q=80",
    ],
    "spices": [
        "https://images.unsplash.com/photo-1532336414038-cf19250c5757?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=700&q=80",
        "https://images.unsplash.com/photo-1509358271058-acd22cc93898?auto=format&fit=crop&w=700&q=80",
    ],
    "default": [
        "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=700&q=80",
    ],
}


CATEGORY_DATA = [
    ("grains", "Grains & Rice", [
        "Basmati Rice", "Brown Rice", "Organic Rice",
        "Sona Masoori Rice", "Red Rice", "Jasmine Rice",
        "Wheat Flour", "Millet", "Quinoa", "Rolled Oats",
        "Corn Flour", "Barley", "Ragi Flour", "Poha",
        "Semolina", "Pearl Millet",
    ]),
    ("fruits", "Fresh Fruits", [
        "Apple", "Banana", "Mango", "Orange", "Grapes",
        "Papaya", "Pineapple", "Watermelon", "Guava",
        "Pomegranate", "Pear", "Kiwi", "Strawberry",
        "Blueberry", "Lemon", "Jackfruit",
    ]),
    ("vegetables", "Vegetables", [
        "Tomato", "Potato", "Onion", "Carrot", "Cabbage",
        "Cauliflower", "Spinach", "Broccoli", "Cucumber",
        "Capsicum", "Brinjal", "Green Beans", "Beetroot",
        "Radish", "Pumpkin", "Green Peas",
    ]),
    ("dairy", "Dairy Products", [
        "Whole Milk", "Toned Milk", "Curd", "Greek Yogurt",
        "Butter", "Cheddar Cheese", "Paneer", "Buttermilk",
        "Cream", "Ghee", "Mozzarella Cheese",
    ]),
    ("bakery", "Bakery Products", [
        "White Bread", "Brown Bread", "Whole Wheat Bread",
        "Multigrain Bread", "Burger Bun", "Pizza Base",
        "Croissant", "Rusk", "Plain Cake", "Muffin",
    ]),
    ("meat", "Meat & Poultry", [
        "Chicken Breast", "Chicken Drumstick", "Chicken Mince",
        "Mutton", "Turkey", "Duck Meat", "Chicken Sausage",
    ]),
    ("seafood", "Fish & Seafood", [
        "Salmon", "Tuna", "Rohu Fish", "Catla Fish",
        "Pomfret", "Sardines", "Mackerel", "Prawns", "Crab",
    ]),
    ("eggs", "Eggs", [
        "Farm Eggs", "Free Range Eggs", "Organic Eggs",
        "Brown Eggs", "White Eggs", "Quail Eggs",
    ]),
    ("oils", "Cooking Oils", [
        "Sunflower Oil", "Groundnut Oil", "Olive Oil",
        "Mustard Oil", "Coconut Oil", "Rice Bran Oil",
        "Sesame Oil", "Soybean Oil",
    ]),
    ("snacks", "Snacks & Packaged Foods", [
        "Potato Chips", "Banana Chips", "Roasted Peanuts",
        "Mixed Nuts", "Popcorn", "Crackers", "Biscuits",
        "Cookies", "Granola Bar", "Namkeen",
    ]),
    ("beverages", "Beverages", [
        "Orange Juice", "Apple Juice", "Mango Juice",
        "Coconut Water", "Green Tea", "Black Tea",
        "Coffee", "Lemonade", "Mineral Water",
    ]),
    ("spices", "Spices & Seasonings", [
        "Turmeric Powder", "Chilli Powder", "Black Pepper",
        "Cumin Seeds", "Coriander Powder", "Cardamom",
        "Cinnamon", "Cloves", "Garam Masala",
    ]),
]


PACK_SIZES = [
    "250 g", "500 g", "1 kg", "2 kg", "5 kg",
    "250 ml", "500 ml", "1 litre", "2 litres",
]


# Indicative demonstration prices in INR, not verified retail prices.
BASE_PRICES = {
    "grains": Decimal("90.00"),
    "fruits": Decimal("70.00"),
    "vegetables": Decimal("45.00"),
    "dairy": Decimal("65.00"),
    "bakery": Decimal("55.00"),
    "meat": Decimal("180.00"),
    "seafood": Decimal("200.00"),
    "eggs": Decimal("75.00"),
    "oils": Decimal("140.00"),
    "snacks": Decimal("50.00"),
    "beverages": Decimal("60.00"),
    "spices": Decimal("80.00"),
}


PACK_MULTIPLIERS = {
    "250 g": Decimal("0.35"),
    "500 g": Decimal("0.65"),
    "1 kg": Decimal("1.00"),
    "2 kg": Decimal("1.90"),
    "5 kg": Decimal("4.50"),
    "250 ml": Decimal("0.35"),
    "500 ml": Decimal("0.65"),
    "1 litre": Decimal("1.00"),
    "2 litres": Decimal("1.90"),
}


def _image_for_product(category, name, pack_size):
    """Select a stable category image for each product variant."""
    images = IMAGE_MAP.get(category, IMAGE_MAP["default"])

    key = f"{category}|{name}|{pack_size}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(images)

    return images[index]


def _price_for_product(category, name, pack_size, sequence):
    """Generate a repeatable demo price for a catalogue item."""
    base_price = BASE_PRICES.get(category, Decimal("50.00"))
    multiplier = PACK_MULTIPLIERS.get(pack_size, Decimal("1.00"))

    # Stable small variation for different products.
    variation = Decimal(str(1 + ((sequence % 7) * 0.04)))

    price = (base_price * multiplier * variation).quantize(
        Decimal("0.01")
    )

    # Ensure every generated catalogue product has a positive price.
    return max(price, Decimal("1.00"))


def build_catalogue():
    catalogue = []
    sequence = 1
    today = date.today()

    for category, category_label, names in CATEGORY_DATA:
        for name, pack_size in cartesian_product(names, PACK_SIZES):
            product_name = f"{name} - {pack_size}"

            price = _price_for_product(
                category,
                name,
                pack_size,
                sequence,
            )

            discount_percentage = Decimal(
                str([0, 5, 10, 15, 20][sequence % 5])
            )

            discounted_price = (
                price * (
                    Decimal("1.00")
                    - discount_percentage / Decimal("100.00")
                )
            ).quantize(Decimal("0.01"))

            catalogue.append({
                "slug": f"{category}-{sequence:05d}",
                "product_name": product_name,
                "base_name": name,
                "product_id": f"FS-DEMO-{sequence:06d}",
                "batch_number": f"DEMO-BATCH-{sequence:06d}",
                "category": category,
                "category_label": category_label,
                "manufacturer": "FoodSafe Demo Foods",
                "ingredients": name,
                "manufacturing_date": today - timedelta(days=30),
                "expiry_date": today + timedelta(days=335),
                "image_url": _image_for_product(
                    category,
                    name,
                    pack_size,
                ),
                "price": price,
                "discount_percentage": discount_percentage,
                "discounted_price": discounted_price,
                "is_demo": True,
            })

            sequence += 1

    return catalogue


def get_catalogue():
    return build_catalogue()


def get_catalogue_product(product_slug):
    for item in build_catalogue():
        if item["slug"] == product_slug:
            return item

    return None


CATEGORY_LABELS = {
    slug: label
    for slug, label, _ in CATEGORY_DATA
}

