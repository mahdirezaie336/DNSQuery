import socket
import threading


def handler(client_socket: socket.socket, address):
    """ This is handler of client sockets. It just sends 'good boy' message. """
    # Sending hints
    client_socket.send(b'\nSend "exit" to terminate safely.\n')

    try:
        # Handler's infinite loop
        while True:
            data = c.recv(4096)
            data_in_string = data.decode('utf-8')
            print('from client:', address[0], data_in_string)
            if data_in_string.strip() == 'exit':
                client_socket.send(b'Thanks for being my friend...\n')
                break
            client_socket.send(b'Good job boy!\n')
    except:
        pass
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
    # Listener's infinite loop
    while True:
        print('Waiting for client...')
        c, address = s.accept()
        print('Client accepted: ', str(address[0]) + ':' + str(address[1]))
        threading.Thread(target=handler, args=(c, address)).start()
except:
    pass
finally:
    print('Closing listener...')
    s.close()
