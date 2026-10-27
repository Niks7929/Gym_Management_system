from django.db import models
from django.conf import settings
from django.utils import timezone

class TrainerClientAssignment(models.Model):
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_assignments')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_assignments')
    start_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('trainer', 'member')
        ordering = ['-start_date']

    def __str__(self):
        return f"Trainer {self.trainer.full_name} -> Client {self.member.full_name}"

class WorkoutPlan(models.Model):
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_workout_plans')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_plans')
    title = models.CharField(max_length=200)
    goal = models.CharField(max_length=200, default='Muscle Building & Strength')
    exercises_schedule = models.JSONField(default=list, help_text="List of workout days with exercise routines")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.member.full_name}"

class DietPlan(models.Model):
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_diet_plans')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diet_plans')
    title = models.CharField(max_length=200)
    daily_calories = models.PositiveIntegerField(default=2200)
    macros = models.JSONField(default=dict, help_text="e.g. {'protein': '160g', 'carbs': '220g', 'fats': '60g'}")
    meals_schedule = models.JSONField(default=list, help_text="List of daily meals: breakfast, lunch, snacks, dinner")
    guidelines = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.member.full_name} ({self.daily_calories} kcal)"
