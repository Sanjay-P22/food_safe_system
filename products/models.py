from decimal import Decimal

from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone


# ============================================================
# 1. FOOD PRODUCT MODEL
# ============================================================

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    product_id = models.CharField(max_length=50, unique=True)
    manufacturer = models.CharField(max_length=200)
    batch_number = models.CharField(max_length=100)
    ingredients = models.TextField()

    manufacturing_date = models.DateField()
    expiry_date = models.DateField()

    # Product image uploaded by the user/admin
    image = models.ImageField(
        upload_to="product_images/",
        blank=True,
        null=True,
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def discounted_price(self):
        discount = self.price * self.discount_percentage / Decimal("100")
        return (self.price - discount).quantize(Decimal("0.01"))

    @property
    def is_expired(self):
        return self.expiry_date < timezone.localdate()

    def __str__(self):
        return f"{self.product_name} ({self.product_id})"


# ============================================================
# 2. SUPPLY CHAIN EVENT MODEL
# ============================================================

class SupplyChainEvent(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="supply_chain_events",
    )

    event_type = models.CharField(
        max_length=100,
        default="Manufactured",
    )

    location = models.CharField(
        max_length=200,
        default="Not specified",
    )

    description = models.TextField(default="")

    event_date = models.DateTimeField(
        default=timezone.now,
    )

    previous_hash = models.CharField(
        max_length=64,
        default="0" * 64,
    )

    event_hash = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )

    def __str__(self):
        return f"{self.product.product_name} - {self.event_type}"


# ============================================================
# 3. CUSTOMER PROFILE MODEL
# ============================================================

class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )

    address_line = models.CharField(
        max_length=255,
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    postal_code = models.CharField(
        max_length=10,
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user}"


# ============================================================
# 4. FOOD ORDER MODEL
# ============================================================

class FoodOrder(models.Model):

    ORDER_STATUS_CHOICES = [
        ("PLACED", "Order Placed"),
        ("CONFIRMED", "Confirmed"),
        ("PACKED", "Packed"),
        ("SHIPPED", "Shipped"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="food_orders",
    )

    order_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
    )

    # Delivery details are stored as a snapshot.
    customer_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    delivery_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10)

    status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS_CHOICES,
        default="PLACED",
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = (
                f"FS-{timezone.now():%Y%m%d%H%M%S%f}"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number or f"Order {self.pk}"


# ============================================================
# 5. FOOD ORDER ITEM MODEL
# ============================================================

class FoodOrderItem(models.Model):

    order = models.ForeignKey(
        FoodOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    # Preserve the price charged when the order was placed.
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return (
            f"{self.product.product_name} "
            f"x {self.quantity} - {self.order.order_number}"
        )

