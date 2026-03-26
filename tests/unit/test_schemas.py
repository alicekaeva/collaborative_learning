"""Юнит-тесты валидации Pydantic-схем."""
import pytest
from pydantic import ValidationError

from app.schemas.user import EarnPointsRequest
from app.schemas.auth import RegisterRequest


# ---------------------------------------------------------------------------
# EarnPointsRequest — ограничения поля points
# ---------------------------------------------------------------------------

class TestEarnPointsRequest:
    def test_valid_points(self):
        req = EarnPointsRequest(points=100)
        assert req.points == 100

    def test_minimum_valid_points(self):
        req = EarnPointsRequest(points=1)
        assert req.points == 1

    def test_maximum_valid_points(self):
        req = EarnPointsRequest(points=10000)
        assert req.points == 10000

    def test_zero_points_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            EarnPointsRequest(points=0)
        errors = exc_info.value.errors()
        assert any("greater than 0" in str(e) or "gt" in str(e) for e in errors)

    def test_negative_points_rejected(self):
        with pytest.raises(ValidationError):
            EarnPointsRequest(points=-50)

    def test_points_above_limit_rejected(self):
        with pytest.raises(ValidationError):
            EarnPointsRequest(points=10001)

    def test_missing_points_rejected(self):
        with pytest.raises(ValidationError):
            EarnPointsRequest()


# ---------------------------------------------------------------------------
# RegisterRequest — базовая валидация полей
# ---------------------------------------------------------------------------

class TestRegisterRequest:
    def test_valid_registration(self):
        req = RegisterRequest(
            email="alice@example.com",
            password="strongpass",
            full_name="Alice",
        )
        assert req.email == "alice@example.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="not-an-email", password="pass", full_name="Alice")

    def test_missing_email_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(password="pass", full_name="Alice")

    def test_missing_password_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="a@b.com", full_name="Alice")
