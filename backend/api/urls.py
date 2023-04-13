from api.views import IngredientViewSet, TagViewSet, UserViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "api"

v1_router = DefaultRouter()
v1_router.register("users", UserViewSet)
v1_router.register("tags", TagViewSet)
v1_router.register("ingredients", IngredientViewSet)

urlpatterns = [
    path("v1/", include(v1_router.urls)),
    path("v1/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
