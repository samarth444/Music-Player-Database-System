import mysql.connector
from getpass import getpass
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from decimal import Decimal

app = Flask(__name__)
app.secret_key = '83ae51fe2b64073d53c01a3d8488f7e5'  # Required for flash messages

# Database connection
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="samu2003",
    database="music"
)
cursor = connection.cursor(dictionary=True)

def hash_password(password):
    return generate_password_hash(password)

#admin operations

# Helper function to require login
# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_authenticated' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route to create a new user
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        phone_number = request.form['phone_number']
        date_of_birth = request.form['date_of_birth']
        country = request.form['country']
        email_id = request.form['email_id']
        password = hash_password(request.form['password'])

        try:
            cursor.execute("""
                INSERT INTO User (user_id, username, phone_number, date_of_birth, country, email_id, password, is_admin)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 0)
            """, (user_id, username, phone_number, date_of_birth, country, email_id, password))
            connection.commit()
            flash('User account created successfully!', 'success')
            return redirect(url_for('index'))
        except mysql.connector.IntegrityError as e:
            flash(f'Error: {e}', 'danger')
    
    return render_template('create_user.html')

@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        adminname = request.form['adminname']
        phone_number = request.form['phone_number']
        date_of_birth = request.form['date_of_birth']
        country = request.form['country']
        email_id = request.form['email_id']
        password = hash_password(request.form['password'])

        try:
            cursor.execute("""
                INSERT INTO User (user_id, username, phone_number, date_of_birth, country, email_id, password, is_admin)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """, (admin_id, adminname, phone_number, date_of_birth, country, email_id, password))
            connection.commit()
            
            return redirect(url_for('index'))
            
        except mysql.connector.IntegrityError as e:
            flash(f'Error: {e}', 'danger')
    
    
    flash('Admin account created successfully!', 'success')
    return render_template('create_admin.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM User WHERE username = %s AND is_admin = TRUE", (username,))
        admin = cursor.fetchone()

        if admin and check_password_hash(admin['password'], password):
            session['admin_authenticated'] = True
            flash('Logged in successfully.', 'success')

            # Update login_status to 'success' for this admin
            cursor.execute("""
                UPDATE User 
                SET login_status = 'success' 
                WHERE username = %s
            """, (username,))
            connection.commit()

            return redirect(url_for('admin_operations'))
        else:
            flash('Incorrect username or password.', 'danger')

            # Update login_status to 'failure' for this admin
            cursor.execute("""
                UPDATE User 
                SET login_status = 'failure' 
                WHERE username = %s
            """, (username,))
            connection.commit()
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('admin_authenticated', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))



@app.route('/admin_operations')
@login_required
def admin_operations():
   
    return render_template('admin_operations.html')



# Route to render the insertion page
@app.route('/insertion')
@login_required
def insertion():
    return render_template('insertion.html')

# Route to handle insertion into Artist table
@app.route('/insert_artist', methods=['POST'])
def insert_artist():
    artist_id = request.form['artist_id']
    name = request.form['name']
    style = request.form['style']
    cursor.execute("INSERT INTO Artist (artist_id, name, style) VALUES (%s, %s, %s);", 
                   (artist_id, name, style))
    connection.commit()
    flash("Artist inserted successfully!")
    return redirect(url_for('insertion'))

# Route to handle insertion into Album table
@app.route('/insert_album', methods=['POST'])
def insert_album():
    album_id = request.form['album_id']
    name = request.form['name']
    genre = request.form['genre']
    year = request.form['year']
    artist_id = request.form['artist_id']
    cursor.execute("INSERT INTO Album (album_id, name, genre, year, artist_id) VALUES (%s, %s, %s, %s, %s);",
                   (album_id, name, genre, year, artist_id))
    connection.commit()
    flash("Album inserted successfully!")
    return redirect(url_for('insertion'))

@app.route('/insert_song', methods=['POST'])
def insert_song():
    song_id = request.form['song_id']
    name = request.form['name']
    ratings = request.form['ratings']
    year_of_release = request.form['year_of_release']
    album_id = request.form['album_id']
    tags = request.form['tags']
    audio_url = request.form['audio_url']  # New field for audio URL or YouTube link
    
    cursor.execute(
        "INSERT INTO Song (song_id, name, ratings, year_of_release, album_id, tags, audio_url) VALUES (%s, %s, %s, %s, %s, %s, %s);",
        (song_id, name, ratings, year_of_release, album_id, tags, audio_url)
    )
    connection.commit()
    flash("Song inserted successfully!")
    return redirect(url_for('insertion'))

# Route to handle insertion into Playlist table
@app.route('/insert_playlist', methods=['POST'])
def insert_playlist():
    playlist_id = request.form['playlist_id']
    name = request.form['name']
    tags = request.form['tags']
    user_id = request.form['user_id']
    artist_id = request.form['artist_id'] or None
    cursor.execute("INSERT INTO Playlist (playlist_id, name, tags, user_id, artist_id) VALUES (%s, %s, %s, %s, %s);",
                   (playlist_id, name, tags, user_id, artist_id))
    connection.commit()
    flash("Playlist inserted successfully!")
    return redirect(url_for('insertion'))

# Route to handle insertion into Playlist_Song table
@app.route('/insert_playlist_song', methods=['POST'])
def insert_playlist_song():
    playlist_id = request.form['playlist_id']
    song_id = request.form['song_id']
    cursor.execute("INSERT INTO Playlist_Song (playlist_id, song_id) VALUES (%s, %s);", (playlist_id, song_id))
    connection.commit()
    flash("Playlist song entry added successfully!")
    return redirect(url_for('insertion'))

@app.route('/deletion')
@login_required
def deletion():
    return render_template('deletion.html')

# Route to handle deletion from User table
@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form['user_id']
    cursor.execute("DELETE FROM User WHERE user_id = %s;", (user_id,))
    connection.commit()
    flash("User deleted successfully!")
    return redirect(url_for('deletion'))

# Route to handle deletion from Artist table
@app.route('/delete_artist', methods=['POST'])
def delete_artist():
    artist_id = request.form['artist_id']
    cursor.execute("DELETE FROM Artist WHERE artist_id = %s;", (artist_id,))
    connection.commit()
    flash("Artist deleted successfully!")
    return redirect(url_for('deletion'))

# Route to handle deletion from Album table
@app.route('/delete_album', methods=['POST'])
def delete_album():
    album_id = request.form['album_id']
    cursor.execute("DELETE FROM Album WHERE album_id = %s;", (album_id,))
    connection.commit()
    flash("Album deleted successfully!")
    return redirect(url_for('deletion'))

# Route to handle deletion from Song table
@app.route('/delete_song', methods=['POST'])
def delete_song():
    song_id = request.form['song_id']
    cursor.execute("DELETE FROM Song WHERE song_id = %s;", (song_id,))
    connection.commit()
    flash("Song deleted successfully!")
    return redirect(url_for('deletion'))

# Route to handle deletion from Playlist table
@app.route('/delete_playlist', methods=['POST'])
def delete_playlist():
    playlist_id = request.form['playlist_id']
    cursor.execute("DELETE FROM Playlist WHERE playlist_id = %s;", (playlist_id,))
    connection.commit()
    flash("Playlist deleted successfully!")
    return redirect(url_for('deletion'))

# Route to handle deletion from Playlist_Song table
@app.route('/delete_playlist_song', methods=['POST'])
def delete_playlist_song():
    playlist_id = request.form['playlist_id']
    song_id = request.form['song_id']
    cursor.execute("DELETE FROM Playlist_Song WHERE playlist_id = %s AND song_id = %s;", (playlist_id, song_id))
    connection.commit()
    flash("Playlist_Song relationship deleted successfully!")
    return redirect(url_for('deletion'))



@app.route('/updation')
@login_required
def updation():
    return render_template('updation.html')



# Route to handle updating user information
@app.route('/update_user', methods=['POST'])
def update_user():
    user_id = request.form['user_id']
    column = request.form['column']
    new_value = request.form['new_value']
    cursor.execute(f"UPDATE User SET {column} = %s WHERE user_id = %s;", (new_value, user_id))
    connection.commit()
    flash("User updated successfully!")
    return redirect(url_for('updation'))

# Similar routes for other tables...

# Route to handle updating artist information
@app.route('/update_artist', methods=['POST'])
def update_artist():
    artist_id = request.form['artist_id']
    column = request.form['column']
    new_value = request.form['new_value']
    cursor.execute(f"UPDATE Artist SET {column} = %s WHERE artist_id = %s;", (new_value, artist_id))
    connection.commit()
    flash("Artist updated successfully!")
    return redirect(url_for('updation'))

# Route to handle updating album information
@app.route('/update_album', methods=['POST'])
def update_album():
    album_id = request.form['album_id']
    column = request.form['column']
    new_value = request.form['new_value']
    cursor.execute(f"UPDATE Album SET {column} = %s WHERE album_id = %s;", (new_value, album_id))
    connection.commit()
    flash("Album updated successfully!")
    return redirect(url_for('updation'))

# Route to handle updating song information
# Route to handle updating song information
@app.route('/update_song', methods=['POST'])
def update_song():
    song_id = request.form['song_id']
    column = request.form['column']
    new_value = request.form['new_value']
    
    # Map form input to actual column names to prevent SQL injection
    valid_columns = {
        "name": "name",
        "ratings": "ratings",
        "year_of_release": "year_of_release",
        "album_id": "album_id",
        "tags": "tags",
        "audio_url": "audio_url"
    }
    
    # Only proceed if the selected column is valid
    if column in valid_columns:
        cursor.execute(f"UPDATE Song SET {valid_columns[column]} = %s WHERE song_id = %s;", (new_value, song_id))
        connection.commit()
        flash("Song updated successfully!")
    else:
        flash("Invalid column selected for update.")
    
    return redirect(url_for('updation'))


# Route to handle updating playlist information
@app.route('/update_playlist', methods=['POST'])
def update_playlist():
    playlist_id = request.form['playlist_id']
    column = request.form['column']
    new_value = request.form['new_value']
    cursor.execute(f"UPDATE Playlist SET {column} = %s WHERE playlist_id = %s;", (new_value, playlist_id))
    connection.commit()
    flash("Playlist updated successfully!")
    return redirect(url_for('updation'))

# Route to handle updating playlist-song relationships
@app.route('/update_playlist_song', methods=['POST'])
def update_playlist_song():
    playlist_id = request.form['playlist_id']
    song_id = request.form['song_id']
    new_playlist_id = request.form['new_playlist_id']
    cursor.execute("UPDATE Playlist_Song SET playlist_id = %s WHERE playlist_id = %s AND song_id = %s;", 
                   (new_playlist_id, playlist_id, song_id))
    connection.commit()
    flash("Playlist_Song relationship updated successfully!")
    return redirect(url_for('updation'))


#user operation

# Decorator to ensure login required
def login2_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_authenticated' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login2'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM User WHERE username = %s AND is_admin = FALSE", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_authenticated'] = True
            flash('Logged in successfully.', 'success')

            # Update login_status to 'success' for this user
            cursor.execute("""
                UPDATE User 
                SET login_status = 'success' 
                WHERE username = %s
            """, (username,))
            connection.commit()

            return redirect(url_for('user_operations'))
        else:
            flash('Incorrect username or password.', 'danger')

            # Update login_status to 'failure' for this user
            cursor.execute("""
                UPDATE User 
                SET login_status = 'failure' 
                WHERE username = %s
            """, (username,))
            connection.commit()
    
    return render_template('login2.html')

# Route to log out the user
@app.route('/logout2')
def logout2():
    session.pop('user_authenticated', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login2'))

# Main user operations page
@app.route('/user_operations')
@login2_required
def user_operations():
    return render_template('user_operations.html')

# AJAX route to search artist by name
@app.route('/search_artist', methods=['POST'])
@login2_required
def search_artist():
    artist_name = request.form['artist_name']
    cursor.execute("""
        SELECT a.album_id, a.name AS album_name, a.genre, a.year, 
               s.song_id, s.name AS song_name, s.ratings, s.audio_url
        FROM Artist ar
        LEFT JOIN Album a ON ar.artist_id = a.artist_id
        LEFT JOIN Song s ON a.album_id = s.album_id
        WHERE ar.name = %s;
    """, (artist_name,))
    results = cursor.fetchall()
    return jsonify(results)


# AJAX route to search song by name
@app.route('/search_song', methods=['POST'])
@login2_required
def search_song():
    song_name = request.form['song_name']
    cursor.execute("""
        SELECT s.song_id, s.name AS song_name, s.ratings, s.audio_url,
               a.album_id, a.name AS album_name,
               ar.artist_id, ar.name AS artist_name
        FROM Song s
        LEFT JOIN Album a ON s.album_id = a.album_id
        LEFT JOIN Artist ar ON a.artist_id = ar.artist_id
        WHERE s.name = %s;
    """, (song_name,))
    results = cursor.fetchall()
    return jsonify(results)

# Sort artists in ascending order
@app.route('/sort_artists_ascending', methods=['GET'])
@login2_required
def sort_artists_ascending():
    cursor.execute("SELECT name FROM Artist ORDER BY name ASC;")
    results = cursor.fetchall()
    return jsonify(results)

# Sort artists in descending order
@app.route('/sort_artists_descending', methods=['GET'])
@login2_required
def sort_artists_descending():
    cursor.execute("SELECT name FROM Artist ORDER BY name DESC;")
    results = cursor.fetchall()
    return jsonify(results)

# Get average rating of all songs by an artist, including URLs of each song
@app.route('/artist_avg_rating', methods=['POST'])
@login2_required
def artist_avg_rating():
    artist_name = request.form['artist_name']
    cursor.execute("""
        SELECT AVG(s.ratings) AS avg_rating
        FROM Song s
        JOIN Album a ON s.album_id = a.album_id
        JOIN Artist ar ON a.artist_id = ar.artist_id
        WHERE ar.name = %s;
    """, (artist_name,))
    avg_rating_result = cursor.fetchone()
    avg_rating = avg_rating_result['avg_rating'] if avg_rating_result['avg_rating'] is not None else "No songs found for artist."

    # Fetch all song URLs for the given artist
    cursor.execute("""
        SELECT s.name AS song_name, s.audio_url
        FROM Song s
        JOIN Album a ON s.album_id = a.album_id
        JOIN Artist ar ON a.artist_id = ar.artist_id
        WHERE ar.name = %s;
    """, (artist_name,))
    songs = cursor.fetchall()
    
    # Prepare response with average rating and song URLs
    return jsonify({
        "average_rating": avg_rating,
        "songs": [{"name": song['song_name'], "audio_url": song['audio_url']} for song in songs]
    })

def get_most_popular_song():
    try:
        cursor.callproc('GetMostPopularSong')  # Call the stored procedure
        
        # Fetch the actual data from stored procedure results
        for result in cursor.stored_results():
            row = result.fetchone()
            if row:
                # Log row data to inspect its structure
                print("Fetched row:", row)
                
                return {
                    "song_id": row["song_id"],
                    "song_name": row["song_name"],
                    "avg_rating": row["avg_rating"],
                    "audio_url": row["audio_url"]
                }
            else:
                print("Unexpected data format in avg_rating:")
                return None
    except Exception as e:
        # Print full error details for debugging
        print("Error retrieving data:", e)
    return None  # Return None if no result is found or an error occurs

@app.route('/most_popular_song', methods=['GET'])
def get_most_popular_song_route():
    most_popular_song = get_most_popular_song()  # Get data from the stored procedure
    print("Server response:", most_popular_song)
    if most_popular_song:
        return jsonify(most_popular_song)  # Return JSON response
    else:
        print("No popular song found or error occurred in stored procedure call.")
        return jsonify({'message': 'No popular song found'}), 404

@app.route('/all_songs', methods=['GET'])
def all_songs():
    cursor.execute("SELECT song_id, name AS song_name, audio_url FROM Song")
    songs = cursor.fetchall()
    return jsonify(songs)

# Route to fetch all songs grouped by album
@app.route('/album_songs', methods=['GET'])
def album_songs():
    cursor.execute("""
        SELECT Album.album_id, Album.name AS album_name, Song.song_id, Song.name AS song_name, Song.audio_url
        FROM Album
        LEFT JOIN Song ON Album.album_id = Song.album_id
        ORDER BY Album.album_id
    """)
    albums = {}
    for row in cursor.fetchall():
        album_id = row['album_id']
        if album_id not in albums:
            albums[album_id] = {
                'album_name': row['album_name'],
                'songs': []
            }
        albums[album_id]['songs'].append({
            'song_id': row['song_id'],
            'song_name': row['song_name'],
            'audio_url': row['audio_url']
        })
    
    return jsonify(list(albums.values()))

# Route to fetch all songs grouped by playlist
@app.route('/playlist_songs', methods=['GET'])
def playlist_songs():
    cursor.execute("""
        SELECT Playlist.playlist_id, Playlist.name AS playlist_name, Song.song_id, Song.name AS song_name, Song.audio_url
        FROM Playlist
        LEFT JOIN Playlist_Song ON Playlist.playlist_id = Playlist_Song.playlist_id
        LEFT JOIN Song ON Playlist_Song.song_id = Song.song_id
        ORDER BY Playlist.playlist_id
    """)
    playlists = {}
    for row in cursor.fetchall():
        playlist_id = row['playlist_id']
        if playlist_id not in playlists:
            playlists[playlist_id] = {
                'playlist_name': row['playlist_name'],
                'songs': []
            }
        playlists[playlist_id]['songs'].append({
            'song_id': row['song_id'],
            'song_name': row['song_name'],
            'audio_url': row['audio_url']
        })
    
    return jsonify(list(playlists.values()))





if __name__ == '__main__':
    app.run(debug=True)
