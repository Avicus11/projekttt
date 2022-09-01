import hashlib

def zakodiraj(s):
    return int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**8
