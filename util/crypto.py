from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.fernet import Fernet
import struct

import sys

KEY_SIZE = 512
KEY_PATH = "keys/"

def generer_cles():
	sk = rsa.generate_private_key(
	    public_exponent=65537,
	    key_size=KEY_SIZE,
	    backend=default_backend()
	)
	pk = sk.public_key()
	fk = Fernet.generate_key() 
	return (sk,pk,fk)


def crypter_msg(msg, pk):

	encrypted = pk.encrypt(
	    msg.encode(),
	    padding.PKCS1v15(),
	)
	return int.from_bytes(encrypted, "big")

def decrypter_msg(msg, sk):
	msg = int(msg)
	ch = msg.to_bytes((msg.bit_length() + 7) // 8, byteorder='big')
	original_message = sk.decrypt(
	    ch,
	    padding.PKCS1v15(),
	)
	return original_message.decode()

	
def sym_crypter_msg(msg, fk):

	f = Fernet(fk)
	encrypted = f.encrypt(msg.encode())
	return int.from_bytes(encrypted, "big")

def sym_decrypter_msg(msg, fk):
	f = Fernet(fk)
	msg = int(msg)
	ch = msg.to_bytes((msg.bit_length() + 7) // 8, byteorder='big')
	original_message = f.decrypt(ch)
	return original_message.decode()	
# la fonction que stock les clé dans 2 fichiers: [nom]_private_key.pem, [nom]_public_key.pem
def store_keys(sk,pk,fk,name,PSSWRD):
	
	pem = sk.private_bytes(
		encoding=serialization.Encoding.PEM,
		format=serialization.PrivateFormat.PKCS8,
		encryption_algorithm=serialization.BestAvailableEncryption(PSSWRD)
		)
	file_name=name+'_private_key.pem'
	with open(KEY_PATH+file_name, 'wb') as f:
		f.write(pem)

	pem = pk.public_bytes(
		encoding=serialization.Encoding.PEM,
		format=serialization.PublicFormat.SubjectPublicKeyInfo)
		
	file_name=name+'_public_key.pem' 
	with open(KEY_PATH+file_name, 'wb') as f:
		f.write(pem)

	file_name=name+'_sym_key.pem' 
	with open(KEY_PATH+file_name, 'wb') as f:
		f.write(fk)


# public key deserialization 
def get_pub_key(name):
	
	with open(KEY_PATH+name+'_public_key.pem', 'rb') as f:

		public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())

	return public_key

# private key deserialization 
def get_sec_key(name,PASSWRD): 
	PASSWRD = PASSWRD.to_bytes((PASSWRD.bit_length() + 7) // 8, byteorder='big')
	with open(KEY_PATH+name+'_private_key.pem', 'rb') as f:
		secret_key = serialization.load_pem_private_key(f.read(),password=PASSWRD, backend=default_backend())
	
	return secret_key

# private key deserialization 
def get_sym_key(name): 
	
	with open(KEY_PATH+name+'_sym_key.pem', 'rb') as f:
		fernet_key = f.read()
	
	return fernet_key
	
