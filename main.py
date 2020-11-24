import sys
import json
from base64 import b64encode, b64decode
import random
from Crypto.Cipher import *
from Crypto.Cipher import ARC4 as arc1
from Crypto.Hash import SHA as sh
from Crypto.Cipher import ARC2 as arc2
from Crypto.Cipher import Blowfish as Bl
from Crypto.Cipher import CAST as C
from Crypto.Random import get_random_bytes as gr
from Crypto.Cipher import AES as trans_cipher
from Crypto.Cipher import ChaCha20_Poly1305 as ChP
from Crypto.Util.py3compat import *
from Crypto.Random import *
from socket import *


def pad(data_to_pad, block_size):
    """Apply standard padding.
    :Parameters:
      data_to_pad : byte string
        The data that needs to be padded.
      block_size : integer
        The block boundary to use for padding. The output length is guaranteed
        to be a multiple of ``block_size``.
      style : string
        Padding algorithm. It can be *'pkcs7'* (default), *'iso7816'* or *'x923'*.
    :Return:
      The original data with the appropriate padding added at the end.
    """
    padding_len = block_size - len(data_to_pad) % block_size
    padding = bchr(padding_len) * padding_len
    return data_to_pad + padding


def unpad(padded_data, block_size):
    """Remove standard padding.
    :Parameters:
      padded_data : byte string
        A piece of data with padding that needs to be stripped.
      block_size : integer
        The block boundary to use for padding. The input length
        must be a multiple of ``block_size``.
      style : string
        Padding algorithm. It can be *'pkcs7'* (default), *'iso7816'* or *'x923'*.
    :Return:
        Data without padding.
    :Raises ValueError:
        if the padding is incorrect.
    """

    pdata_len = len(padded_data)
    if pdata_len % block_size:
        raise ValueError("Input data is not padded")
    padding_len = bord(padded_data[-1])
    if padding_len < 1 or padding_len > min(block_size, pdata_len):
        raise ValueError("Padding is incorrect.")
    if padded_data[-padding_len:] != bchr(padding_len) * padding_len:
        raise ValueError("PKCS#7 padding is incorrect.")
    return padded_data[:-padding_len]

def server_start(port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(1)
    return sock

def server_listen(sock):
    conn, addr = sock.accept()
    data = conn.recv(4096)
    data = json.loads(data)
    conn.close()
    return data

def server_close(sock):
    sock.close()

def client(port, data):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('localhost', port))
    sock.send(json.dumps(data).encode("utf-8"))
    sock.close()

def keygen():
    AT_key = get_random_bytes(16)
    BT_key = get_random_bytes(16)
    R_key = get_random_bytes(16)
    print("AT_key: ", AT_key.hex())
    print("BT_key: ", BT_key.hex())
    print("R_key: ", R_key.hex())
    f1 = open("AT_key.txt", "wb")
    f1.write(AT_key)
    f1.close()
    f2 = open("BT_key.txt", "wb")
    f2.write(BT_key)
    f2.close()
    f3 = open("R_key.txt", "wb")
    f3.write(R_key)
    f3.close()

def encrypt(key, temp, data):
    cipher = trans_cipher.new(key, trans_cipher.MODE_CBC, temp)
    ct_bytes = cipher.encrypt(pad(d, 16))
    ct = b64encode(ct_bytes).decode('utf-8')
    temp = b64encode(temp).decode('utf-8')
    result = json.dumps({'temp': temp, 'ciphertext': ct})
    return result

def decrypt(key, data):
    b64 = json.loads(data)
    temp = b64decode(b64['temp'])
    ct = b64decode(b64['ciphertext'])
    decipher = trans_cipher.new(key, trans_cipher.MODE_CBC, temp)
    pt = unpad(decipher.decrypt(ct), trans_cipher.block_size)
    return pt

if __name__ == "__main__":
    if len(sys.argv) > 1:
        _type = sys.argv[1]

        IS_PROTOCOL_SUCCESS = False
        A = 'alice'
        B = 'bob'
        I = 0

        ALICE_PORT = 27013
        BOB_PORT = 27014
        KDC_PORT = 27026

        if _type == 'A':
            sock = server_start(ALICE_PORT)

            dict_transmit = dict()
            dict_transmit['a'] = A
            dict_transmit['b'] = B

            f = open("AT_key.txt", "rb")
            key = f.read()
            tempv = get_random_bytes(16)
            f.close()

            while (not IS_PROTOCOL_SUCCESS):
                I = I + 1
                dict_transmit['i'] = I

                d = dict_transmit.copy()
                rand = random.getrandbits(128)
                d['r'] = rand
                d = json.dumps(d).encode("utf-8")

                dict_transmit['ea'] = encrypt(key, tempv, d)

                print("Send to Bob:")
                print("\tI:", I)
                print("\tA:", A)
                print("\tB:", B)
                print("\tEA:", dict_transmit.get('ea'))
                print("\tNonce-A:", rand)
                print("\tAT_Key:", key.hex())
                print("\tNot encrypted:", d.decode("utf-8"))
                print("\tData:", dict_transmit)
                print("\n--------------------\n")

                client(BOB_PORT, dict_transmit)
                dict_transmit.pop('ea')

                dict_receive = server_listen(sock)

                if dict_receive:
                    print("Get from Bob:")
                    print("\tI:", dict_receive.get('i'))
                    dec = decrypt(key, dict_receive.get('ea'))
                    dec = json.loads(dec)
                    print("\tNonce-A:", dec.get('r'))
                    print("\tKey:", b64decode(dec.get('key')).hex())
                    print("\tData:", dict_receive)

                if dict_receive and dict_receive.get("i") == I and dec.get('r') == rand:
                    break
            server_close(sock)

        elif _type == 'B':
            sock = server_start(BOB_PORT)

            f = open("BT_key.txt", "rb")
            key = f.read()
            tempv = get_random_bytes(16)
            f.close()

            s = ['i', 'a', 'b', 'ea']

            while (not IS_PROTOCOL_SUCCESS):
                dict_transmit = server_listen(sock)

                status = True

                for i in s:
                    if i not in dict_transmit.keys():
                        status = False

                if status:
                    I = dict_transmit.get('i')
                    A = dict_transmit.get('a')
                    B = dict_transmit.get('b')

                    d = dict_transmit.copy()
                    d.pop('ea')
                    rand = random.getrandbits(128)
                    d['r'] = rand
                    d = json.dumps(d).encode("utf-8")

                    dict_transmit['eb'] = encrypt(key, tempv, d)
                    print("Send to KDC:")
                    print("\tI:", I)
                    print("\tA:", A)
                    print("\tB:", B)
                    print("\tEA:", dict_transmit.get('ea'))
                    print("\tEB:", dict_transmit.get('eb'))
                    print("\tNonce-B:", rand)
                    print("\tBT_Key:", key.hex())

                    print("\tNot encrypted:", d.decode("utf-8"))
                    print("\tData:", dict_transmit)
                    print("\n--------------------\n")

                    client(KDC_PORT, dict_transmit)
                    dict_transmit.clear()

                    dict_receive = server_listen(sock)
                    if dict_receive:
                        print("Get from KDC:")
                        print("\tI:", dict_receive.get('i'))
                        dec = decrypt(key, dict_receive.pop('eb'))
                        dec = json.loads(dec)
                        print("\tNonce-B:", dec.get('r'))
                        print("\tKey:", b64decode(dec.get('key')).hex())
                        print("\tData:", dict_receive)

                    client(ALICE_PORT, dict_receive)

                    if dict_receive and dict_receive.get("i") == I and dec.get('r') == rand:
                        break

            server_close(sock)

        elif _type == 'KDC':
            sock = server_start(KDC_PORT)

            f = open("AT_key.txt", "rb")
            key1 = f.read()
            tempv1 = get_random_bytes(16)
            f.close()

            f = open("BT_key.txt", "rb")
            key2 = f.read()
            tempv2 = get_random_bytes(16)
            f.close()

            f = open("R_key.txt", "rb")
            key = f.read()
            f.close()

            s = ['i', 'a', 'b', 'ea', 'eb']
            state = False

            while (not IS_PROTOCOL_SUCCESS):
                dict_receive = server_listen(sock)

                status = True

                for i in s:
                    if i not in dict_receive.keys():
                        status = False

                if status:
                    I = dict_receive.get('i')
                    A = dict_receive.get('a')
                    B = dict_receive.get('b')

                    d1 = decrypt(key1, dict_receive.get('ea'))
                    d1 = json.loads(d1)
                    d2 = decrypt(key2, dict_receive.get('eb'))
                    d2 = json.loads(d2)

                    print("Get from Bob:")
                    print("\tI:", I)
                    print("\tA:", A)
                    print("\tB:", B)
                    print("\tEA_decrypt:", d1)
                    print("\tEB_decrypt:", d2)
                    print("\tData:", dict_receive)
                    print("\n--------------------\n")

                    r1 = 0
                    r2 = 0

                    if d1.get('a') == A and d1.get('b') == B and d2.get('a') == A and d2.get('b') == B and d1.get(
                            'i') == d2.get('i') and d1.get('i') == I:
                        r1 = d1.get('r')
                        r2 = d2.get('r')
                        state = True

                    if state:
                        dict_transmit = dict()
                        dict_transmit['i'] = I

                        d = dict()
                        d['r'] = r1
                        d['key'] = b64encode(key).decode('utf-8')
                        d = json.dumps(d).encode("utf-8")
                        dict_transmit['ea'] = encrypt(key1, tempv1, d)

                        print("Send to Bob:")
                        print("\tI:", I)
                        print("\tEA_decrypt:", d.decode('utf-8'))

                        d = dict()
                        d['r'] = r2
                        d['key'] = b64encode(key).decode('utf-8')
                        d = json.dumps(d).encode("utf-8")
                        dict_transmit['eb'] = encrypt(key2, tempv2, d)

                        print("\tEB_decrypt:", d.decode('utf-8'))
                        print("\tResult_key:", key.hex())
                        print("\tData:", dict_transmit)

                        client(BOB_PORT, dict_transmit)
                        break
                    client(BOB_PORT, "")

            server_close(sock)
        elif _type == 'key':
            keygen()
        else:
            print("Wrong Argument entered: ", _type)