import socket
import binascii
import main


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(binascii.unhexlify('aaaa010000010000000000000667697468756203636f6d0000010001'), ('1.1.1.1', 53))
data, _ = s.recvfrom(4096)
print(main.decode_message(binascii.hexlify(data).decode('utf-8')))
