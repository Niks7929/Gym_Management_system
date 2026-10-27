from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='member', **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    RECEPTIONIST = 'receptionist', 'Receptionist'
    TRAINER = 'trainer', 'Trainer'
    MEMBER = 'member', 'Member'

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=191)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.MEMBER)
    
    # Optional branch relationship (nullable for global admin)
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role}) - {self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
