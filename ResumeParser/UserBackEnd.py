from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class UserBackEnd(ModelBackend):
    def authenticate(self,username=None, password=None, user_type=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username, user_type=user_type)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
