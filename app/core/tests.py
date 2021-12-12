from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models, serializers

CREATE_USER_URL = reverse("core:create")
TOKEN_URL = reverse("core:token")
ME_URL = reverse("core:me")
CATEGORY_URL = reverse("core:category-list")
BUDGET_URL = reverse("core:budget-list")


def create_sample_user(username="TestUsername", password="Password123!"):
    user = get_user_model().objects.create_user(username)
    user.set_password(password)
    user.save()

    return user


def create_sample_category(
    name="My Category",
):
    return models.Category.objects.create(name=name)


def create_sample_budget(
    author,
    category,
    name="My Budget",
    income=200.00,
    expenses=100.00,
):
    return models.Budget.objects.create(
        name=name,
        author=author,
        income=income,
        expenses=expenses,
        category=category,
    )


class TestModels(TestCase):
    def test_creating_category(self):
        category = models.Category.objects.create(name="Family")

        self.assertEqual(str(category), "Family")

    def test_creating_budget(self):
        user = create_sample_user()
        category = models.Category.objects.create(name="Family")

        data = {
            "name": "My budget",
            "author": user,
            "income": 1500.00,
            "expenses": 1000.00,
            "category": category,
        }

        budget = models.Budget.objects.create(**data)
        self.assertEqual(str(budget), data["name"])


class TestPublicAPI(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successfull"""
        payload = {
            "username": "TestUsername",
            "password": "Password123!",
            "password2": "Password123!",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test creating user that already exists fails"""
        payload = {
            "username": "TestUsername",
            "password": "Password123!",
            "password2": "Password123!",
        }
        create_sample_user()

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 8 characters"""
        payload = {
            "username": "TestUsername",
            "password": "pipi",
            "password2": "pipi",
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model()
            .objects.filter(username=payload["username"])
            .exists()
        )
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            "username": "TestUsername",
            "password": "Password123!",
        }
        create_sample_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        payload = {
            "username": "TestUsername",
            "password": "WrongPassword1",
        }

        create_sample_user()
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {
            "username": "TestUsername",
            "password": "Password123!",
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are equired"""
        payload = {
            "email": "",
            "password": "Password123!",
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.post(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateAPI(TestCase):
    def setUp(self):
        self.user = create_sample_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrioeving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "id": self.user.id,
                "username": self.user.username,
            },
        )

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            "password": "New_password123!",
            "password2": "New_password123!",
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_category_view(self):
        """Test retriving categories"""
        create_sample_category()
        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual((res.data["results"][0]["name"]), "My Category")

    def test_budget_view(self):
        """Test retrieving budgets"""
        user2 = create_sample_user("User2")
        category = create_sample_category()
        budget1 = create_sample_budget(author=self.user, category=category)
        budget2 = create_sample_budget(
            author=user2,
            category=category,
            name="My Budget 2",
        )
        budget2.shared_with.add(self.user)
        budget3 = create_sample_budget(
            author=user2, category=category, name="My budget 3"
        )

        res = self.client.get(BUDGET_URL)
        serializer1 = serializers.BudgetSerializer(budget1)
        serializer2 = serializers.BudgetSerializer(budget2)
        serializer3 = serializers.BudgetSerializer(budget3)

        self.assertEqual(len(res.data["results"]), 2)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_if_budget_author_is_set_to_authenticated_user(self):
        """Test seting author to budget"""
        category = create_sample_category()

        payload = {
            "name": "My Budget",
            "income": 2000.00,
            "expenses": 1300.00,
            "category": category.id,
        }

        res = self.client.post(BUDGET_URL, payload)
        self.assertEqual(res.data["author"], self.user.id)
