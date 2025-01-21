# Лабораторная работа 11, ДПИ22-1, Ершова Ю Д, 2025 г.
# Сервер


import os
import socket
from datetime import datetime

# хост
HOST = "127.0.0.1"
# порт
PORT = 8088
# рабочая директория сервера
WORKING_DIR = os.path.join(os.getcwd(), "resources")


# генерация HTTP-заголовков для ответа сервера
def generate_headers(status_code, content_type="text/html", content_length=0):
    status_messages = {200: "OK", 404: "Not Found", 400: "Bad Request"}
    status_message = status_messages.get(status_code, "Unknown Status")

    headers = [
        f"HTTP/1.1 {status_code} {status_message}",
        f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        f"Content-Type: {content_type}; charset=utf-8",
        f"Content-Length: {content_length}",
        "Server: SimpleWebServer",
        "Connection: close",
        "\r\n"
    ]
    return "\r\n".join(headers)


# обработка запроса клиента
def handle_request(client_socket):
    request = client_socket.recv(1024).decode("utf-8")
    if not request:
        return

    # разбор HTTP-запроса
    try:
        request_line = request.split("\r\n")[0]
        method, path, _ = request_line.split(" ")
        if method != "GET":
            raise ValueError("Only GET requests are supported")
    except ValueError:
        response = generate_headers(400).encode("utf-8")
        client_socket.send(response)
        return

    # устанавливаем путь к ресурсу
    path = "/index.html"
    file_path = WORKING_DIR + path

    # проверяем существование файла
    if os.path.isfile(file_path):
        with open(file_path, "rb") as file:
            content = file.read()
        headers = generate_headers(200, content_type="text/html", content_length=len(content))
        response = headers.encode("utf-8") + content
    else:
        content = b"<h1>404 Not F</h1>"
        headers = generate_headers(404, content_type="text/html", content_length=len(content))
        response = headers.encode("utf-8") + content

    # отправляем ответ клиенту
    client_socket.send(response)


# запуск веб-сервера
def start_server():
    if not os.path.exists(WORKING_DIR):
        os.makedirs(WORKING_DIR)

    # создаём сокет
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Сервер запущен на {HOST}:{PORT}...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Подключился клиент: {client_address}")
            with client_socket:
                handle_request(client_socket)


if __name__ == "__main__":
    start_server()
