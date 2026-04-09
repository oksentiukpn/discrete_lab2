import socket
import threading

from random_prime import get_random_prime


def rsa_encrypt(text, e, n):
    return [pow(ord(char), e, n) for char in text]


def rsa_decrypt(codes, d, n):
    return "".join([chr(pow(code, d, n)) for code in codes])


class Client:
    def __init__(self, server_ip: str, port: int, username: str) -> None:
        self.server_ip = server_ip
        self.port = port
        self.username = username

        p, q = get_random_prime(256), get_random_prime(256)
        self.n = p * q
        self.e = 65537
        self.d = pow(self.e, -1, (p - 1) * (q - 1))

    def init_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.server_ip, self.port))
        except Exception as e:
            print("[client]: could not connect to server: ", e)
            return

        self.s.send(self.username.encode())

        server_pub = self.s.recv(1024).decode()
        self.se, self.sn = map(int, server_pub.split(","))

        self.s.send(f"{self.e},{self.n}".encode())

        print("Connected and keys exchanged!")

        message_handler = threading.Thread(target=self.read_handler, args=())
        message_handler.start()
        input_handler = threading.Thread(target=self.write_handler, args=())
        input_handler.start()

    def read_handler(self):
        while True:
            try:
                data = self.s.recv(4096).decode()
                if not data:
                    break
                codes = eval(data)
                print(f"\n{rsa_decrypt(codes, self.d, self.n)}")
            except Exception:
                break

    def write_handler(self):
        while True:
            msg = input(f"{self.username}> ")
            full_msg = f"{self.username}: {msg}"
            encrypted = rsa_encrypt(full_msg, self.se, self.sn)
            self.s.send(str(encrypted).encode())



if __name__ == "__main__":
    cl = Client("127.0.0.1", 9001, "b_g")
    cl.init_connection()
