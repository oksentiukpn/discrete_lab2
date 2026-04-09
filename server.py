import socket
import threading

from random_prime import get_random_prime


def rsa_encrypt(text, e, n):
    return [pow(ord(char), e, n) for char in text]


def rsa_decrypt(codes, d, n):
    return "".join([chr(pow(code, d, n)) for code in codes])


def simple_hash(text):
    h = 5381
    for char in text:
        h = ((h << 5) + h) + ord(char)
    return h & 0xFFFFFFFFFFFFFFFF


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
            self.username_lookup[c] = username

            c.send(f"{self.e},{self.n}".encode())

            client_pub = c.recv(1024).decode()
            ce, cn = map(int, client_pub.split(","))
            self.client_keys[c] = (ce, cn)

            self.clients.append(c)

            threading.Thread(target=self.handle_client, args=(c, addr)).start()

    def broadcast(self, msg: str):
        msg_hash = simple_hash(msg)
        for client in self.clients:
            ce, cn = self.client_keys[client]
            encrypted_msg = rsa_encrypt(msg, ce, cn)
            client.send(str((msg_hash, encrypted_msg)).encode())

    def handle_client(self, c: socket, addr):
        while True:
            try:
                data = c.recv(4096).decode()
                if not data:
                    break

                received_hash, encrypted_msg = eval(data)
                msg = rsa_decrypt(encrypted_msg, self.d, self.n)

                if simple_hash(msg) == received_hash:
                    self.broadcast(msg)
                else:
                    print(
                        f"Integrity check failed for message from {self.username_lookup.get(c, 'Unknown')}"
                    )
            except Exception as e:
                print(f"Error handling client {addr}: {e}")
                break


if __name__ == "__main__":
    s = Server(9001)
    s.start()
