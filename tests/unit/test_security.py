"""Юнит-тесты для app.core.security — хэширование паролей и JWT-токены."""
import time

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


# ---------------------------------------------------------------------------
# Хэширование паролей
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = get_password_hash("secret")
        assert hashed != "secret"

    def test_correct_password_verifies(self):
        hashed = get_password_hash("correct-password")
        assert verify_password("correct-password", hashed) is True

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct-password")
        assert verify_password("wrong-password", hashed) is False

    def test_empty_password_verifies_own_hash(self):
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt использует случайную соль — одинаковый вход даёт разные хэши."""
        h1 = get_password_hash("same")
        h2 = get_password_hash("same")
        assert h1 != h2


# ---------------------------------------------------------------------------
# Access-токен
# ---------------------------------------------------------------------------

class TestAccessToken:
    def test_returns_string(self):
        token = create_access_token(subject=1, roles=["ROLE_USER"])
        assert isinstance(token, str)
        assert len(token) > 20

    def test_decoded_payload_has_correct_sub(self):
        token = create_access_token(subject=42, roles=[])
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "42"

    def test_decoded_payload_has_access_type(self):
        token = create_access_token(subject=1, roles=[])
        payload = decode_token(token)
        assert payload["type"] == "access"

    def test_decoded_payload_contains_roles(self):
        roles = ["ROLE_USER", "ROLE_ADMIN"]
        token = create_access_token(subject=1, roles=roles)
        payload = decode_token(token)
        assert payload["roles"] == roles

    def test_decoded_payload_has_exp_in_future(self):
        token = create_access_token(subject=1, roles=[])
        payload = decode_token(token)
        assert "exp" in payload
        # exp должен быть в будущем
        assert payload["exp"] > time.time()


# ---------------------------------------------------------------------------
# Refresh-токен
# ---------------------------------------------------------------------------

class TestRefreshToken:
    def test_returns_string(self):
        token = create_refresh_token(subject=1)
        assert isinstance(token, str)

    def test_decoded_payload_has_refresh_type(self):
        token = create_refresh_token(subject=1)
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

    def test_decoded_payload_has_correct_sub(self):
        token = create_refresh_token(subject=7)
        payload = decode_token(token)
        assert payload["sub"] == "7"

    def test_refresh_token_has_no_roles_field(self):
        token = create_refresh_token(subject=1)
        payload = decode_token(token)
        assert "roles" not in payload


# ---------------------------------------------------------------------------
# decode_token
# ---------------------------------------------------------------------------

class TestDecodeToken:
    def test_garbage_string_returns_none(self):
        assert decode_token("not.a.jwt") is None

    def test_empty_string_returns_none(self):
        assert decode_token("") is None

    def test_tampered_signature_returns_none(self):
        token = create_access_token(subject=1, roles=[])
        # Меняем последний символ — подпись становится невалидной
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        assert decode_token(tampered) is None
