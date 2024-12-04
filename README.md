# Networking Rock-Paper-Scissors Game
## Introduction:
This was an assignment in the lab of Network and protocols.
The aim is to develop a multiplayer "rock-paper-scissors" game, where there are few functionality to make and tasks to do.
This project is devided in two main part and will will highlight through this explanation all the work we did.

## Part 1: (Easy Tasks)
  Focuse on establishing the basic networking capabilities for the local game. The main goal is to develop a solid client-server application capable of basic multiplayer gameplay. As shown here the clients are able to connect to the server with no issues:
  <img width="1392" alt="Screenshot 2024-12-04 at 8 03 10 PM" src="https://github.com/user-attachments/assets/c753875b-6568-4246-ae8e-9b15752338fa">


## Server Responsibilities
* **Command Handling:**
  * `/help`: Displays available commands.
  * `/exit` or `Ctrl+C`: Terminates the connection.
  * `/kick <username>`: Kicks a specific player.
  * `/list_games`: Lists ongoing games.
  * `/list_players`: Lists connected players.
  * `/end_game <username>`: Ends a game session and kicks all involved players.
* **Connection Handling:**
  * Handles multiple client connections concurrently.
* **Game Management:**
  * Organizes gaming sessions.
  * Determines the winner.
* **Error Handling:**
  * Handles errors gracefully and provides informative messages.

## Client Responsibilities
* **Command Handling:**
  * `/help`: Displays available commands.
  * `/exit` or `Ctrl+C`: Terminates the connection.
  * `/register <username> <password>`: Creates a new user account.
  * `/login <username> <password>`: Logs in with existing credentials.
  * `/find_game`: Searches for a game.
  * `/game_with <username>`: Specifies an opponent.
  * `/my_score`: Views personal score.
* **Error Handling:**
  * Handles errors gracefully and provides informative messages.

### Note:
  The connection between the server and the client use TCP protocol.


## Part 2: (Advanced Tasks)

### **Server-Side Enhancements**
* **Multi-threaded Architecture:** Implement a multi-threaded server to handle multiple concurrent game sessions efficiently.
* **Advanced Gameplay Modes:**
  * **Player Invite System:** Allow players to invite specific opponents to private matches.
* **Security Measures:**
  * **Data Encryption:** Employ encryption techniques to protect sensitive player data (All clients passwords are saved in a .json file after encrypte them using sh256).
  * **Input Validation:** Validate all user input to prevent malicious attacks.

### **Client-Side Enhancements**
* **Secure Authentication:** Implement a secure authentication system to protect user accounts.
