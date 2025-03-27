from flask import Blueprint, render_template, request, redirect, url_for
#from flask_sqlalchemy import SQLAlchemy
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
        # Check if routine_id exists
        routine_id = request.form.get('routine_id') 
        routine_name = request.form['name']
        # check if routine exists
        if routine_id:
            routine = Routine.query.get_or_404(routine_id)
            # update routine name
            routine.name = routine_name
        
        else:

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

@main.route('/routine_delete/<int:routine_id>', methods=['POST'])
def delete_routine(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    db.session.delete(routine)
    db.session.commit()
    return redirect(url_for('main.create_routine'))

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

        return redirect(url_for('main.update_or_add_muscle_to_group',
            muscle_group_id=new_group.id))

    muscle_groups = MuscleGroup.query.all()
    return render_template('muscle_groups.html',
        groups=muscle_groups)

@main.route('/delete_muscle_group/<int:muscle_group_id>',
            methods=['POST'])
def delete_muscle_group(muscle_group_id):
    selected_group = MuscleGroup.query.get_or_404(muscle_group_id)
    muscles = Muscle.query.filter_by(
        muscle_group_id=muscle_group_id).all()
    for muscle in muscles:
        db.session.delete(muscle)
    db.session.delete(selected_group)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/muscle_group/<int:muscle_group_id>',
    methods=['GET', 'POST'])
def update_or_add_muscle_to_group(muscle_group_id):
    muscle_group = MuscleGroup.query.get_or_404(muscle_group_id)
    if request.method == 'POST':
        # Check if muscle_id exists
        muscle_id = request.form.get('muscle_id')  
        muscle_name = request.form['name']

        if muscle_id:
            muscle = Muscle.query.get_or_404(muscle_id)
            muscle.name = muscle_name
        else:
            new_muscle = Muscle(name=muscle_name,
                muscle_group_id=muscle_group.id)
            db.session.add(new_muscle)
        
        
        db.session.commit()
        return redirect(
            url_for(
                'main.update_or_add_muscle_to_group',
                muscle_group_id=muscle_group.id))
    
    # Display the current muscles in the group
    muscles_in_group = Muscle.query.filter_by(
        muscle_group_id=muscle_group.id).all()
    
    return render_template('muscle_group.html',
        muscle_group=muscle_group, muscles=muscles_in_group)

@main.route('/delete_muscle/<int:muscle_group_id>/<int:muscle_id>',
            methods=['POST'])
def delete_muscle(muscle_group_id, muscle_id):
    selected_muscle = Muscle.query.get_or_404(muscle_id)
    db.session.delete(selected_muscle)
    db.session.commit()
    return redirect(url_for(
        'main.update_or_add_muscle_to_group',
        muscle_group_id=muscle_group_id
    ))


@main.route('/exercises', methods=['GET', 'POST'])
def exercises():
    if request.method == 'POST':
        exercise_id = request.form.get('exercise_id')
        exercise_name = request.form['name']
        if exercise_id:
            exercise = Exercise.query.get_or_404(exercise_id)
            exercise.name = exercise_name
        else:
            new_exercise = Exercise(name=exercise_name)
            db.session.add(new_exercise)
        db.session.commit()
    
    exercises = Exercise.query.options(db.joinedload(Exercise.muscles_worked)).all()
    sets = SetLog.query.all()
    return render_template('exercises.html',
        exercises=exercises, sets=sets)

@main.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    selected_exercise= Exercise.query.get_or_404(exercise_id)
    db.session.delete(selected_exercise)
    db.session.commit()
    return redirect(url_for('main.exercises'))

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
