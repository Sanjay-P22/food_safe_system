from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from products import views as product_views


def admin_logout_redirect(request):
    """
    Log out of Django Admin and return to the Admin login page.
    """
    from django.contrib.auth import logout

    logout(request)
    return redirect("/admin/login/")


urlpatterns = [
    # Django Admin
    path("admin/logout/", admin_logout_redirect, name="admin_logout"),
    path("admin/", admin.site.urls),

    # FoodSafe application
    path("products/", include("products.urls")),
    path("", product_views.home, name="home"),
    path("welcome/", product_views.welcome, name="welcome"),

    # Website authentication
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("signup/", product_views.signup, name="signup"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Password reset
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="products/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

