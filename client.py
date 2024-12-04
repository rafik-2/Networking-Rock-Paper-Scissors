import socket
import threading
import sys

# Global variable to store threads
threads = []
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
shutdown_flag = threading.Event()

# Kill all the threads
def kill_all_threads():
    global client
    global threads
    shutdown_flag.set() # to break all loop in any thread
    client.close()
    for thread in threads:
        print("thread stoped!")
        thread.join()
    sys.exit("Exited the game. See you soon!")

    
# Define available commands and game options
game_list = ["rock", "paper", "scissor"]
server_address = ('127.0.0.1', 7777)
command_list = ["/help", "/register", "/login", "/find_game", "/game_with", "/my_score", "/exit"]

# Function to handle receiving messages from the server
def receive_messages(clietn):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                print(f"\n{message}")
        except:
            print("Connection lost.")
            break

# Function to send commands to the server
def send_command(client, command):
    client.send(command.encode('utf-8'))

def start_client():
    # Connect to the server
    client.connect(server_address)

    # Start a thread to receive messages from the server
    receiver_thread = threading.Thread(target=receive_messages, args=(client,), daemon=True)
    threads.append(receiver_thread)
    receiver_thread.start()

    print("Welcome to the Game! Type commands to interact with the server.")
    while not shutdown_flag.is_set():
        try:
            command = input("\nEnter command: ")
            
            if command.startswith("/register") or command.startswith("/login"):
                send_command(client, command)

            elif command.startswith("/find_game"):
                send_command(client, command)

            elif command.startswith("/game_with"):
                send_command(client, command)

            elif command.startswith("/accept_game"):
                send_command(client, command)

            elif command.startswith("/my_score"):
                send_command(client, command)

            elif command in game_list:
                send_command(client, command)

            elif command.startswith("/help"):
                send_command(client, command)
            elif command.startswith("/list"):
                send_command(client, command)
            
            elif command.startswith("/exit"):
                send_command(client, command)
                break

            else:
                print("Unknown command!\nUse /help to see all avelable commands")
        except KeyboardInterrupt as e:
            print(f"{e}")
            break
    kill_all_threads()

if __name__ == "__main__":
    start_client()
