import base64
from decimal import Decimal
from io import BytesIO

import qrcode

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .catalogue import (
    get_catalogue,
    get_catalogue_product,
    CATEGORY_LABELS,
)
from .forms import ProductForm, SupplyChainEventForm
from .integrity import calculate_event_hash, verify_hash_chain
from .image_helper import get_product_image
from .iot_monitoring import generate_temperature_reading
from .models import (
    Product,
    SupplyChainEvent,
    CustomerProfile,
    FoodOrder,
    FoodOrderItem,
)


# ============================================================
# PRODUCT IMAGE AND PRICE HELPERS
# ============================================================

def get_matching_catalogue_product(product):
    """
    Find the catalogue entry that matches a registered product.
    Matching by product ID keeps catalogue images consistent.
    """
    for item in get_catalogue():
        if item["product_id"] == product.product_id:
            return item

    return None


def prepare_product_image(product):
    """
    Image priority:
    1. Uploaded image saved on the product.
    2. Matching catalogue image.
    3. Existing image helper fallback.
    """
    if product.image and product.image.name:
        product.display_image = product.image.url
        return product

    catalogue_item = get_matching_catalogue_product(product)

    if catalogue_item:
        product.display_image = catalogue_item["image_url"]
    else:
        product.display_image = get_product_image(
            product.product_name
        )

    return product


def prepare_demo_product(product):
    """
    Prepare display values for registered products.

    Saved prices are preferred. If a registered product has no
    saved price, use its matching catalogue price when available.
    Otherwise, use a clearly identifiable demonstration price.
    """
    prepare_product_image(product)

    catalogue_item = get_matching_catalogue_product(product)

    if product.price > Decimal("0.00"):
        original_price = product.price
        discount = product.discount_percentage

    elif catalogue_item and catalogue_item.get("price") is not None:
        original_price = Decimal(
            str(catalogue_item["price"])
        )
        discount = Decimal(
            str(catalogue_item.get("discount_percentage", 0))
        )

    else:
        original_price = Decimal(
            str(round(100 + (product.id * 25), 2))
        )
        discount = Decimal(
            str(10 + (product.id % 4) * 5)
        )
        product.is_demo_price = True

    discounted_price = (
        original_price
        * (Decimal("100") - discount)
        / Decimal("100")
    ).quantize(Decimal("0.01"))

    product.demo_original_price = original_price
    product.demo_discount = discount
    product.demo_price = discounted_price

    return product


# ============================================================
# HOME AND DASHBOARD
# ============================================================

@login_required(login_url="login")
def home(request):
    return redirect("welcome")


@login_required(login_url="login")
def welcome(request):
    catalogue = get_catalogue()

    query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()

    if query:
        query_lower = query.casefold()

        catalogue = [
            item for item in catalogue
            if query_lower in item["product_name"].casefold()
            or query_lower in item["product_id"].casefold()
            or query_lower in item["category_label"].casefold()
            or query_lower in item["manufacturer"].casefold()
            or query_lower in item["batch_number"].casefold()
        ]

    if selected_category:
        catalogue = [
            item for item in catalogue
            if item["category"] == selected_category
        ]

    paginator = Paginator(catalogue, 24)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "products": page_obj,
        "query": query,
        "selected_category": selected_category,
        "category_choices": CATEGORY_LABELS.items(),
        "catalogue_count": len(get_catalogue()),
        "registered_products_count": Product.objects.count(),
        "supply_chain_events_count": SupplyChainEvent.objects.count(),
        "quotes": [
            "Food Safety Is Everyone's Responsibility.",
            "Trust Every Product. Verify Every Journey.",
            "From Farm to Fork, Every Step Matters.",
            "Safe Food, Healthy Future.",
        ],
    }

    return render(request, "welcome.html", context)


# ============================================================
# CATALOGUE PRODUCT DETAILS
# ============================================================

@login_required(login_url="login")
def catalogue_product_detail(request, product_slug):
    product = get_catalogue_product(product_slug)

    if product is None:
        messages.error(
            request,
            "Product not found in the catalogue.",
        )
        return redirect("welcome")

    return render(
        request,
        "products/catalogue_product_detail.html",
        {
            "product": product,
            "product_image": product["image_url"],
        },
    )


# ============================================================
# PRODUCT REGISTRATION
# ============================================================

@login_required(login_url="login")
def register_product(request):
    product_slug = request.GET.get(
        "catalogue",
        "",
    ).strip()

    demo_product = (
        get_catalogue_product(product_slug)
        if product_slug
        else None
    )

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            product = form.save()

            messages.success(
                request,
                f"{product.product_name} registered successfully!",
            )

            return redirect("product_list")

        messages.error(
            request,
            "Registration failed. Please correct the errors below.",
        )

    else:
        initial = {}

        if demo_product:
            initial = {
                "product_name": demo_product["product_name"],
                "product_id": demo_product["product_id"],
                "manufacturer": demo_product["manufacturer"],
                "batch_number": demo_product["batch_number"],
                "ingredients": demo_product["ingredients"],
                "manufacturing_date": (
                    demo_product["manufacturing_date"]
                ),
                "expiry_date": demo_product["expiry_date"],
                "price": demo_product.get("price", ""),
                "discount_percentage": (
                    demo_product.get("discount_percentage", 0)
                ),
            }

        form = ProductForm(initial=initial)

    context = {
        "form": form,
        "catalogue_product": demo_product,
        "catalogue_image": (
            demo_product["image_url"]
            if demo_product
            else ""
        ),
    }

    return render(
        request,
        "products/register_product.html",
        context,
    )


# ============================================================
# REGISTERED PRODUCT LIST
# ============================================================

@login_required(login_url="login")
def product_list(request):
    products = Product.objects.all().order_by("-id")

    for product in products:
        prepare_demo_product(product)

    return render(
        request,
        "products/product_list.html",
        {"products": products},
    )


# ============================================================
# REGISTERED PRODUCT DETAILS, QR AND INTEGRITY
# ============================================================

@login_required(login_url="login")
def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
    )

    events = list(
        product.supply_chain_events.order_by("id")
    )

    # No events means integrity has not yet been verified.
    if not events:
        integrity_status = "NOT_YET_VERIFIED"
        integrity_message = (
            "No supply-chain events have been recorded yet. "
            "Add events before verifying the hash chain."
        )
        integrity_valid = False

    elif verify_hash_chain(product):
        integrity_status = "VALID"
        integrity_message = (
            "The recorded supply-chain events passed the "
            "hash-chain consistency check."
        )
        integrity_valid = True

    else:
        integrity_status = "INVALID"
        integrity_message = (
            "The supply-chain records failed the hash-chain "
            "verification check. Review the event records."
        )
        integrity_valid = False

    # Build the URL encoded in the QR code.
    product_url = request.build_absolute_uri(
        reverse(
            "product_detail",
            kwargs={"product_id": product.id},
        )
    )

    qr_code_base64 = ""

    try:
        qr = qrcode.QRCode(
            version=1,
            box_size=8,
            border=4,
        )
        qr.add_data(product_url)
        qr.make(fit=True)

        qr_image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")

        qr_code_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

    except Exception:
        messages.warning(
            request,
            "The QR code could not be generated.",
        )

    prepare_demo_product(product)

    context = {
        "product": product,
        "events": events,
        "integrity_verified": integrity_valid,
        "integrity_valid": integrity_valid,
        "integrity_status": integrity_status,
        "integrity_message": integrity_message,
        "qr_code": qr_code_base64,
        "qr_base64": qr_code_base64,
        "product_image": product.display_image,
    }

    return render(
        request,
        "products/product_detail.html",
        context,
    )


# ============================================================
# SUPPLY-CHAIN EVENT CREATION
# ============================================================

@login_required(login_url="login")
def add_supply_chain_event(request):
    if request.method == "POST":
        form = SupplyChainEventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)

            previous_event = (
                SupplyChainEvent.objects
                .filter(product=event.product)
                .order_by("-id")
                .first()
            )

            event.previous_hash = (
                previous_event.event_hash
                if previous_event
                else "0" * 64
            )

            event.event_hash = ""
            event.save()

            event.event_hash = calculate_event_hash(event)
            event.save(update_fields=["event_hash"])

            messages.success(
                request,
                "Supply-chain event added successfully!",
            )

            return redirect(
                "product_detail",
                product_id=event.product.id,
            )

        messages.error(
            request,
            "Please correct the form errors.",
        )

    else:
        form = SupplyChainEventForm()

    return render(
        request,
        "products/add_supply_chain_event.html",
        {"form": form},
    )


# ============================================================
# AI FOOD SCREENING
# ============================================================

@login_required(login_url="login")
def ai_detection(request):
    from .ai_detection import detect_adulteration

    result = None

    if request.method == "POST":
        food_type = request.POST.get("food_type", "")
        result = detect_adulteration(food_type)

    return render(
        request,
        "products/ai_detection.html",
        {"result": result},
    )



# ============================================================
# USER SIGNUP
# ============================================================

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            CustomerProfile.objects.get_or_create(user=user)
            login(request, user)

            messages.success(
                request,
                "Your account was created successfully!",
            )

            return redirect("welcome")

    else:
        form = UserCreationForm()

    return render(
        request,
        "registration/signup.html",
        {"form": form},
    )


# ============================================================
# CUSTOMER PROFILE
# ============================================================

@login_required(login_url="login")
def profile(request):
    customer_profile, created = (
        CustomerProfile.objects.get_or_create(
            user=request.user
        )
    )

    if request.method == "POST":
        customer_profile.phone_number = request.POST.get(
            "phone_number", ""
        ).strip()

        customer_profile.address_line = request.POST.get(
            "address_line", ""
        ).strip()

        customer_profile.city = request.POST.get(
            "city", ""
        ).strip()

        customer_profile.state = request.POST.get(
            "state", ""
        ).strip()

        customer_profile.postal_code = request.POST.get(
            "postal_code", ""
        ).strip()

        if not customer_profile.phone_number:
            messages.error(
                request,
                "Please enter your phone number.",
            )

        elif not customer_profile.address_line:
            messages.error(
                request,
                "Please enter your delivery address.",
            )

        elif not customer_profile.city:
            messages.error(
                request,
                "Please enter your city.",
            )

        elif not customer_profile.postal_code:
            messages.error(
                request,
                "Please enter your PIN code.",
            )

        else:
            customer_profile.save()

            messages.success(
                request,
                "Your profile was updated successfully.",
            )

            return redirect("profile")

    return render(
        request,
        "products/profile.html",
        {
            "user": request.user,
            "profile": customer_profile,
        },
    )


# ============================================================
# PLACE FOOD ORDER
# ============================================================

@login_required(login_url="login")
def place_order(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
    )

    customer_profile, created = (
        CustomerProfile.objects.get_or_create(
            user=request.user
        )
    )

    if product.is_expired:
        messages.error(
            request,
            "This product has expired and cannot be ordered.",
        )
        return redirect(
            "product_detail",
            product_id=product.id,
        )

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", "1"))
        except (TypeError, ValueError):
            quantity = 0

        if quantity < 1 or quantity > 100:
            messages.error(
                request,
                "Enter a quantity between 1 and 100.",
            )
            return redirect(
                "place_order",
                product_id=product.id,
            )

        customer_name = request.POST.get(
            "customer_name", ""
        ).strip()

        phone_number = request.POST.get(
            "phone_number", ""
        ).strip()

        delivery_address = request.POST.get(
            "delivery_address", ""
        ).strip()

        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()

        if not all([
            customer_name,
            phone_number,
            delivery_address,
            city,
            postal_code,
        ]):
            messages.error(
                request,
                "Please complete all required delivery details.",
            )
            return redirect(
                "place_order",
                product_id=product.id,
            )

        if product.price <= Decimal("0.00"):
            messages.error(
                request,
                "This product does not have a valid saved price. "
                "Please update its price before ordering.",
            )
            return redirect(
                "product_detail",
                product_id=product.id,
            )

        unit_price = product.discounted_price

        total_amount = (
            unit_price * quantity
        ).quantize(Decimal("0.01"))

        with transaction.atomic():
            order = FoodOrder.objects.create(
                user=request.user,
                customer_name=customer_name,
                phone_number=phone_number,
                delivery_address=delivery_address,
                city=city,
                state=state,
                postal_code=postal_code,
                total_amount=total_amount,
                status="PLACED",
            )

            FoodOrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                discount_percentage=product.discount_percentage,
            )

        messages.success(
            request,
            f"Order {order.order_number} placed successfully!",
        )

        return redirect(
            "order_detail",
            order_id=order.id,
        )

    prepare_product_image(product)

    return render(
        request,
        "products/place_order.html",
        {
            "product": product,
            "profile": customer_profile,
            "product_image": product.display_image,
        },
    )


# ============================================================
# CUSTOMER ORDER HISTORY
# ============================================================

@login_required(login_url="login")
def order_history(request):
    orders = (
        FoodOrder.objects
        .filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    return render(
        request,
        "products/order_history.html",
        {"orders": orders},
    )


# ============================================================
# ORDER DETAILS AND TRACKING
# ============================================================

@login_required(login_url="login")
def order_detail(request, order_id):
    order = get_object_or_404(
        FoodOrder.objects.prefetch_related("items__product"),
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "products/order_detail.html",
        {"order": order},
    )


# ============================================================
# IOT TEMPERATURE MONITORING
# ============================================================

@login_required(login_url="login")
def iot_temperature_monitor(request):
    # This currently generates simulated readings, not physical sensor data.
    reading = generate_temperature_reading()

    product = Product.objects.filter(
        product_id="FS-TEST-001"
    ).first()

    event = None

    if product:
        previous_event = (
            SupplyChainEvent.objects
            .filter(product=product)
            .order_by("-id")
            .first()
        )

        previous_hash = (
            previous_event.event_hash
            if previous_event
            else "0" * 64
        )

        event = SupplyChainEvent(
            product=product,
            event_type="IoT Temperature Monitoring",
            location="Food Storage",
            description=(
                f"Temperature: {reading['temperature']} °C | "
                f"Status: {reading['status']} | "
                f"Message: {reading['message']} | "
                f"Reading time: {reading['timestamp']}"
            ),
            previous_hash=previous_hash,
        )

        event.save()

        event.event_hash = calculate_event_hash(event)
        event.save(update_fields=["event_hash"])

        messages.info(
            request,
            f"IoT reading saved for {product.product_name}.",
        )

    else:
        messages.warning(
            request,
            "No demonstration product found. Register a product "
            "with product ID FS-TEST-001 to save IoT events.",
        )

    return render(
        request,
        "products/iot_monitoring.html",
        {
            "reading": reading,
            "product": product,
            "event": event,
        },
    )


# ============================================================
# SEARCH REGISTERED PRODUCTS
# ============================================================

@login_required(login_url="login")
def search_products(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.none()

    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query)
            | Q(product_id__icontains=query)
            | Q(batch_number__icontains=query)
            | Q(manufacturer__icontains=query)
        ).order_by("-id")

    for product in products:
        prepare_demo_product(product)

    return render(
        request,
        "products/search_result.html",
        {
            "products": products,
            "query": query,
        },
    )