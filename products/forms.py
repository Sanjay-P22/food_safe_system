from django import forms
from django.core.exceptions import ValidationError
from .models import Product, SupplyChainEvent


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_name",
            "product_id",
            "manufacturer",
            "batch_number",
            "ingredients",
            "manufacturing_date",
            "expiry_date",
            "price",
            "discount_percentage",
            "image",
        ]

        widgets = {
            "product_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter product name",
            }),
            "product_id": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter unique product ID",
            }),
            "manufacturer": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter manufacturer name",
            }),
            "batch_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter batch number",
            }),
            "ingredients": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter product ingredients",
            }),
            "manufacturing_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "expiry_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter price",
                "min": "0",
                "step": "0.01",
            }),
            "discount_percentage": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter discount percentage",
                "min": "0",
                "max": "100",
                "step": "0.01",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
        }

    def clean_product_name(self):
        value = self.cleaned_data.get("product_name", "").strip()

        if not value:
            raise ValidationError("Product name is required.")

        return value

    def clean_product_id(self):
        value = self.cleaned_data.get("product_id", "").strip()

        if not value:
            raise ValidationError("Product ID is required.")

        existing = Product.objects.filter(product_id=value)

        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise ValidationError(
                "This Product ID is already registered."
            )

        return value

    def clean_manufacturer(self):
        value = self.cleaned_data.get("manufacturer", "").strip()

        if not value:
            raise ValidationError("Manufacturer is required.")

        return value

    def clean_batch_number(self):
        value = self.cleaned_data.get("batch_number", "").strip()

        if not value:
            raise ValidationError("Batch number is required.")

        return value

    def clean_ingredients(self):
        value = self.cleaned_data.get("ingredients", "").strip()

        if not value:
            raise ValidationError("Ingredients are required.")

        return value

    def clean_price(self):
        price = self.cleaned_data.get("price")

        if price is not None and price < 0:
            raise ValidationError("Price cannot be negative.")

        return price

    def clean_discount_percentage(self):
        discount = self.cleaned_data.get("discount_percentage")

        if discount is not None and not (0 <= discount <= 100):
            raise ValidationError(
                "Discount must be between 0 and 100 percent."
            )

        return discount

    def clean(self):
        cleaned_data = super().clean()

        manufacturing_date = cleaned_data.get("manufacturing_date")
        expiry_date = cleaned_data.get("expiry_date")

        if manufacturing_date and expiry_date:
            if expiry_date <= manufacturing_date:
                self.add_error(
                    "expiry_date",
                    "Expiry date must be later than manufacturing date.",
                )

        return cleaned_data


class SupplyChainEventForm(forms.ModelForm):
    class Meta:
        model = SupplyChainEvent
        fields = [
            "product",
            "event_type",
            "location",
            "description",
            "event_date",
        ]
