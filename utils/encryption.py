import os
import json
from dotenv import load_dotenv
from cryptography.fernet import Fernet


def get_cipher():
    load_dotenv()
    key = os.getenv("SECRET_KEY", "")
    cipher = Fernet(key)
    return cipher


def encrypt_data(data):
    cipher = get_cipher()
    encrypted_data = cipher.encrypt(data.encode()).decode()
    return encrypted_data


def decrypt_data(encrypted_data):
    cipher = get_cipher()
    decrypted_data = cipher.decrypt(encrypted_data.encode()).decode()
    return decrypted_data


def encrypt_dictionary(dictionary):
    cipher = get_cipher()
    encrypted_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, int) or isinstance(value, str):
            encrypted_dict[key] = cipher.encrypt(json.dumps(value).encode()).decode()

    return encrypted_dict
