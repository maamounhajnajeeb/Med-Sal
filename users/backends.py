from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from typing import Any

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username: str | None = None, password: str | None = None, **kwargs: Any) -> User | None:
        try:
            print(username)
            user = User.objects.get(username=username)
        # if the email doesn't exist then we raise ValueError
        except User.DoesNotExist:
            raise ValueError("User Doesn't Exists")
        print(password)
        print(f"check password: {user.check_password(password)}")
        print(self.user_can_authenticate(user))
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
