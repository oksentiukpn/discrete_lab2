import socket
import threading

from random_prime import get_random_prime


def rsa_encrypt(text, e, n):
    return [pow(ord(char), e, n) for char in text]


def rsa_decrypt(codes, d, n):
    return "".join([chr(pow(code, d, n)) for code in codes])


class Server:
    def __init__(self, port: int) -> None:
        self.host = "127.0.0.1"
        self.port = port
        self.clients = []
        self.client_keys = {}
        self.username_lookup = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        p, q = get_random_prime(256), get_random_prime(256)
        self.n = p * q
        self.e = 65537
        self.d = pow(self.e, -1, (p - 1) * (q - 1))

    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen(100)
        print(f"Server started on {self.port}")

        while True:
            c, addr = self.s.accept()
            username = c.recv(1024).decode()
            print(f"{username} tries to connect")
            self.broadcast(f"new person has joined: {username}")
            self.username_lookup[c] = username

            c.send(f"{self.e},{self.n}".encode())

            client_pub = c.recv(1024).decode()
            ce, cn = map(int, client_pub.split(","))
            self.client_keys[c] = (ce, cn)

            self.clients.append(c)
            self.broadcast(f"System: {username} joined")

            threading.Thread(target=self.handle_client, args=(c, addr)).start()

    def broadcast(self, msg: str):
        for client in self.clients:
            ce, cn = self.client_keys[client]
            encrypted_msg = rsa_encrypt(msg, ce, cn)
            client.send(str(encrypted_msg).encode())

    def handle_client(self, c: socket, addr):
        while True:
            msg = c.recv(4096).decode()
            msg = rsa_decrypt(eval(msg), self.d, self.n)

            for client in self.clients:
                if client != c:
                    ce, cn = self.client_keys[client]
                    client.send(str(rsa_encrypt(msg, ce, cn)).encode())


if __name__ == "__main__":
    s = Server(9001)
    s.start()
