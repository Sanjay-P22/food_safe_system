
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and Dashboard
    path("", views.home, name="home"),
    path("welcome/", views.welcome, name="welcome"),

    # Authentication
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("signup/", views.signup, name="signup"),

    # Product Catalogue
    path(
        "catalogue/<slug:product_slug>/",
        views.catalogue_product_detail,
        name="catalogue_product_detail",
    ),

    # Product Management
    path("register/", views.register_product, name="register_product"),
    path("list/", views.product_list, name="product_list"),
    path("search/", views.search_products, name="search_products"),
    path(
        "detail/<int:product_id>/",
        views.product_detail,
        name="product_detail",
    ),

    # Supply Chain and Blockchain
    path(
        "supply-chain/add/",
        views.add_supply_chain_event,
        name="add_supply_chain_event",
    ),

    # AI Food Detection
    path(
        "ai-detection/",
        views.ai_detection,
        name="ai_detection",
    ),

    # IoT Temperature Monitoring
    path(
        "iot-monitoring/",
        views.iot_temperature_monitor,
        name="iot_monitoring",
    ),

    # User Profile
    path("profile/", views.profile, name="profile"),
]
