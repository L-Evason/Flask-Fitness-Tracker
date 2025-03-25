from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

from database import db

# Association Tables
# Establish many to many relation for muscle and exercise
exercise_muscle = db.Table(
    'exercise_muscle',
    db.Column('exercise_id', db.Integer,
              db.ForeignKey('exercise.id'), primary_key=True),
    db.Column('muscle_id', db.Integer,
              db.ForeignKey('muscle.id'), primary_key=True)
)

# Establish many to many relationship between routine and exercise
routine_exercise = db.Table(
    'routine_exercise',
    db.Column('routine_id', db.Integer,
              db.ForeignKey('routine.id'), primary_key=True),
    db.Column('exercise_id', db.Integer,
              db.ForeignKey('exercise.id'), primary_key=True)
)


# Models
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    muscles_worked = db.relationship(
        'Muscle',
        secondary=exercise_muscle,
        backref=db.backref('exercises', lazy=True),
        lazy=True
    )

    def __repr__(self):
        return '<Exercise %r>' % self.id

# Parent of Muscle
class MuscleGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    muscles = db.relationship(
        'Muscle', backref='group', lazy=True)
    
    def __repr__(self):
        return '<MuscleGroup %r>' % self.id

# Child of MuscleGroup
class Muscle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    muscle_group_id = db.Column(
        db.Integer, db.ForeignKey('muscle_group.id'), nullable=False)
    
    def __repr__(self):
        return '<Muscle %r>' % self.id
    

class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    exercises = db.relationship(
        'Exercise',
        secondary=routine_exercise,
        backref=db.backref('routines', lazy=True),
        lazy=True
    )

    def __repr__(self):
        return '<Task %r>' % self.id

    
class RoutineLog(db.Model):
    __tablename__ = 'routine_log'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    routine_id = db.Column(
        db.Integer, db.ForeignKey('routine.id'), nullable=False)
    routine = db.relationship(
        'Routine', backref=db.backref('logs', lazy=True))
    
    def __repr__(self):
        return '<Task %r>' % self.id
    

class SetLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float)
    reps = db.Column(db.Integer)
    routine_log_id = db.Column(
        db.Integer, db.ForeignKey('routine_log.id'), nullable=False)
    exercise_id = db.Column(
        db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    routine_log = db.relationship(
        'RoutineLog', backref=db.backref('sets', lazy=True))
    exercise = db.relationship(
        'Exercise', backref=db.backref('sets', lazy=True))  

    def __repr__(self):
        return '<Task %r>' % self.id
    