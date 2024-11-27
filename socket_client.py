import socket
import threading
from des1 import encryption, decryption  # Import fungsi DES

# Variabel global untuk status koneksi
connected = True

def ped(menu, message): #singkatan PKA encrypt decrypt
    pka_key = 'abcdefg'
    if menu == '1':
        encrypted_message, _, _ = encryption(message, pka_key)
        return encrypted_message
    if menu == '2':
        decrypted_message = decryption(message, pka_key)
        return decrypted_message
        
def get_key_from_pka(pka_host, pka_port, client_id, pka_menu, target_id):
    pka_socket = socket.socket()
    pka_socket.connect((pka_host, pka_port))
    pka_socket.recv(1024)  # Terima pesan minta menu
    
    pka_socket.sendall(pka_menu.encode())
    if pka_menu == '1':
        key_message = pka_socket.recv(1024)  # Terima pesan minta id
        pka_socket.sendall(client_id.encode())
    elif pka_menu == '2':
        pka_socket.recv(1024)  # Terima pesan minta id client
        pka_socket.sendall(client_id.encode())
        pka_socket.recv(1024)  # Terima pesan minta id target
        pka_socket.sendall(target_id.encode())
        please_wait = pka_socket.recv(1024).decode()
        print(please_wait)
        while True:
            invitation_response = pka_socket.recv(1024).decode()
            if invitation_response:
                print(invitation_response)
            if invitation_response == 'no':
                print(f"This client rejected your invitation\n")
                pka_socket.close()
                return 'no'
            elif 'yes' in invitation_response:
                pka_socket.sendall('ok'.encode())
                break
            pass
    elif pka_menu == '3':
        pka_socket.recv(1024)  # Terima pesan minta id
        pka_socket.sendall(client_id.encode())
        while True:
            invitation_message = pka_socket.recv(1024).decode()
            if invitation_message:
                print(f"Received message: {invitation_message}")
                if "Do you want to join the chat?" in invitation_message:
                        response = input("Do you want to join the chatroom? (yes/no): ")
                        if response.lower() == 'yes':
                            response_message = invitation_message.split(": ")[-1].strip()
                            pka_socket.sendall(response_message.encode())
                            print("Joining the chatroom...")
                            target_key = pka_socket.recv(1024).decode()
                            print(f"targets key should be: {target_key}")
                            
                            pka_socket.sendall("ok".encode())
                            
                            your_key = pka_socket.recv(1024).decode()
                            print(f"your key should be: {your_key}")
                            pka_socket.close()
                            return target_key, your_key
                        else:
                            print("You declined the invitation.")
                            response_message = 'no'
                            pka_socket.sendall(response_message.encode())
                            response_message = invitation_message.split(": ")[-1].strip()
                            pka_socket.sendall(response_message.encode())
    key_message = pka_socket.recv(1024).decode()
    pka_socket.close()
    if "public key" in key_message:  # Ensure it's a valid key response
        print(f"Received key message: {key_message}")
        return key_message.split(": ")[-1].strip()  # Extract the key
    else:
        print("Error: Invalid response or client ID not found.")
        return None  # Return None if no valid key was found

# Fungsi untuk menerima pesan dari server
def receive_messages(client_socket, key, target_key):
    global connected
    while connected:
        try:
            # Terima pesan terenkripsi dari server
            encrypted_data = client_socket.recv(1024).decode()
            if not encrypted_data:
                break
            try:
                data_decrypt_target = decryption(encrypted_data, key)  # Coba dekripsi pesan
                data_decrypt_own = decryption(data_decrypt_target, target_key)
                print(data_decrypt_own)  # Tampilkan pesan jika berhasil didekripsi
            except:
                print("Received encrypted message (key mismatch)")  # Jika kunci berbeda
        except:
            if connected:  # Hanya tampilkan error jika masih terhubung
                print("An error occurred. Connection closed.")
            break
    client_socket.close()

def client_program():
    global connected
    host = socket.gethostname()
    port = 5000
    pka_host = socket.gethostname()
    pka_port = 5555
    
    username = input("Enter your username: ")
    client_id = input("Enter your 6-digit ID: ")
    key = get_key_from_pka(pka_host, pka_port, client_id, '1', None)
    
    # Pilih Client yang ingin dihubungi
    while True:
        print("1. Connect with someone")
        print("2. Wait for people to connect ")
        print("3. Join the group chat ")
        cli_menu = input("What do You want to do: ")
        if cli_menu == '1':
            connect_to = input("Enter the 6-Digit ID of user you want to chat with: ")
            target_key = get_key_from_pka(pka_host, pka_port, client_id, '2', connect_to)
            if 'no' in target_key:
                continue
            if target_key:  # Check if the key is valid and not None
                print(f"This Client Accepted, Successfully fetched the key for ID {connect_to}")
                break  # Exit the loop if key is fetched
            else:
                print("ID is not matching any client or invalid response. Please try again.")
        elif cli_menu == '2':
            target_key, key = get_key_from_pka(pka_host, pka_port, client_id, '3', None)
            if target_key:
                break
            else:
                print("You quit before someone wants to connect to you.")
        elif cli_menu == '3':
            target_key = 'abcdefgh' 
            break
    
    client_socket = socket.socket()
    client_socket.connect((host, port))

    # Buat thread untuk menerima pesan dari server
    thread = threading.Thread(target=receive_messages, args=(client_socket, key, target_key))
    thread.start()

    # Kirim pesan ke server
    while True:
        message = input(" -> ")
        if message.lower().strip() == 'exit':
            connected = False  # Set status koneksi menjadi False
            print("Exiting chat room...")
            client_socket.close()  # Tutup koneksi ke server
            break

        # Gabungkan nama pengguna dengan pesan
        full_message = f"[{username}]: {message}"
        encrypted_message_with_own_key, _, _ = encryption(full_message, key)
        encrypted_message_with_target_key, _, _ = encryption(encrypted_message_with_own_key, target_key)
        client_socket.send(encrypted_message_with_target_key.encode())

if __name__ == '__main__':
    client_program()
