from datetime import datetime, date
from app.extensions import db

class GymSetting(db.Model):
    __tablename__ = 'gym_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_name = db.Column(db.String(120), default='SETFIT DARK RAGE')
    tagline = db.Column(db.String(200), default='BUILD YOUR POWER. DEFINE YOUR LIMITS.')
    announcement_bar = db.Column(db.String(255), default='⚡ NEW ATHLETE OFFER: Sign up today & receive 1 Free Fitness Assessment + Custom Diet Plan!')
    
    contact_email = db.Column(db.String(120), default='contact@setfitgym.com')
    contact_phone = db.Column(db.String(30), default='+91 98765 43210')
    address = db.Column(db.String(255), default='Near Pratibha Society, Karve Nagar, Pune, Maharashtra 411052')
    currency_symbol = db.Column(db.String(10), default='₹')
    upi_id = db.Column(db.String(100), default='setfit@upi')
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def phone(self):
        return self.contact_phone

    @property
    def email(self):
        return self.contact_email

    @property
    def upi_name(self):
        return self.gym_name

    def __repr__(self):
        return f"<GymSetting {self.gym_name}>"

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), default='Free Weights') # Cardio, Free Weights, Resistance Machines, Recovery
    serial_number = db.Column(db.String(100), unique=True, nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='Operational') # 'Operational', 'Under Maintenance', 'Decommissioned'
    location = db.Column(db.String(100), default='Main Weightlifting Arena')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    maintenances = db.relationship('EquipmentMaintenance', backref='equipment', lazy=True, cascade='all, delete-orphan')

    @property
    def condition(self):
        return self.status

    @property
    def brand(self):
        return self.name.split(' ')[0] if self.name else 'SETFIT'

    @property
    def last_serviced(self):
        return self.purchase_date

    def __repr__(self):
        return f"<Equipment {self.name} ({self.status})>"

class EquipmentMaintenance(db.Model):
    __tablename__ = 'equipment_maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False)
    
    maintenance_date = db.Column(db.Date, default=date.today, nullable=False)
    cost = db.Column(db.Float, default=0.0)
    technician_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Completed') # 'Scheduled', 'In Progress', 'Completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<EquipmentMaintenance Eq:{self.equipment_id} Date:{self.maintenance_date}>"

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), default='Supplements') # Supplements, Merchandise, Drinks, Accessories
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(50), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sales = db.relationship('ProductSale', backref='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.name} - ₹{self.price} (Stock: {self.stock_quantity})>"

class ProductSale(db.Model):
    __tablename__ = 'product_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='SET NULL'), nullable=True)
    
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(30), default='cash')
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)

    member = db.relationship('MemberProfile', backref='purchases')

    def __repr__(self):
        return f"<ProductSale Product:{self.product_id} Qty:{self.quantity} Total:₹{self.total_amount}>"

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id', ondelete='CASCADE'), nullable=False)
    
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    session_type = db.Column(db.String(50), default='Personal Training 1-on-1')
    status = db.Column(db.String(30), default='scheduled') # 'scheduled', 'completed', 'cancelled'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    member = db.relationship('MemberProfile', backref='appointments')
    trainer = db.relationship('TrainerProfile', backref='appointments')

    def __repr__(self):
        return f"<Appointment Member:{self.member_id} Trainer:{self.trainer_id} Date:{self.appointment_date}>"

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(30), default='info') # 'info', 'warning', 'success', 'danger'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f"<Notification User:{self.user_id} - {self.title}>"
