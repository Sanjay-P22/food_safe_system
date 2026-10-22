from django.templatetags.static import static


def get_product_image(product):
    """Return an appropriate existing image for a product."""

    if hasattr(product, "product_name"):
        name = str(product.product_name).lower()
    else:
        name = str(product).lower()

    image_mapping = [
        (("apple",), "images/apples.jpg"),
        (
            (
                "milk", "curd", "yogurt", "yoghurt",
                "butter", "cheese", "paneer",
                "buttermilk", "cream", "ghee",
            ),
            "images/milk.jpg",
        ),
        (("oil",), "images/oil.jpg"),
        (
            (
                "wheat", "flour", "atta", "ragi",
                "millet", "quinoa", "oats",
                "barley", "poha", "semolina",
            ),
            "images/wheat.jpg",
        ),
        (("rice",), "images/rice.jpg"),
        (
            (
                "banana", "mango", "orange", "grapes",
                "papaya", "pineapple", "watermelon",
                "guava", "pomegranate", "pear", "kiwi",
                "strawberry", "blueberry", "lemon",
                "jackfruit",
            ),
            "images/apples.jpg",
        ),
    ]

    for keywords, image_path in image_mapping:
        if any(keyword in name for keyword in keywords):
            return static(image_path)

    return static("images/default.jpg")