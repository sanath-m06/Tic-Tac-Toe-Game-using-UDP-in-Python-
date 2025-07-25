import socket

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", 12345))
print("Server started on port 12345")

# Initialize game state
board = [" " for _ in range(9)]
players = []
current_turn = 0
game_started = False

winning_combinations = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6]
]

def send_board():
    board_str = ",".join(board)
    for player_addr in players:
        server_socket.sendto(f"BOARD {board_str}".encode(), player_addr)

def check_win(marker):
    for combo in winning_combinations:
        if all(board[i] == marker for i in combo):
            return True
    return False

print("Waiting for players to connect...")

while True:
    data, addr = server_socket.recvfrom(1024)
    message = data.decode().strip()
    print(f"Received: '{message}' from {addr}")

    if message.startswith("CONNECT"):
        if len(players) < 2 and addr not in players:
            players.append(addr)
            player_id = len(players) - 1
            server_socket.sendto(f"WELCOME {player_id}".encode(), addr)
            print(f"Player {player_id} connected: {addr}")
            if len(players) == 2:
                game_started = True
                for p in players:
                    server_socket.sendto("START".encode(), p)
                send_board()
                server_socket.sendto("TURN".encode(), players[current_turn])
                print("Game started!")
        else:
            server_socket.sendto("ERROR Game full or already connected".encode(), addr)

    elif message.startswith("MOVE") and game_started:
        if addr in players:
            player_id = players.index(addr)
            if player_id == current_turn:
                try:
                    position = int(message.split()[1]) - 1
                    if not 0 <= position < 9:
                        server_socket.sendto("ERROR Position out of range. Choose 1-9.".encode(), addr)
                    elif board[position] != " ":
                        server_socket.sendto("ERROR Position already taken.".encode(), addr)
                    else:
                        marker = "X" if player_id == 0 else "O"
                        board[position] = marker
                        send_board()
                        if check_win(marker):
                            server_socket.sendto("WIN".encode(), players[player_id])
                            server_socket.sendto("LOSE".encode(), players[1 - player_id])
                            print(f"Player {player_id} wins!")
                            break
                        elif " " not in board:
                            for p in players:
                                server_socket.sendto("DRAW".encode(), p)
                            print("Game ended in a draw!")
                            break
                        else:
                            current_turn = 1 - current_turn
                            server_socket.sendto("TURN".encode(), players[current_turn])
                except (IndexError, ValueError):
                    server_socket.sendto("ERROR Invalid move format. Use: MOVE <1-9>".encode(), addr)
            else:
                # If it's not your turn, just tell the player
                server_socket.sendto("ERROR Not your turn".encode(), addr)
        else:
            server_socket.sendto("ERROR Not a player".encode(), addr)

    else:
        server_socket.sendto("ERROR Unknown command".encode(), addr)