import uuid
from http import HTTPStatus
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase
from django.urls import reverse

from users.forms import RegisterForm, UserPasswordChangeForm
from django.test import RequestFactory

from users.views import UserPasswordChangeView


class LogoutTestCase(TestCase):
    fixtures = [
        "fixtures/users_user.json"
    ]

    def test_logout(self):
        user = get_user_model().objects.get(pk=2)
        self.client.force_login(user)

        response = self.client.get(reverse("users:logout"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("users:login"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class LoginTestCase(TestCase):
    fixtures = [
        "fixtures/users_user.json"
    ]

    def test_get_login_form(self):
        response = self.client.get(reverse("users:login"))
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/login.html")
        self.assertEqual(context["title"], "Вход")

    def test_login_with_incorrect_credentials(self):
        data = [
            (
                {
                    "email": "user1@mail.ru",
                    "password": "1234"
                },
                ["Неверный адрес электронной почты или пароль"]
            ),
            (
                {
                    "email": "incorrect_email@mail.ru",
                    "password": "1234"
                },
                ["Неверный адрес электронной почты или пароль"]
            )
        ]

        for case in data:
            credentials = case[0]
            expected = case[1]
            with self.subTest(credentials=credentials):
                response = self.client.post(reverse("users:login"), credentials)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, "users/login.html")
                self.assertEqual(response.context["title"], "Вход")
                self.assertEqual(
                    response.context["form"].non_field_errors(),
                    expected
                )

    def test_login_with_correct_credentials(self):

        data = {
            "email": "user1@mail.ru",
            "password": "some_password"
        }

        response = self.client.post(reverse("users:login"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("home"))


class RegistrationTestCase(TestCase):
    fixtures = [
        "fixtures/users_user.json"
    ]

    def test_get_register_form(self):
        response = self.client.get(reverse("users:registration"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/registration.html")
        self.assertEqual(response.context["title"], "Регистрация")

    def test_register_duplicate_email(self):
        data = {
            "email": "user1@mail.ru",
            "password1": "some_password",
            "password2": "some_password",
        }
        form = RegisterForm(data)
        self.assertFalse(form.is_valid())

    def test_registration(self):
        data = {
            "email": "user_n@mail.ru",
            "password1": "some_password",
            "password2": "some_password"
        }
        response = self.client.post(reverse("users:registration"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("users:email_was_sent"))

        self.assertTrue(get_user_model().objects.filter(
            email=data["email"], is_active=False
        ).exists())

    @patch("django.core.cache.cache.set")
    def test_set_cache(self, mock_set):
        data = {
            "email": "user_n@mail.ru",
            "password1": "some_password",
            "password2": "some_password"
        }
        self.client.post(reverse("users:registration"), data)
        mock_set.assert_called()

    @patch("django.core.cache.cache.get")
    def test_register_confirm_when_user_in_cache(self, mock_get):
        user = get_user_model().objects.create(
            email="user_n@mail.ru",
            password="1234",
            is_active=False,
        )
        mock_get.return_value = {"user_id": user.pk}
        response = self.client.get(
            reverse(
                "users:register_confirm",
                kwargs={"token": uuid.uuid4().hex}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(get_user_model().objects.filter(
            email=user.email,
            is_active=True
        ).exists())

    @patch("django.core.cache.cache.get")
    def test_register_confirm_when_user_not_in_cache(self, mock_get):
        mock_get.return_value = None
        response = self.client.get(
            reverse(
                "users:register_confirm",
                kwargs={"token": uuid.uuid4().hex}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/invalid_link.html")
        self.assertEqual(response.context["title"], "Ссылка недействительна")


class ProfileTestCase(TestCase):
    fixtures = [
        "fixtures/users_user.json"
    ]

    def test_profile(self):
        user_id = 2
        user = get_user_model().objects.get(pk=user_id)
        self.client.force_login(user)
        response = self.client.get(reverse("users:profile", kwargs={"user_id": user_id}))
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertEqual(context["title"], "Профиль")
        self.assertEqual(len(context["form"].fields), 1)
        self.assertTrue("email" in context["form"].fields.keys())

    def test_profile_without_auth(self):
        user_id = 2
        response = self.client.get(reverse("users:profile", kwargs={"user_id": user_id}))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("users:login") + "?next=/users/profile/2"
        )


class UserPasswordChangeTestCase(TestCase):
    fixtures = [
        "fixtures/users_user.json"
    ]

    def setUp(self):
        user_id = 2
        self.user = get_user_model().objects.get(pk=user_id)
        self.client.force_login(self.user)

    def test_get_password_change_form(self):
        response = self.client.get(reverse(
            "users:password_change",
        ))
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/password_change.html")
        self.assertEqual(context["title"], "Смена пароля")
        self.assertEqual(type(context["form"]), UserPasswordChangeForm)

    def test_incorrect_old_password(self):
        user = get_user_model().objects.create(
            email="user_n@mail.ru",
        )
        user.set_password("some_password")
        user.save()

        data = {
            "old_password": "incorrect_password",
            "new_password1": "new_password",
            "new_password2": "new_password",
        }
        form = UserPasswordChangeForm(data)
        form.user = user
        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.error_messages["password_incorrect"],
            "Ваш старый пароль введен неправильно. Пожалуйста, введите его снова."
        )

    def test_mismatched_passwords(self):
        user = get_user_model().objects.create(
            email="user_n@mail.ru",
        )
        user.set_password("some_password")
        user.save()

        data = {
            "old_password": "some_password",
            "new_password1": "new_password1",
            "new_password2": "new_password2",
        }
        form = UserPasswordChangeForm(data)
        form.user = user
        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.error_messages["password_mismatch"],
            "Введенные пароли не совпадают."
        )

    def test_change_password(self):
        user = get_user_model().objects.create(
            email="user_n@mail.ru",
        )
        user.set_password("some_password")
        user.save()

        data = {
            "old_password": "some_password",
            "new_password1": "new_password",
            "new_password2": "new_password"
        }

        request_factory = RequestFactory()
        request = request_factory.post(reverse("users:password_change"), data)

        request.user = user
        session = SessionStore()
        request.session = session
        request.session['_auth_user_id'] = user.pk
        request.session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
        request.session.save()
        request._dont_enforce_csrf_checks = True

        view = UserPasswordChangeView()
        view.request = request
        response = view.post(request=request)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("users:password_change_done"))


class ResetPasswordTestCase(TestCase):
    def test_password_reset_get_form(self):
        response = self.client.get(reverse("users:password_reset"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed("users/password_reset.html")

    def test_password_reset_post_form(self):
        data = {
            "email": "user1@mail.ru"
        }
        response = self.client.post(reverse("users:password_reset"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("users:password_reset_done"))

    def test_password_reset_done(self):
        data = {
            "email": "user1@mail.ru"
        }
        response = self.client.post(reverse("users:password_reset"), data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/password_reset_done.html")

    def test_password_reset_complete(self):
        response = self.client.get(reverse("users:password_reset_complete"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/password_reset_complete.html")
