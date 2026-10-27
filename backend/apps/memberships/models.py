import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class DurationType(models.TextChoices):
    MONTHLY = 'monthly', 'Monthly (30 Days)'
    QUARTERLY = 'quarterly', 'Quarterly (90 Days)'
    HALF_YEARLY = 'half_yearly', 'Half-Yearly (180 Days)'
    YEARLY = 'yearly', 'Yearly (365 Days)'

class MembershipPlan(models.Model):
    name = models.CharField(max_length=150)
    duration_type = models.CharField(max_length=30, choices=DurationType.choices, default=DurationType.MONTHLY)
    duration_days = models.PositiveIntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default='')
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - ${self.price} ({self.duration_days} days)"

class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    PENDING_VERIFICATION = 'pending_verification', 'Pending Verification'
    EXPIRED = 'expired', 'Expired'
    PENDING = 'pending', 'Pending'
    CANCELLED = 'cancelled', 'Cancelled'

class Subscription(models.Model):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    status = models.CharField(max_length=30, choices=SubscriptionStatus.choices, default=SubscriptionStatus.PENDING_VERIFICATION)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-end_date']

    def __str__(self):
        return f"{self.member.full_name} - {self.plan.name} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        # Check auto expiry
        if self.end_date and self.end_date < timezone.now().date() and self.status == SubscriptionStatus.ACTIVE:
            self.status = SubscriptionStatus.EXPIRED
        super().save(*args, **kwargs)

class PaymentMethod(models.TextChoices):
    UPI = 'upi', 'UPI / Online Transfer'
    CASH = 'cash', 'Cash'
    CARD = 'card', 'Credit/Debit Card'
    BANK_TRANSFER = 'bank_transfer', 'Bank Wire'

class PaymentType(models.TextChoices):
    INITIAL = 'initial', 'Initial Registration'
    RENEWAL = 'renewal', 'Membership Renewal'
    ADDON = 'addon', 'Add-on / Personal Training'

class PaymentStatus(models.TextChoices):
    COMPLETED = 'completed', 'Completed / Verified'
    PENDING_VERIFICATION = 'pending_verification', 'Pending Bank Verification'
    PENDING = 'pending', 'Pending'
    REJECTED = 'rejected', 'Rejected'
    FAILED = 'failed', 'Failed'

class Payment(models.Model):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.UPI)
    payment_type = models.CharField(max_length=30, choices=PaymentType.choices, default=PaymentType.INITIAL)
    status = models.CharField(max_length=30, choices=PaymentStatus.choices, default=PaymentStatus.PENDING_VERIFICATION)
    invoice_number = models.CharField(max_length=100, unique=True, blank=True)
    utr_number = models.CharField(max_length=100, blank=True, default='')
    upi_vpa = models.CharField(max_length=100, blank=True, default='')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')
    transaction_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-transaction_date']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            prefix = "INV"
            unique_part = uuid.uuid4().hex[:8].upper()
            date_str = timezone.now().strftime("%Y%m%d")
            self.invoice_number = f"{prefix}-{date_str}-{unique_part}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.member.full_name} (₹{self.amount}) [{self.status}]"

class EnquiryStatus(models.TextChoices):
    NEW = 'new', 'New Lead'
    CONTACTED = 'contacted', 'Contacted / WhatsApp Sent'
    CONVERTED = 'converted', 'Converted to Member'
    REJECTED = 'rejected', 'Not Interested'

class Enquiry(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=20)
    fitness_goal = models.CharField(max_length=200, blank=True, default='General Fitness')
    preferred_time = models.CharField(max_length=100, blank=True, default='Morning (6 AM - 10 AM)')
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=30, choices=EnquiryStatus.choices, default=EnquiryStatus.NEW)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone}) - {self.status}"
