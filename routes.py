from flask import Blueprint, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import *

main = Blueprint('main', __name__)

# Route for the home page to render the index.html file
@main.route('/')
def index():
    return render_template('index.html')

# Route to render the routines.html file
@main.route('/routines', methods=['GET', 'POST'])
def create_routine():
    # If createing a routine get 'name'. Upload to .db file
    if request.method == 'POST':
        routine_name = request.form['name']
        new_routine = Routine(name=routine_name)
        db.session.add(new_routine)
        db.session.commit()
    
    routines = Routine.query.all()
    return render_template('routines.html', routines=routines)
    
@main.route('/routine/<int:routine_id>', methods=['GET', 'POST'])
def view_routine(routine_id):
    # get routine from id field
    routine = Routine.query.get(routine_id)
    exercises = Exercise.query.all()
    if not routine:
        return "Routine not found", 404
    # get routine_exercises
    routine_exercises = routine.exercises
    if request.method == 'POST':
        #submit exercises as list
        selected_exercises = request.form.getlist('exercises')
        for exercise_id in selected_exercises:
            exercise = Exercise.query.get(exercise_id)
            if exercise and exercise not in routine.exercises:
                routine.exercises.append(exercise)
        db.session.commit()

        return redirect(url_for('main.view_routine',
            routine_id=routine.id))
        
    return render_template('routine.html', routine=routine,
        exercises= exercises, routine_exercises=routine_exercises)

@main.route('/routine_log/<int:routine_id>', methods=['GET', 'POST'])
def log_routine(routine_id):
    routine = Routine.query.get(routine_id)
    exercises = routine.exercises
    
    if not routine:
        return "Routine not found", 404

    # If POST log create a RoutineLog and SetLog
    if request.method == 'POST':
        for exercise in exercises:
            now = datetime.now()
            reps_key = f"reps_{exercise.id}"
            weight_key = f"weight_{exercise.id}"
            if reps_key in request.form and weight_key in request.form:
                reps = request.form[reps_key]
                weight = request.form[weight_key]

                routine_log = RoutineLog(
                    date=now,
                    routine_id=routine_id
                )
                db.session.add(routine_log)
                db.session.commit()

                new_set_log = SetLog(
                    routine_log_id=routine_log.id,
                    exercise_id=exercise.id,
                    reps=reps,
                    weight=weight

                )
                db.session.add(new_set_log)
        
        db.session.commit()
        return redirect(url_for(
            'main.view_routine', routine_id=routine_id, exercises=exercises))

    return render_template(
        'log_routine.html',
        routine=routine, exercises=exercises)


@main.route('/muscle_groups', methods=['GET', 'POST'])
def muscle_groups():
    if request.method == 'POST':
        group_name = request.form['name']
        new_group = MuscleGroup(name=group_name)
        db.session.add(new_group)
        db.session.commit()

        return redirect(url_for('main.add_muscle_to_group',
            muscle_group_id=new_group.id))

    muscle_groups = MuscleGroup.query.all()
    return render_template('muscle_groups.html',
        groups=muscle_groups)

@main.route('/muscle_group/<int:muscle_group_id>',
    methods=['GET', 'POST'])
def add_muscle_to_group(muscle_group_id):
    muscle_group = MuscleGroup.query.get_or_404(muscle_group_id)
    if request.method == 'POST':
        muscle_name = request.form['name']
        
        new_muscle = Muscle(name=muscle_name,
            muscle_group_id=muscle_group.id)
        
        db.session.add(new_muscle)
        db.session.commit()
        return redirect(
            url_for(
                'main.add_muscle_to_group',
                muscle_group_id=muscle_group.id))
    
    # Display the current muscles in the group
    muscles_in_group = Muscle.query.filter_by(
        muscle_group_id=muscle_group.id).all()
    
    return render_template('muscle_group.html',
        muscle_group=muscle_group, muscles=muscles_in_group)


@main.route('/exercises', methods=['GET', 'POST'])
def exercises():
    if request.method == 'POST':
        exercise_name = request.form['name']
        new_exercise = Exercise(name=exercise_name)
        db.session.add(new_exercise)
        db.session.commit()
    
    exercises = Exercise.query.all()
    sets = SetLog.query.all()
    return render_template('exercises.html',
        exercises=exercises, sets=sets)

@main.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
def view_exercise(exercise_id):
    exercise = Exercise.query.get(exercise_id)
    all_muscles = Muscle.query.all()
    if not exercise:
        return "Exercise not found", 404

    exercise_muscles = exercise.muscles_worked
    if request.method == 'POST':
        selected_muscles = request.form.getlist('muscles')
        for muscle_id in selected_muscles:
            muscle = Muscle.query.get(muscle_id)
            if muscle and muscle not in exercise.muscles_worked:
                exercise.muscles_worked.append(muscle)
        
        db.session.commit()
        # Redirect the user to the exercises page
        return redirect(url_for('main.view_exercise',
            exercise_id= exercise.id))

    return render_template('exercise.html',
        exercise=exercise, muscles=all_muscles,
        exercise_muscles= exercise_muscles)
