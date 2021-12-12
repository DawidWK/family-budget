from rest_framework import (
    generics,
    authentication,
    mixins,
    permissions,
    viewsets,
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from core.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    CategorySerializer,
    BudgetSerializer,
)
from core import models


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrive and return authentication user"""
        return self.request.user


class BaseModelViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """Base viewset for Budget and Category"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class CategoryViewSet(BaseModelViewSet):
    """Base viewset for user owned recipe atrribiutes"""

    queryset = models.Category.objects.all()
    serializer_class = CategorySerializer


class BudgetViewSet(BaseModelViewSet):
    """Budget viewset"""

    queryset = models.Budget.objects.all()
    serializer_class = BudgetSerializer

    def get_queryset(self):
        """Returns only queryset where authenticated user is author
        or is in shared_with field"""
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only", 0))
        )

        queryset = self.queryset.filter(
            Q(shared_with=self.request.user) | Q(author=self.request.user)
        )
        if assigned_only:
            queryset = queryset.filter(author=self.request.user)

        return queryset

    def perform_create(self, serializer):
        """Set author to authenticated user"""
        serializer.save(author=self.request.user)
