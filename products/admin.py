from django.contrib import admin
from django.utils import timezone

from .models import Product, SupplyChainEvent


# FoodSafe admin branding
admin.site.site_header = "FoodSafe Administration"
admin.site.site_title = "FoodSafe Admin Portal"
admin.site.index_title = "Food Safety Management Dashboard"


# Save Django's original admin dashboard view
_original_admin_index = admin.site.index


def foodsafe_admin_index(request, extra_context=None):
    today = timezone.localdate()

    context = {
        "total_products": Product.objects.count(),

        "total_events": SupplyChainEvent.objects.count(),

        "total_categories": (
            Product.objects.values("product_name")
            .distinct()
            .count()
        ),

        "expired_products": Product.objects.filter(
            expiry_date__lt=today
        ).count(),

        "recent_products": Product.objects.order_by("-id")[:5],

        "recent_events": (
            SupplyChainEvent.objects
            .select_related("product")
            .order_by("-id")[:5]
        ),
    }

    if extra_context:
        context.update(extra_context)

    return _original_admin_index(
        request,
        extra_context=context,
    )


# Activate the customised dashboard
admin.site.index = foodsafe_admin_index


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "product_id",
        "manufacturer",
        "batch_number",
        "manufacturing_date",
        "expiry_date",
    )

    search_fields = (
        "product_name",
        "product_id",
        "manufacturer",
        "batch_number",
    )

    list_filter = (
        "manufacturing_date",
        "expiry_date",
    )

    ordering = ("-id",)


@admin.register(SupplyChainEvent)
class SupplyChainEventAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "event_type",
        "location",
        "event_date",
    )

    search_fields = (
        "product__product_name",
        "event_type",
        "location",
    )

    list_filter = (
        "event_type",
        "event_date",
    )

    readonly_fields = (
        "previous_hash",
        "event_hash",
    )

    ordering = ("-id",)