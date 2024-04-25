from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            # Если пользователь с указанным email не найден, возвращаем None
            return None
        else:
            # Проверяем пароль и возвращаем пользователя, если пароль верен
            if user.check_password(password):
                return user
        # Если пароль неверен, или пользователь не найден, возвращаем None
        return None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
