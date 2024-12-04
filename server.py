import socket
import threading
import json
import hashlib
import sys
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
threads = []
game_list = ["rock", "paper", "scissor"]
clients = {}
ongoing_games = {}
game_queue = []  # This will hold players waiting for a game
player_scores = {}  # This will store player scores
player_stats = {}  # For tracking game statistics
opponent_list = []

shutdown_flag = threading.Event()

# Kill all the threads
def kill_all_threads():
    print("[SERVER] Cleaning up resources...")
    global server
    global threads
    shutdown_flag.set() # to break all loop in any thread
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print("please wait!.")
    server.close()
    for thread in threads:
        thread.join()
    sys.exit("[SERVER] Server exited.")

        

# Handles server-side commands entered via the command line.
def handle_server_commands():
    while not shutdown_flag.is_set(): 
        # shutdown_flag.is_set():
        try:
            command = input("> ")

            # Handle the /exit command
            if command.startswith("/exit"):
                shutdown_flag.set()
                print("[SERVER] Shutting down the server...")
                break
            
            # Handle the /help command
            elif command.startswith("/help"):
                help()

            # Handle the /kick command
            elif command.startswith("/kick"):
                parts = command.split(" ", 1)
                if len(parts) < 2:
                    print("[SERVER] Usage: /kick <username>")
                else:
                    username = parts[1]
                    if username in clients:
                        conn = clients[username]
                        conn.send("[SERVER] You have been kicked out.".encode('utf-8'))
                        conn.close()
                        del clients[username]
                        print(f"[SERVER] User {username} has been kicked.")
                    else:
                        print(f"[SERVER] User {username} not found.")
            
            # Handle the /del command
            elif command.startswith("/del"):
                parts = command.split(" ", 1)
                if len(parts) < 2:
                    print("[SERVER] Usage: /del <username>")
                else:
                    username = parts[1]
                    users = load_users()
                    if username in users:
                        del users[username]
                        save_users(users)
                        if username in clients:
                            conn = clients[username]
                            conn.send("[SERVER] Your account has been deleted.".encode('utf-8'))
                            conn.close()
                            del clients[username]
                        print(f"[SERVER] User {username} has been deleted.")
                    else:
                        print(f"[SERVER] User {username} not found.")
            
            # Handle the /end_game command
            elif command.startswith("/end_game"):
                parts = command.split(" ", 1)
                if len(parts) < 2:
                    print("[SERVER] Usage: /end_game <username>")
                else:
                    username = parts[1]
                    if username in ongoing_games:
                        opponent = ongoing_games[username]["opponent"]
                        clients[username].send("[SERVER] Your game session has ended.".encode('utf-8'))
                        clients[opponent].send("[SERVER] Your game session has ended.".encode('utf-8'))
                        del ongoing_games[username]
                        del ongoing_games[opponent]
                        print(f"[SERVER] Game session between {username} and {opponent} has ended.")
                    else:
                        print(f"[SERVER] No active game found for {username}.")
            
            # Handle the /list_games command
            elif command.startswith("/list_games"):
                if ongoing_games:
                    print("[SERVER] Current games:")
                    for player, game in ongoing_games.items():
                        if player not in opponent_list:
                            opponent_list.append(player)
                            print(f"{player} vs {game['opponent']}")
                else:
                    print("[SERVER] No ongoing games.")
            
            # Handle the /list_players command
            elif command.startswith("/list_online_players"):
                if clients:
                    print("[SERVER] Current connected players:")
                    for player in clients:
                        print(player)
                else:
                    print("[SERVER] No players connected.")

            # Handle unknown commands
            else:
                print("[SERVER] Unknown command.")
        
        except Exception as e:
            if shutdown_flag.is_set():
                    break
            print(f"[SERVER ERROR] {e}")
    
    # Shut down the server
    kill_all_threads()

# Function to list all avelable commands 
def help():
    print("""
Available commands:
/exit - Exit the server
/help - Show this help message
/kick <username> - Kick a user from the server
/end_game <username> - End a game session and kick all players involved
/list_games - List all current ongoing games
""")
# */del <username> - Delete a user permanently

# Load users from the JSON file
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save users to the JSON file
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

# Load scores from a JSON file
def load_scores():
    try:
        with open('scores.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save scores to a JSON file
def save_scores():
    with open('scores.json', 'w') as f:
        json.dump(player_scores, f)

# Hash a password
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Verify password
def verify_password(stored_hash, password):
    return stored_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()

# Register a new user
def register_user(username, password, conn=None):
    users = load_users()
    
    # Check if username already exists
    if username in users:
        temp_message = "Username already taken. Please try a different one.".encode('utf-8')
        if conn:
            conn.send(temp_message)
        else:
            print(temp_message)
        return False
    
    # Hash the password and store the user
    hashed_password = hash_password(password)
    users[username] = hashed_password
    player_stats[username] = {'games_played': 0, 'games_won': 0, 'games_lost': 0}
    save_users(users)
    
    # Initialize player score
    player_scores[username] = 0
    save_scores()
    if conn:
        conn.send(f"Welcome, {username}! You are now registered and logged in.".encode('utf-8'))
    return True

# Login an existing user
def login_user(username, password, conn):
    users = load_users()

    if username not in users:
        conn.send("Username not found. Please register first.".encode('utf-8'))
        return False

    stored_hash = users[username]
    if verify_password(stored_hash, password):
        conn.send(f"Welcome back, {username}!".encode('utf-8'))
        return True
    else:
        conn.send("Incorrect password. Please try again.".encode('utf-8'))
        return False

# Update the player score
def update_score(winner_username, loser_username):
    player_scores[winner_username] += 1
    player_stats[winner_username]['games_won'] += 1
    player_stats[loser_username]['games_lost'] += 1
    player_stats[winner_username]['games_played'] += 1
    player_stats[loser_username]['games_played'] += 1
    save_scores()

# Determine winner
def winner(choice1, choice2):
    if choice1 == choice2:
        return "Draw!"
    elif (choice1 == "rock" and choice2 == "scissor") or \
         (choice1 == "scissor" and choice2 == "paper") or \
         (choice1 == "paper" and choice2 == "rock"):
        return "Player 1 wins!"
    else:
        return "Player 2 wins!"

# Handle each client
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("Welcome! Please register with /register <username> <password>".encode('utf-8'))

    username = None
    try:
        while not shutdown_flag.is_set():
            try:
                msg = conn.recv(1024).decode('utf-8')
                if not msg:
                    break  # Connection closed by client
            except (socket.error, ConnectionResetError):
                print(f"[ERROR] Connection error with {addr}")
                break

            # Register user
            if msg.startswith("/register"):
                parts = msg.split(" ")
                if len(parts) < 3:
                    conn.send("Usage: /register <username> <password>".encode('utf-8'))
                    continue
                username, password = parts[1], parts[2]
                if username in clients:
                    conn.send("Username already taken. Please try a different one.".encode('utf-8'))
                else:
                    # Attempt registration
                    if register_user(username, password, conn):
                        clients[username] = conn

            # Login user
            elif msg.startswith("/login"):
                parts = msg.split(" ")
                if len(parts) < 3:
                    conn.send("Usage: /login <username> <password>".encode('utf-8'))
                    continue
                username, password = parts[1], parts[2]
                if username in clients:
                    conn.send("You are already logged in.".encode('utf-8'))
                else:
                    if login_user(username, password, conn):
                        clients[username] = conn

            # Find a game
            elif msg.startswith("/find_game"):
                if username in game_queue:
                    conn.send("You are already in the queue for a game.".encode('utf-8'))
                    continue
                
                # Add the player to the game queue
                game_queue.append(username)
                conn.send("You have been added to the game queue. Waiting for an opponent...".encode('utf-8'))

                # Try to match the player with another in the queue
                if len(game_queue) >= 2:
                    player1 = game_queue.pop(0)
                    player2 = game_queue.pop(0)

                    # Start the game between the two players
                    ongoing_games[player1] = {"opponent": player2, "choice": None}
                    ongoing_games[player2] = {"opponent": player1, "choice": None}

                    clients[player1].send(f"Game started! You are playing against {player2}. Enter your choice ('rock', 'paper', or 'scissor').".encode('utf-8'))
                    clients[player2].send(f"Game started! You are playing against {player1}. Enter your choice ('rock', 'paper', or 'scissor').".encode('utf-8'))

            # Play against a specific player
            elif msg.startswith("/game_with"):
                parts = msg.split(" ", 1)
                if len(parts) < 2:
                    conn.send("Usage: /game_with <username>".encode('utf-8'))
                    continue
                opponent = parts[1]
                if opponent not in clients:
                    conn.send(f"User {opponent} not found.".encode('utf-8'))
                elif opponent in ongoing_games:
                    conn.send(f"{opponent} is already in a game.".encode('utf-8'))
                else:
                    ongoing_games[username] = {"opponent": opponent, "choice": None}
                    ongoing_games[opponent] = {"opponent": username, "choice": None}
                    conn.send(f"Game request sent to {opponent}. Waiting for them to accept...".encode('utf-8'))
                    clients[opponent].send(f"{username} has challenged you to a game. Accept with /accept_game.".encode('utf-8'))

            # Accept a game request
            elif msg.startswith("/accept_game"):
                if username in ongoing_games and ongoing_games[username]["choice"] is None:
                    opponent = ongoing_games[username]["opponent"]
                    conn.send("Game started! Enter your choice ('rock', 'paper', or 'scissor').".encode('utf-8'))
                    clients[opponent].send("Game started! Enter your choice ('rock', 'paper', or 'scissor').".encode('utf-8'))
                else:
                    conn.send("No game request to accept.".encode('utf-8'))

            # Handle player's move
            elif msg in game_list:
                if username in ongoing_games:
                    game = ongoing_games[username]
                    game["choice"] = msg
                    opponent = game["opponent"]
                    if ongoing_games[opponent]["choice"] is not None:
                        # Both players have made their choice
                        player_choice = game["choice"]
                        opponent_choice = ongoing_games[opponent]["choice"]
                        result = winner(player_choice, opponent_choice)

                        # Update scores based on result
                        if result == "Player 1 wins!":
                            update_score(username, opponent)
                        elif result == "Player 2 wins!":
                            update_score(opponent, username)

                        conn.send(f"Your choice: {player_choice}, Opponent's choice: {opponent_choice}. Result: {result}".encode('utf-8'))
                        clients[opponent].send(f"Your choice: {opponent_choice}, Opponent's choice: {player_choice}. Result: {result}".encode('utf-8'))

                        # Clear game state
                        del ongoing_games[username]
                        del ongoing_games[opponent]
                    else:
                        conn.send("Waiting for opponent's choice...".encode('utf-8'))
                else:
                    conn.send("You are not in a game. Use /find_game to start a game.".encode('utf-8'))


            # List active players
            elif msg.startswith("/list"):
                active_players = "\n".join([user for user in clients])
                conn.send(f"Active players:\n{active_players}".encode('utf-8'))

            # Show player score and stats
            elif msg.startswith("/my_score"):
                if username in player_scores:
                    stats = player_stats[username]
                    conn.send(f"Your score: {player_scores[username]}, Games played: {stats['games_played']}, Won: {stats['games_won']}, Lost: {stats['games_lost']}".encode('utf-8'))
                else:
                    conn.send("You are not registered.".encode('utf-8'))


            # Help command
            elif msg.startswith("/help"):
                help_text = """Available commands:
                /register <username> <password> - Register a new user.
                /login <username> <password> - Login to your account.
                /find_game - Join the game queue.
                /game_with <opponent_name> - Challenge another player to a game.
                /accept_game - Accept a game challenge.
                /my_score - View your ranking and stats.
                /exit - Shut down the Server."""
                conn.send(help_text.encode('utf-8'))

            # Exit command
            elif msg.startswith("/exit"):
                conn.send("Exiting the game.".encode('utf-8'))
                break

            else:
                conn.send("Unknown command. Write /help to list all available commands".encode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up when client disconnects
        if username in clients:
            del clients[username]
            print(f"{username} disconnected.")
        conn.close()
        """if username:
            if username in ongoing_games:
                opponent = ongoing_games[username]["opponent"]
                if opponent in ongoing_games:
                    clients[opponent].send(f"{username} has disconnected. Game ended.".encode('utf-8'))
                del ongoing_games[username]
            del clients[username]
            if username in game_queue:
                game_queue.remove(username)
        conn.close()"""

# Start the server
def start_server():
    global server
    server.bind(('127.0.0.1', 7777))
    server.listen(5)
    print("[SERVER] Server started. Listening for connections...")

    server_thread = threading.Thread(target=handle_server_commands, daemon=True)
    server_thread.start()
    
    try:
        while not shutdown_flag.is_set():
            try:
                conn, addr = server.accept()
                new_thread = threading.Thread(target=handle_client, args=(conn, addr))
                threads.append(new_thread)
                new_thread.start()
            except socket.error as e:
                if shutdown_flag.is_set():
                    break
                print(f"[SERVER ERROR] {e}")
            except Exception as e:
                if shutdown_flag.is_set():
                    break
                print(f"[SERVER ERROR] {e}")
    except KeyboardInterrupt:
        print("\n[SERVER] Received Ctrl+C. Shutting down the server.")
    finally:
        # Clean up when the server is shutting down
        kill_all_threads()

if __name__ == "__main__":
    start_server()
