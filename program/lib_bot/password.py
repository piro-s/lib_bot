from hashlib import sha256

password = 'PASSWORD'
hash = sha256(password.encode())
with open('credential', 'w+') as file:
    file.write(hash.hexdigest()) # passwd