import socket
from _thread import *
import threading
import hashlib


def main():
    # the server will start working at the computer that it is running on
    host = 'localhost'
    port_control = 8000
    port_data = 8001
    client_count = 0

    # connect the host and ports to the socket server
    # for both control and data channels
    try:
        # TCP protocol by default
        server_control_socket = socket.socket()
        server_data_socket = socket.socket()
        server_control_socket.bind((host, port_control))
        server_data_socket.bind((host, port_data))
    except socket.error as e:
        print("can't create a socket")
        print(str(e))
        return

    # The server is listening on the ports for clients
    server_control_socket.listen()
    server_data_socket.listen()
    print('Server is listening..')

    # The server is always working, need to stop it manually
    while True:
        # get the client sockets
        client_control, address_c = server_control_socket.accept()
        client_data, address_d = server_data_socket.accept()
        print('Control channel connected to: ' + address_c[0] + ':' + str(address_c[1]))
        print('Data channel connected to: ' + address_d[0] + ':' + str(address_d[1]))
        # start the treads, for multiple clients
        start_new_thread(channels_handler, (client_control, client_data,))
        client_count += 1
        print('Client number: ' + str(client_count))


# save all the clients MACs and codes in tuples
# clients is a set of tuples so if a client is already in the set, he will not be added again
# for clients that wants to connect to the server several times - the MAC and code will be the same
# I used a set to save space and time - just adding no need to remove or to check if the client is already in the set
clients = set()
# a lock for mutual exclusion between threads
lock = threading.Lock()


# write the message to the log file
def write_to_log(message):
    with open('logfile.txt', 'a') as logFile:
        logFile.write(message + '\n')

        
# handler for control and data channels
def channels_handler(control_channel, data_channel):
    try:
        # handler for control channel port 8000
        unique = control_channel.recv(2048)
        # use the sha-1 hash function to generate a unique code, a better hash function than the default one (hash())
        code = hashlib.sha1(unique).hexdigest()
        # send the code to the client
        control_channel.sendall(str.encode(code))
    except socket.error as e:
        print("can't receive or send on control channel")
        print(str(e))
        return
    # encode the code to bytes to match the code received from the data channel
    code = code.encode()
    # protect mutual resource
    lock.acquire()
    clients.add((unique, code))
    lock.release()
    control_channel.close()

    # handler for data channel port 8001
    # this flag indicates if the message was written to the log file
    flag = False
    try:
        message = data_channel.recv(2048)
    except socket.error as e:
        print("can't receive on data channel")
        print(str(e))
        return
    message = message.split()
    # message = message + ' ' + identifier + ' ' + str(code)
    # message[0] = message
    # message[1] = identifier
    # message[2] = code

    # protect critical code
    lock.acquire()
    for unique, code in clients:
        if unique == message[1] and code == message[2]:
            flag = True
            # write a string to the file, not bytes
            mess = message[0].decode()
            write_to_log(mess)
            break
    lock.release()
    try:
        if not flag:
            data_channel.sendall(str.encode('error'))
        else:
            data_channel.sendall(str.encode('success'))
    except socket.error as e:
        print("can't send on data channel")
        print(str(e))
    data_channel.close()


if __name__ == '__main__':
    main()
