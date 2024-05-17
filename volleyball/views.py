import datetime
import sys
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.conf import settings
import mysql.connector
from django.http import JsonResponse

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
        request.session['username'] = username
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
    database_manager_name = request.session.get('username')
    return render(request, 'database_manager_dashboard.html', {'database_manager_name': database_manager_name})

def add_user(request):
    database_manager_name = request.session.get('username')
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

    return render(request, 'database_manager_dashboard.html', {'database_manager_name': database_manager_name})

def get_stadium(request):
    database_manager_name = request.session.get('username')
    if request.method == 'POST':
        connection = connect_to_database()
        with connection.cursor() as cursor:
            cursor.execute("SELECT stadium_ID, stadium_name FROM Stadium")
            stadiums = cursor.fetchall()
        # Convert the list of tuples to a list of dictionaries
        stadiums_data = [{'stadium_ID': stadium[0], 'stadium_name': stadium[1]} for stadium in stadiums]
        # Return JSON response with stadiums list
        cursor.close()
        connection.close()
        return JsonResponse(stadiums_data, safe=False)
    return render(request, 'database_manager_dashboard.html', {'database_manager_name': database_manager_name})

def get_jury_names_surnames(request):
    coach_username = request.session.get('username')
    if request.method == 'POST':
        connection = connect_to_database()
        with connection.cursor() as cursor:
            cursor.execute("SELECT name, surname FROM Jury")
            jury = cursor.fetchall()
        # Convert the list of tuples to a list of dictionaries
        jury_data = [{'name': jury[0], 'surname': jury[1]} for jury in jury]
        # Return JSON response with jury list
        cursor.close()
        connection.close()
        return JsonResponse(jury_data, safe=False)
    return render(request, 'coach_dashboard.html', {'coach_username': coach_username})

def update_stadium(request):
    database_manager_name = request.session.get('username')
    if request.method == 'POST':
        new_name = request.POST.get('new_stadium_name')
        stadium_id = request.POST.get('stadium')
        connection = connect_to_database()
        with connection.cursor() as cursor:
            # Update stadium name in the Stadium table
            cursor.execute("UPDATE Stadium SET stadium_name = %s WHERE stadium_ID = %s", [new_name, stadium_id])
        connection.commit()
        cursor.close()
        connection.close()
        messages.success(request, 'Stadium updated successfully!')
    return render(request, 'database_manager_dashboard.html', {'database_manager_name': database_manager_name})

def player_dashboard(request):
    player_username = request.session.get('username')
    sql_query = """
        SELECT name, surname
        FROM Player
        WHERE username = %s
    """
    connect_to_database()
    with connection.cursor() as cursor:
        cursor.execute(sql_query, [player_username])
        player_data = cursor.fetchone()

        # Extract player name and surname
        player_name = player_data[0] if player_data else None
        player_surname = player_data[1] if player_data else None

        # Retrieve players played with
        cursor.execute("""
            SELECT DISTINCT p.name, p.surname
            FROM Player p
            JOIN SessionSquads ss ON p.username = ss.played_player_username
            WHERE ss.session_ID IN (
                SELECT DISTINCT session_ID
                FROM SessionSquads
                WHERE played_player_username = %s
            )
            AND ss.played_player_username != %s
        """, [player_username, player_username])
        players_played_with = cursor.fetchall()

        cursor.execute("""
            SELECT AVG(height) AS average_height
            FROM (
                SELECT p.height
                FROM Player p
                JOIN SessionSquads ss ON p.username = ss.played_player_username
                WHERE ss.played_player_username != %s
                AND ss.session_ID IN (
                    SELECT DISTINCT session_ID
                    FROM SessionSquads
                    WHERE played_player_username = %s
                )
                AND p.username != %s -- Exclude current player
                GROUP BY p.username
                HAVING COUNT(DISTINCT ss.session_ID) = (
                    SELECT MAX(session_count)
                    FROM (
                        SELECT COUNT(DISTINCT ss.session_ID) AS session_count
                        FROM Player p
                        JOIN SessionSquads ss ON p.username = ss.played_player_username
                        WHERE ss.played_player_username != %s
                        AND ss.session_ID IN (
                            SELECT DISTINCT session_ID
                            FROM SessionSquads
                            WHERE played_player_username = %s
                        )
                        AND p.username != %s -- Exclude current player
                        GROUP BY p.username
                    ) AS session_counts
                )
            ) AS players_with_most_sessions
        """, [player_username, player_username, player_username, player_username, player_username, player_username])
        average_height = cursor.fetchone()[0]
    
    cursor.close()
    connection.close()
    
    context = {
        'player_username': player_username,
        'player_name': player_name,
        'player_surname': player_surname,
        'players_played_with': players_played_with,
        'average_height': average_height,
    }

    return render(request, 'player_dashboard.html', context)

def coach_dashboard(request):
    
    coach_username = request.session.get('username')

    if request.method == 'GET':
        sql_query = """
        SELECT name, surname
        FROM Coach
        WHERE username = %s
        """
        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute(sql_query, [coach_username])
        coach_data = cursor.fetchone()

        coach_name = coach_data[0] if coach_data else None
        coach_surname = coach_data[1] if coach_data else None

        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        team_query = \
                    f"""
                    SELECT team_name, team_ID
                    FROM Team 
                    WHERE coach_username = '{coach_username}' AND contract_start <= '{current_date}' AND contract_finish >= '{current_date}'
                    """
        cursor.execute(team_query)
        team = cursor.fetchone()
        team_name = team[0] if team else None
        team_id = team[1] if team else None

        stadium_query = "SELECT stadium_name, country FROM Stadium"
        cursor.execute(stadium_query)
        stadiums = cursor.fetchall()

        #write query to get all players in the team
        query = """
            SELECT p.username, p.name, p.surname
            FROM Player p
            JOIN PlayerTeams pt ON p.username = pt.username
            WHERE pt.team = %s
        """
        cursor.execute(query, [team_id])
        players = cursor.fetchall()

        #get max session id
        cursor.execute("SELECT MAX(session_ID) FROM MatchSession")
        max_session_id = cursor.fetchone()[0]
        session_id = max_session_id + 1 if max_session_id else 1

        try:
            query = """
                SELECT ms.session_ID, t.team_name, ms.stadium_name, ms.time_slot, ms.date, j.name , j.surname, ms.rating, t.team_ID
                FROM MatchSession ms
                JOIN Team t ON ms.team_ID = t.team_ID
                JOIN Jury j ON ms.assigned_jury_username = j.username
                ORDER BY ms.session_ID
            """
            cursor.execute(query)
            matches = cursor.fetchall()
        except Exception as e:
            messages.error(request, f'Failed to fetch matches: {e}')
            matches = []

        coach_matches_query = """
                SELECT ms.session_ID
                FROM MatchSession ms
                JOIN Team t ON ms.team_ID = t.team_ID
                WHERE t.coach_username = %s 
                AND t.contract_start <= %s 
                AND t.contract_finish >= %s
                AND NOT EXISTS (
                    SELECT 1
                    FROM SessionSquads ss
                    WHERE ss.session_ID = ms.session_ID
                )
                ORDER BY ms.session_ID
            """
        cursor.execute(coach_matches_query, [coach_username, current_date, current_date])
        coach_matches = cursor.fetchall()
        cursor.close()
        conn.close()

        context = {
            'coach_name': coach_name,
            'coach_surname': coach_surname,
            'sessions': matches,
            'team_name': team_name,
            'team_id': team_id,
            'session_id': session_id,
            'stadiums': stadiums if stadiums else [],
            'matches': coach_matches if coach_matches else [],
            'players': players if players else []
        }
        return render(request, 'coach_dashboard.html', context)
    
    if request.method == 'POST':
        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            query = f"DELETE FROM MatchSession WHERE session_ID = {request.POST.get('session_id')}"
            cursor.execute(query)
            conn.commit()
        except Exception as e:
            messages.error(request, f'Failed to delete match: {e}')
            return HttpResponse('Failed to delete match')

        cursor.close()
        conn.close()

        return redirect('coach_dashboard')

def create_squad(request):
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        
        # Extract player names and positions
        players_and_positions = []
        selected_players = set()  #chechk if the player is selected twice or more
        for i in range(1, 7):  
            player_username = request.POST.get(f'player{i}')
            position_id = request.POST.get(f'position{i}')
            if player_username in selected_players:
                return redirect('coach_dashboard')
            selected_players.add(player_username)
            players_and_positions.append((player_username, position_id))
        
        connection = connect_to_database()
        cursor = connection.cursor()

        #check if the player can play in the selected position
        for player_username, position_id in players_and_positions:
            cursor.execute(
                "SELECT COUNT(*) FROM PlayerPositions WHERE username = %s AND position = %s",
                [player_username, position_id]
            )
            count = cursor.fetchone()[0]
            if count == 0:
                return redirect('coach_dashboard')
        #find max squad id
        cursor.execute("SELECT MAX(squad_ID) FROM SessionSquads")
        max_squad_id = cursor.fetchone()[0]
        squad_id = max_squad_id + 1 if max_squad_id else 1
        # Insert players and positions into the database
        for player_username, position_id in players_and_positions:
            cursor.execute(
                "INSERT INTO SessionSquads (squad_ID, session_ID, played_player_username, position_ID) VALUES (%s, %s, %s, %s)",
                [squad_id, session_id, player_username, position_id]
            )
            squad_id += 1
        
        connection.commit()
        cursor.close()
        connection.close()

        return redirect('coach_dashboard')
    return redirect('coach_dashboard')

def jury_dashboard(request):
    
    if request.method == 'GET':
        
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')

        jury_username = request.session.get('username')
        sql_query = """
        SELECT name, surname
        FROM Jury
        WHERE username = %s
        """

        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute(sql_query, [jury_username])
        jury_data = cursor.fetchone()

        jury_name = jury_data[0] if jury_data else None
        jury_surname = jury_data[1] if jury_data else None

        try:
            query = """
                SELECT ms.session_ID, t.team_name, ms.stadium_name, ms.time_slot, ms.date, ms.rating
                FROM MatchSession ms
                JOIN Team t ON ms.team_ID = t.team_ID
                WHERE ms.date < %s AND ms.assigned_jury_username = %s AND ms.rating IS NULL
            """
            cursor.execute(query, [current_date, jury_username])
            matches = cursor.fetchall()
        except Exception as e:
            messages.error(request, f'Failed to fetch matches: {e}')
            matches = []

        try:
            query = """
                SELECT COUNT(*)
                FROM MatchSession
                WHERE assigned_jury_username = %s AND rating IS NOT NULL
            """
            cursor.execute(query, [jury_username])
            rated_matches = cursor.fetchone()[0]

        except Exception as e:
            messages.error(request, f'Failed to fetch rated matches: {e}')
            rated_matches = 0

        try:
            query = """
                SELECT AVG(rating)
                FROM MatchSession
                WHERE assigned_jury_username = %s AND rating IS NOT NULL
            """
            cursor.execute(query, [jury_username])
            avg_rating = cursor.fetchone()[0]
        except Exception as e:
            messages.error(request, f'Failed to fetch average rating: {e}')
            avg_rating = "N/A"

        cursor.close()
        conn.close()

        context = {
            'jury_username': jury_username,
            'jury_name': jury_name,
            'jury_surname': jury_surname,
            'sessions': matches,
            'rated_sessions_count': rated_matches,
            'average_rating': avg_rating
        }

        if not matches:
            messages.info(request, 'No matches to rate')
            return render(request, 'jury_dashboard.html', context)

        return render(request, 'jury_dashboard.html', context)

    if request.method == 'POST':       
        conn = connect_to_database()
        cursor = conn.cursor()

        for key, value in request.POST.items():
            if key.startswith('rating_'):
                try:
                    session_id = int(key.split('_')[1])
                    if(value == ''):
                        continue
                    rating = float(value)
                    query = f"UPDATE MatchSession SET rating = {rating} WHERE session_ID = {session_id}"
                    cursor.execute(query)
                    conn.commit()
                except Exception as e:
                    messages.error(request, f'Failed to submit rating: {e}')
                    return redirect('jury_dashboard')

        cursor.close()
        conn.close()

        return redirect('jury_dashboard')

def create_match_session(request):
    
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        team_id = request.POST.get('team_id')
        stadium_name = request.POST.get('stadium_name')
        time_slot = request.POST.get('time_slot')
        date = request.POST.get('date')
        assigned_jury_name_surname = request.POST.get('assigned_jury_name_surname')

        #get username of the coach
        coach_username = request.session.get('username')
        
        # Extract the username from the name and surname
        assigned_jury_name = assigned_jury_name_surname.split(' ')[0]
        assigned_jury_surname = assigned_jury_name_surname.split(' ')[1]

        connection = connect_to_database()
        #check if the coach is still the coach of the team in the current date
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM Team WHERE team_ID = '{team_id}' AND coach_username = '{coach_username}' AND contract_start <= '{date}' AND contract_finish >= '{date}'")
            team = cursor.fetchone()
            if not team:
                messages.error(request, 'You are not the coach of this team in the selected date')
                return redirect('coach_dashboard')
            
        #sql query to find jury username
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT username FROM Jury WHERE name = '{assigned_jury_name}' AND surname = '{assigned_jury_surname}'")
            assigned_jury_username = cursor.fetchone()[0]
        
        #sql query to find stadium id and country
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT stadium_ID, country FROM Stadium WHERE stadium_name = '{stadium_name}'")
            stadium_data = cursor.fetchone()
            stadium_id = stadium_data[0]
            stadium_country = stadium_data[1]
        
        try:
            with connection.cursor() as cursor:
                
                insert_query = \
                    f"""
                    INSERT INTO MatchSession (session_ID, team_ID, stadium_ID, stadium_name, stadium_country, time_slot, date, assigned_jury_username) 
                    VALUES ('{session_id}', '{team_id}', '{stadium_id}', '{stadium_name}', '{stadium_country}', '{time_slot}', '{date}', '{assigned_jury_username}')
                    """
                cursor.execute(insert_query)
        except Exception as e:
            cursor.close()
            messages.error(request, f'Failed to create match session: {e}')
            return redirect('coach_dashboard')
        
        connection.commit()
        cursor.close()


    return redirect('coach_dashboard')