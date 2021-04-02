#!/usr/bin/env python3

import socket
import binascii


print('Starting server...')
# Creating listening socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 16800))
print('Socket bound to port 16800 UDP.')

try:
    # Server's infinite loop
    while True:
        print('Waiting for message...')
        message, address = s.recvfrom(4096)
        print('Client accepted: ', str(address))
        print('Message is:', binascii.hexlify(message))
        data = binascii.unhexlify('eeee818000010001000000000470696e670265750000010001c00c0001000100014889000458c62e3c')
        print('Sending response...')
        s.sendto(data, address)
except:
    pass
finally:
    print('\nClosing listener...')
    s.close()
