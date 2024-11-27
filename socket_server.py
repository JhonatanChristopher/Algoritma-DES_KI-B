import socket
import threading
from des1 import encryption, decryption  # Import fungsi DES

# List untuk menyimpan semua koneksi client
clients = []
key = 'abcdefgh'  # Kunci DES server yang akan dicocokkan dengan client

# Fungsi untuk broadcast pesan ke semua client
def broadcast(message, client_socket):
    for client in clients:
        try:
            if client == client_socket:
                continue 
            client.send(message)
        except:
            clients.remove(client)  # Hapus client jika gagal mengirim

# Fungsi untuk menangani setiap client
def handle_client(client_socket, client_address):
    while True:
        try:
            # Terima pesan terenkripsi dari client
            encrypted_data = client_socket.recv(1024).decode()
            if not encrypted_data:
                break

            # Dekripsi pesan dari client menggunakan key server
            try:
                data = decryption(encrypted_data, key)
                print(f"Message from {client_address}: {data}")
                
                # Enkripsi ulang pesan dengan key server sebelum broadcast
                encrypted_message, _, _ = encryption(data, key)
                broadcast(encrypted_message.encode(), client_socket)
            except:
                print(f"Received message with mismatched key from {client_address}")
                broadcast(encrypted_data.encode(), client_socket)  # Broadcast pesan tetap terenkripsi jika key tidak cocok

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
            break

    # Hapus client dari daftar jika keluar
    clients.remove(client_socket)
    client_socket.close()

def server_program():
    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen()

    print("Server listening on port", port)

    while True:
        # Terima koneksi client baru
        client_socket, address = server_socket.accept()
        print(f"Connection from: {address}")

        # Tambahkan client baru ke list
        clients.append(client_socket)

        # Buat thread baru untuk menangani client ini
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.start()

if __name__ == '__main__':
    server_program()
