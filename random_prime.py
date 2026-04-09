import random


def is_prime(n, k=5):
    """Miller-Rabin primality test."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # Find r and d such that n - 1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Perform k tests
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def get_random_prime(bits):
    """Generates a random prime number of 'bits' length."""
    while True:
        # Generate a random odd number of the specified bit length
        num = random.getrandbits(bits)
        num |= (1 << bits - 1) | 1  # Ensure it's the correct bit length and odd

        if is_prime(num):
            return num
