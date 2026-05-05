from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User, Profile
from catalog.models import Category, Product, Stock
from orders.models import Cart, Order


class FullFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name="PC", slug="pc")
        self.product = Product.objects.create(
            category=self.cat,
            name="GPU RTX",
            slug="gpu-rtx",
            description="x",
            price=Decimal("1000.00"),
        )
        Stock.objects.create(product=self.product, quantity=5)

    def test_register_creates_user_profile_cart_and_logs_in(self):
        resp = self.client.post(reverse("register"), {
            "email": "test@example.com",
            "username": "tester",
            "password1": "StrongPass!2345",
            "password2": "StrongPass!2345",
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get(email="test@example.com")
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertTrue(Cart.objects.filter(user=user).exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_login_with_email(self):
        User.objects.create_user(email="a@b.com", username="ab", password="StrongPass!234")
        resp = self.client.post(reverse("login"), {
            "email": "a@b.com",
            "password": "StrongPass!234",
        })
        self.assertEqual(resp.status_code, 302)

    def test_full_purchase_flow(self):
        User.objects.create_user(email="x@y.com", username="xy", password="StrongPass!234")
        self.client.post(reverse("login"), {"email": "x@y.com", "password": "StrongPass!234"})

        r = self.client.post(reverse("orders:add_to_cart", args=[self.product.id]), {"quantity": 2})
        self.assertEqual(r.status_code, 302)

        r = self.client.get(reverse("orders:cart"))
        self.assertContains(r, "GPU RTX")

        r = self.client.post(reverse("orders:checkout"), follow=True)
        self.assertEqual(r.status_code, 200)

        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, "paid")
        self.assertEqual(order.total_price, Decimal("2000.00"))
        self.assertEqual(order.items.count(), 1)

        self.product.stock.refresh_from_db()
        self.assertEqual(self.product.stock.quantity, 3)

    def test_cart_requires_login(self):
        r = self.client.get(reverse("orders:cart"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login", r.url)
