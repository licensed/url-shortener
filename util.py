import os
from string import ascii_letters, digits
from random import choice

URL_CHARS = int(os.environ.get('URL_CHARS', 6))


def generate_short_url():
    characters = ascii_letters + digits
    return ''.join(choice(characters) for _ in range(URL_CHARS))
