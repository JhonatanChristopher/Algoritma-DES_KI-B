import socket
import random
import string
import threading
from des1 import encryption, decryption

# Database sederhana untuk menyimpan ID dan key
clients_db = {}
waiting_for_invitation = {}
inviting = {}

def generate_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def handle_client(connection, address):
    try:
        connection.sendall(b"Welcome to PKA. Please enter the menu you want:\n")
        pka_menu = connection.recv(1024).decode().strip()

        if pka_menu == '1':  # Key for the client itself
            connection.sendall(b"Please enter your 6-digit ID:\n")
            client_id = connection.recv(1024).decode().strip()

            # Check if the client_id exists
            if client_id in clients_db:
                public_key = clients_db[client_id]
                connection.sendall(f"Your public key is: {public_key}\n".encode())
            else:
                new_key = generate_key()
                clients_db[client_id] = new_key
                connection.sendall(f"New public key generated: {new_key}\n".encode())

        elif pka_menu == '2':  # Request key for another client
            connection.sendall(b"Please enter the your 6-digit ID:\n")
            client_id = connection.recv(1024).decode().strip()
            connection.sendall(b"Please enter the your target 6-digit ID:\n")
            target_id = connection.recv(1024).decode().strip()
            if waiting_for_invitation[target_id]:
                # check if target_id is waiting
                if target_id in clients_db:
                    inviting[client_id] = connection #saving the socket of the inviter for response
                    connection.sendall(f"Invitation sent to {address}, Please kindly wait for respond...\n".encode())
                    invitation_message = f"You have received an invitation. Do you want to join the chat? (yes/no) Invitation from: {client_id}"
                    target_socket = waiting_for_invitation[target_id]
                    target_socket.sendall(invitation_message.encode())
                    while True:
                        pass
            else:
                connection.sendall(b"This ID does not belong to any client or Client isnt in waiting room.\n")
        elif pka_menu == '3':
            connection.sendall(b"Please enter your 6-digit ID:\n")
            client_id = connection.recv(1024).decode().strip()
            waiting_for_invitation[client_id] = connection
            while True:
                id_accepted = connection.recv(1024).decode().strip()
                if id_accepted in clients_db:
                    del waiting_for_invitation[client_id]
                    public_key = clients_db[id_accepted]
                    connection.sendall(f"{public_key}".encode())
                    client_key = clients_db[client_id]
                    connection.recv(1024).decode().strip() #jeda
                    connection.sendall(f"{client_key}".encode())
                    #inviters
                    inviter_socket = inviting[id_accepted]
                    inviter_socket.sendall(f'yes'.encode())
                    inviter_socket.recv(1024).decode().strip() #jeda
                    inviter_socket.sendall(f"client public key is: {client_key}".encode())
                    print("yes")
                    del inviting[id_accepted]
                elif id_accepted:
                    del clients_db[client_id]
                    clients_db[client_id] = generate_key()
                    id_rejected = connection.recv(1024).decode().strip()
                    inviter_socket = inviting[id_rejected]
                    inviter_socket.sendall(f'no'.encode())
                    print("no")
                    del inviting[id_accepted]
                pass
    except Exception as e:
        print(f"Error with client {address}: {e}")
    finally:
        connection.close()


def start_pka():
    host=socket.gethostname()
    port=5555
    pka_socket = socket.socket()
    pka_socket.bind((host, port))
    pka_socket.listen(5)
    print(f"PKA started on {host}:{port}")

    while True:
        client_socket, client_address = pka_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    start_pka()
