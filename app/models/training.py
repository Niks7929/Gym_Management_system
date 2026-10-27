from datetime import datetime, date
import json
from app.extensions import db

class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), default='Chest') # Chest, Back, Legs, Shoulders, Arms, Core, Cardio
    equipment_needed = db.Column(db.String(100), default='Barbell / Dumbbells')
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Exercise {self.name} ({self.category})>"

class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id', ondelete='SET NULL'), nullable=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    
    title = db.Column(db.String(120), nullable=False) # e.g. "Hypertrophy Push-Pull-Legs Split"
    goal = db.Column(db.String(100), default='Muscle Building')
    schedule_json = db.Column(db.Text, nullable=True) # Full schedule array stored as JSON
    
    start_date = db.Column(db.Date, default=date.today, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exercises = db.relationship('WorkoutExercise', backref='plan', lazy=True, cascade='all, delete-orphan')

    @property
    def description(self):
        return self.notes

    @property
    def days_per_week(self):
        return len(self.exercises) if self.exercises else 5

    @property
    def schedule_list(self):
        if self.schedule_json:
            try:
                return json.loads(self.schedule_json)
            except Exception:
                return []
        return []

    def set_schedule(self, schedule_data):
        self.schedule_json = json.dumps(schedule_data)

    def __repr__(self):
        return f"<WorkoutPlan {self.title} for Member:{self.member_id}>"

class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id', ondelete='CASCADE'), nullable=False)
    day_name = db.Column(db.String(30), default='Monday') # Monday, Day 1, etc.
    
    exercise_name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.String(20), default='4')
    reps = db.Column(db.String(30), default='8-12')
    rest_time = db.Column(db.String(30), default='90 sec')
    notes = db.Column(db.String(255), nullable=True)

    @property
    def day_number(self):
        return self.day_name

    @property
    def exercise(self):
        class _Ex:
            name = self.exercise_name
            target_muscle = "Primary Group"
        return _Ex()

    def __repr__(self):
        return f"<WorkoutExercise {self.exercise_name} ({self.sets}x{self.reps})>"

class DietPlan(db.Model):
    __tablename__ = 'diet_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id', ondelete='SET NULL'), nullable=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    
    title = db.Column(db.String(120), nullable=False) # e.g. "High Protein Lean Bulk Blueprint"
    daily_calories = db.Column(db.Integer, default=2800)
    protein_grams = db.Column(db.String(30), default='180g')
    carbs_grams = db.Column(db.String(30), default='320g')
    fats_grams = db.Column(db.String(30), default='70g')
    
    guidelines = db.Column(db.Text, nullable=True)
    meals_json = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    meals = db.relationship('DietMeal', backref='diet_plan', lazy=True, cascade='all, delete-orphan')

    @property
    def target_calories(self):
        return self.daily_calories

    @property
    def description(self):
        return self.guidelines

    @property
    def notes(self):
        return self.guidelines

    @property
    def goal(self):
        return "Athletic Nutrition"

    @property
    def meals_list(self):
        if self.meals_json:
            try:
                return json.loads(self.meals_json)
            except Exception:
                return []
        return []

    def set_meals(self, meals_data):
        self.meals_json = json.dumps(meals_data)

    def __repr__(self):
        return f"<DietPlan {self.title} ({self.daily_calories} kcal)>"

class DietMeal(db.Model):
    __tablename__ = 'diet_meals'
    
    id = db.Column(db.Integer, primary_key=True)
    diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plans.id', ondelete='CASCADE'), nullable=False)
    
    meal_time = db.Column(db.String(30), default='08:00 AM')
    meal_name = db.Column(db.String(80), default='Breakfast')
    items = db.Column(db.Text, nullable=False) # e.g., 6 Egg whites, 100g Oats, Banana
    calories = db.Column(db.Integer, default=550)
    macros = db.Column(db.String(100), default='P: 40g | C: 65g | F: 12g')

    @property
    def name(self):
        return self.meal_name

    @property
    def timing(self):
        return self.meal_time

    @property
    def food_items(self):
        return self.items

    def __repr__(self):
        return f"<DietMeal {self.meal_name} ({self.meal_time})>"

class TrainerMemberAssignment(db.Model):
    __tablename__ = 'trainer_members'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id', ondelete='CASCADE'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    
    assigned_date = db.Column(db.Date, default=date.today, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<TrainerMemberAssignment Trainer:{self.trainer_id} Member:{self.member_id}>"
