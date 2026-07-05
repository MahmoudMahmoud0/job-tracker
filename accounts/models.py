from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(PermissionsMixin, AbstractBaseUser):
    pass