import socket

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Server address (replace "192.0.0.2" with your server's local IP)
server_addr = ("192.168.255.172", 12345)  # Update this with your server's IP

# Connect to the server
name = input("Enter your name: ")
client_socket.sendto(f"CONNECT {name}".encode(), server_addr)

# Receive welcome message and player ID
data, addr = client_socket.recvfrom(1024)
message = data.decode().strip()
if message.startswith("WELCOME"):
    player_id = int(message.split()[1])
    print(f"Connected as Player {player_id} ({'X' if player_id == 0 else 'O'})")
else:
    print("Error:", message)
    client_socket.close()
    exit()

# Wait for the game to start
while True:
    data, addr = client_socket.recvfrom(1024)
    message = data.decode().strip()
    if message == "START":
        print("Game started!")
        break
    else:
        print("Waiting for another player...")

def display_board(board):
    """Display the 3x3 board with proper formatting, ensuring all positions are visible."""
    print("\nBoard:")
    print(f"Debug: Board data = {board}")  # Keep for debugging
    for i in range(0, 9, 3):
        # Create the row, ensuring each position is displayed
        row = [board[j] if board[j] not in [" ", ""] else str(j + 1) for j in range(i, i + 3)]
        # Format the row manually to avoid join issues
        row_display = f"{row[0]} | {row[1]} | {row[2]}"
        print(row_display)
    print()

# Main game loop
while True:
    data, addr = client_socket.recvfrom(1024)
    message = data.decode().strip()

    if message.startswith("BOARD"):
        try:
            board_str = message.split(" ", 1)[1].split(",")  # Extract board from "BOARD X, ,O,..."
            print(f"Received board: {board_str}")
            if len(board_str) == 9:
                display_board(board_str)
            else:
                print(f"Error: Invalid board length ({len(board_str)} elements)")
        except IndexError:
            print("Error: Malformed BOARD message")

    elif message == "TURN":
        while True:
            try:
                position = int(input("Your turn, enter position (1-9): "))
                if 1 <= position <= 9:
                    client_socket.sendto(f"MOVE {position}".encode(), server_addr)
                    break
                else:
                    print("Position must be between 1 and 9")
            except ValueError:
                print("Enter a number between 1 and 9")

    elif message == "WIN":
        print("You win!")
        break

    elif message == "LOSE":
        print("You lose!")
        break

    elif message == "DRAW":
        print("It's a draw!")
        break

    elif message.startswith("ERROR"):
        print(f"Error: {message.split(' ', 1)[1]}")

    else:
        print("Unknown message:", message)

client_socket.close()