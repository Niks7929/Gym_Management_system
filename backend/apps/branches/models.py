from django.db import models
from django.utils import timezone

class Branch(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Branches"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class GymSetting(models.Model):
    gym_name = models.CharField(max_length=200, default='SETFIT Dark Rage Elite Fitness')
    tagline = models.CharField(max_length=255, default='Forged in Iron. Powered by Relentless Discipline.')
    announcement_bar = models.CharField(max_length=255, default='⚡ NEW MEMBER SPECIAL: Sign up today & receive 1 Free 1-on-1 Fitness Assessment + Customized Diet Chart!')
    hero_headline = models.CharField(max_length=255, default='UNLEASH YOUR INNER TITAN')
    hero_subtitle = models.TextField(default='Welcome to SETFIT DARK RAGE — the premier high-performance strength and conditioning fitness facility. Master-level coaching, state-of-the-art powerlifting equipment, and tailor-made nutrition plans.')
    hero_badge_text = models.CharField(max_length=200, default='Forged in Iron. Powered by Relentless Discipline.')
    hero_cta_primary = models.CharField(max_length=100, default='Claim Membership Pass')
    hero_cta_secondary = models.CharField(max_length=100, default='Member Portal Login')
    theme_accent = models.CharField(max_length=50, default='crimson') # crimson, gold, emerald, cyan, violet
    
    stat_access_hours = models.CharField(max_length=50, default='24/7')
    stat_equipment_text = models.CharField(max_length=50, default='100% Olympic')
    stat_trainers_count = models.CharField(max_length=50, default='15+')
    stat_members_count = models.CharField(max_length=50, default='5,000+')

    contact_email = models.EmailField(default='contact@setfitgym.com')
    contact_phone = models.CharField(max_length=50, default='+91 98765 00001')
    address = models.TextField(default='777 Titan Way, Iron District, Metropolis')
    currency_symbol = models.CharField(max_length=10, default='₹')
    upi_id = models.CharField(max_length=100, default='setfit@upi')
    date_format = models.CharField(max_length=30, default='YYYY-MM-DD')
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.gym_name
