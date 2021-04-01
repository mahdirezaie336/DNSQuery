import socket
import threading


def handler(client_socket: socket.socket, address):
    client_socket.send(b'\nSend "exit" to terminate safely.\n')

    try:
        while True:
            data = c.recv(4096)
            data_in_string = data.decode('uft-8')
            print('from client:', address[0], data_in_string)
            if data_in_string.strip() == 'exit':
                break
            client_socket.send(b'Good job boy!\n')
    finally:
        print('Connection closed:', address[0], address[1])
        client_socket.close()


# Creating listening socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 16800))
print('Socket bound to port 16800.')

# Listen
s.listen()

# Creating threads
try:
    while True:
        print('Waiting for client...')
        c, address = s.accept()
        print('Client accepted: ', str(address[0]) + ':' + str(address[1]))
        threading.Thread(target=handler, args=(c, address)).start()
finally:
    s.close()
