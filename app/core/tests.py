from django.test import TestCase
from core import models
from django.contrib.auth import get_user_model


class TestModels(TestCase):
    def create_sample_user(self):
        return get_user_model().objects.create_user(
            "test@gmail.com", "Password123!"
        )

    def test_creating_category(self):
        category = models.Category.objects.create(name="Family")

        self.assertEqual(str(category), "Family")

    def test_creating_budget(self):
        user = self.create_sample_user()
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
