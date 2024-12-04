import random
game_list = ["rock", "paper", "scissor"]


# Getting user input
def user_play():
    choise = input("Enter 'rock', 'paper', or 'scissor': ").lower()
    while choise not in game_list:
        print("Invalid input. Please try again.")
        choise = input("Enter 'rock', 'paper', or 'scissor: ").lower()
    return choise

# Determination of the winner
def winner(user_choise, pc_choise):
    if user_choise == pc_choise:
        return "Draw!"    
    # when the pc win
    elif ((user_choise == "rock" and pc_choise == "paper") or
        (user_choise == "scissor" and pc_choise == "rock") or
        (user_choise == "paper" and pc_choise == "scissor")):
        return "Computer wins!"
    else:
        return "You win!"
    
# Random choise from the computer
def computer_play():
    return random.choice(game_list)
    
# Playing the game
def play():
    print("Welcome to the Rock, Paper, Scissor Game!\n")
    user_choise = user_play()
    computer_choise = computer_play()
    
    print("User choosed: ", user_choise)
    print("Computer choosed: ", computer_choise)
    
    print("Winner is : ", winner(user_choise, computer_choise))
    
    
if __name__== "__main__":
    play()
