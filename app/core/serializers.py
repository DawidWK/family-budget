from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from core import models


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""

    password2 = serializers.CharField(
        max_length=128, write_only=True, required=True
    )

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "password2": {"write_only": True, "min_length": 8},
        }

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"new_password2": _("The two password fields didn't match.")}
            )
        data.pop("password2")
        return data

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data["username"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update a user, settings the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    username = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = "__all__"


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Budget
        fields = (
            "id",
            "name",
            "author",
            "income",
            "expenses",
            "category",
            "shared_with",
        )
        read_only_fields = (
            "id",
            "author",
        )
