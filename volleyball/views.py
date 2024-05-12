from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib import messages
from django.conf import settings
import mysql.connector

def connect_to_database():
    connection_params = settings.DATABASES['default']
    return mysql.connector.connect(
        host=connection_params['HOST'],
        user=connection_params['USER'],
        password=connection_params['PASSWORD'],
        database=connection_params['NAME'],
        port=connection_params['PORT']
    )
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        queries = {
            'Jury': f"SELECT * FROM Jury WHERE username = '{username}' AND password = '{password}'",
            'Coach': f"SELECT * FROM Coach WHERE username = '{username}' AND password = '{password}'",
            'Player': f"SELECT * FROM Player WHERE username = '{username}' AND password = '{password}'",
            'DatabaseManager': f"SELECT * FROM DatabaseManager WHERE username = '{username}' AND password = '{password}'"
        }
        
        connection = connect_to_database()

        with connection.cursor() as cursor:
            for user_type, query in queries.items():
                cursor.execute(query)
                user = cursor.fetchone()
                if user:
                    if user_type == 'Player':
                        return redirect('player_dashboard')
                    elif user_type == 'Jury':
                        return redirect('jury_dashboard')
                    elif user_type == 'Coach':
                        return redirect('coach_dashboard')
                    elif user_type == 'DatabaseManager':
                        return redirect('database_manager_dashboard')
        
        # If no user found in any database, display error message
        messages.error(request, 'Invalid username or password')
        cursor.close()
        connection.close()

    return render(request, 'login.html')

def database_manager_dashboard(request):
    # This view is accessible only to authenticated users
    return render(request, 'database_manager_dashboard.html')

def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        user_type = request.POST.get('user_type')

        # Additional fields based on user type
        nationality = request.POST.get('nationality') if user_type in ('jury', 'coach') else None
        date_of_birth = request.POST.get('date_of_birth') if user_type == 'player' else None
        height = request.POST.get('height') if user_type == 'player' else None
        weight = request.POST.get('weight') if user_type == 'player' else None

        # Validate form fields (e.g., check for empty fields)
        if not all([username, password, name, surname]):
            messages.error(request, 'All fields are required')
            return redirect('database_manager_dashboard.html')

        # Establish connection to the database
        connection = connect_to_database()

        try:
            with connection.cursor() as cursor:
                # Insert user into the database Jury Coach Player if user_type is one of them
                if user_type == 'player':
                    cursor.execute(f"INSERT INTO Player (username, password, name, surname, date_of_birth, height, weight) VALUES ('{username}', '{password}', '{name}', '{surname}', '{date_of_birth}', '{height}', '{weight}')")
                elif user_type == 'coach':
                    cursor.execute(f"INSERT INTO Coach (username, password, name, surname, nationality) VALUES ('{username}', '{password}', '{name}', '{surname}', '{nationality}')")
                elif user_type == 'jury':
                    cursor.execute(f"INSERT INTO Jury (username, password, name, surname, nationality) VALUES ('{username}', '{password}', '{name}', '{surname}', '{nationality}')")
                
            messages.success(request, 'User added successfully!')
        except Exception as e:
            # Check if the error message is related to the trigger preventing insertion
            if 'Adding new Database Managers is not allowed' in str(e):
                
                messages.error(request, 'Adding new Database Managers is not allowed')
            else:
                # If insertion failed due to other reasons, display a generic error message
                messages.error(request, f'Failed to add user: {e}')
        
        connection.commit()
        cursor.close()
        connection.close()

    return render(request, 'database_manager_dashboard.html')

def update_stadium(request):
    # Add functionality to update stadium information here
    return render(request, 'update_stadium.html')
    
def player_dashboard(request):
    # Add player-specific functionalities here
    return render(request, 'player_dashboard.html')

def coach_dashboard(request):
    # Add coach-specific functionalities here
    return render(request, 'coach_dashboard.html')

def jury_dashboard(request):
    # Add jury-specific functionalities here
    return render(request, 'jury_dashboard.html')