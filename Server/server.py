import socket
import os
import threading

def handle_client(conn):
    try:
        while True:
            command = conn.recv(1024).decode()
            if not command:
                # Conexão fechada pelo cliente
                print("Cliente desconectado.")
                break

            if command.startswith("cd"):
                try:
                    _, path = command.split(maxsplit=1)
                    os.chdir(path)
                    conn.send(f"Diretório alterado para {os.getcwd()}".encode())
                except Exception as e:
                    conn.send(f"Erro ao alterar diretório: {e}".encode())

            elif command == "pwd":
                conn.send(f"Diretório atual do servidor: {os.getcwd()}".encode())

            elif command.startswith("mkdir"):
                try:
                    _, folder_name = command.split(maxsplit=1)
                    os.makedirs(folder_name, exist_ok=True)
                    conn.send("Pasta criada com sucesso.".encode())
                except Exception as e:
                    conn.send(f"Erro: {e}".encode())

            elif command.startswith("upload"):
                try:
                    _, filename = command.split(maxsplit=1)
                    with open(filename, "wb") as f:
                        data = conn.recv(1024)
                        while data:
                            f.write(data)
                            data = conn.recv(1024)
                    conn.send("Arquivo enviado com sucesso.".encode())
                except Exception as e:
                    conn.send(f"Erro ao salvar arquivo: {e}".encode())

            elif command.startswith("download"):
                try:
                    _, filename = command.split(maxsplit=1)
                    if os.path.isfile(filename):
                        with open(filename, "rb") as f:
                            data = f.read(1024)
                            while data:
                                conn.send(data)
                                data = f.read(1024)
                        conn.send(b"EOF")  # Sinaliza o fim do arquivo
                    else:
                        conn.send("Erro: Arquivo não encontrado.".encode())
                except Exception as e:
                    conn.send(f"Erro ao enviar arquivo: {e}".encode())

            elif command == "ls":
                try:
                    files = "; ".join(os.listdir("."))
                    conn.send(files.encode())
                except Exception as e:
                    conn.send(f"Erro: {e}".encode())

            elif command.startswith("rm"):
                try:
                    _, filename = command.split(maxsplit=1)
                    os.remove(filename)
                    conn.send("Arquivo removido com sucesso.".encode())
                except Exception as e:
                    conn.send(f"Erro: {e}".encode())

            elif command == "exit":
                conn.send("Conexão encerrada.".encode())
                break
    except ConnectionResetError:
        print("Conexão encerrada abruptamente pelo cliente.")
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))
    server.listen(5)
    print("Servidor pronto e aguardando conexão...")

    while True:
        conn, addr = server.accept()
        print(f"Conexão recebida de {addr}")
        # Lida com o cliente em uma thread separada
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    start_server()
