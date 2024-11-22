import socket
import os
import threading

def send_command(command, conn):
    conn.send(command.encode())
    response = conn.recv(1024).decode()
    print("Resposta do servidor:", response)

def upload_file(filename, client):
    try:
        with open(filename, "rb") as f:
            client.send(f"upload {filename}".encode())  # Envia o comando de upload
            data = f.read(1024)
            while data:
                client.send(data)  # Envia os dados do arquivo em partes de 1024 bytes
                data = f.read(1024)
            client.send(b"")  # Finaliza o envio com um sinal de "fim"
        print("Arquivo enviado com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar o arquivo: {e}")

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5000))

    while True:
        command = input("Digite o comando: ")

        if command == "exit":
            send_command(command, client)
            break

        # Navegação e criação de diretórios no cliente
        elif command.startswith("lcd"):
            _, path = command.split(maxsplit=1)
            try:
                os.chdir(path)
                print(f"Diretório local alterado para {os.getcwd()}")
            except Exception as e:
                print(f"Erro ao alterar diretório local: {e}")

        elif command == "lpwd":
            print(f"Diretório atual do cliente: {os.getcwd()}")

        elif command.startswith("lmkdir"):
            _, folder_name = command.split(maxsplit=1)
            try:
                os.makedirs(folder_name, exist_ok=True)
                print(f"Pasta '{folder_name}' criada localmente com sucesso.")
            except Exception as e:
                print(f"Erro ao criar pasta local: {e}")

        elif command.startswith("upload"):
            _, filename = command.split(maxsplit=1)
            # Inicia o upload em uma thread separada
            th = threading.Thread(target=upload_file, args=(filename, client), daemon=True) #criando um módulo de thread
            th.start()
            print("Upload iniciado em segundo plano.")
            th.join(15) #tempo para dar join na nova thread, finaliza o thread

        elif command.startswith("download"):
            _, filename = command.split(maxsplit=1)
            client.send(f"download {filename}".encode())
            with open(f"downloaded_{filename}", "wb") as f:
                while True:
                    data = client.recv(1024)
#                   if data == b"EOF":
                    print(data)
                    break
 #                   f.write(data)
                    print("Arquivo baixado com sucesso.")

        else:
            # Comandos enviados diretamente ao servidor, incluindo `cd`, `pwd`, `ls`, etc.
            send_command(command, client)

    client.close()

if __name__ == "__main__":
    start_client()
