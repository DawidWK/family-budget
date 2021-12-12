from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

router = DefaultRouter()
router.register("category", views.CategoryViewSet)
router.register("budget", views.BudgetViewSet)

urlpatterns = [
    path("user/create/", views.CreateUserView.as_view(), name="create"),
    path("user/token/", views.CreateTokenView.as_view(), name="token"),
    path("user/me/", views.ManageUserView.as_view(), name="me"),
    path("", include(router.urls)),
]
