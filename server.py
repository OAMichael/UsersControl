#!/usr/bin/python3

import select
import socket
import sys
import signal
import traceback

BUFSIZE = 2048
ENCODE = 'utf-8'
TCP_KEEPALIVE_TIMEOUT = 300

class TcpServer(object):

    def __init__(self, port, quantity, host = "0.0.0.0"):
        self.clients = 0
        self.clientdict = {}
        self.connection_list = []

        # AF_INET - internet socket, SOCK_STREAM - connection-based protocol for TCP, 
        # IPPROTO_TCP - choosing TCP
        print ("* Creating the server socket")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Check and turn on TCP Keepalive
        x = self.server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
        if (x == 0):
            print ("* Socket Keepalive off, turning on")
            x = self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            print ('* setsockopt ' + str(x))
            # Overrides value (in seconds) for keepalive
            self.server_socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPALIVE if sys.platform.startswith('darwin')
                                                                               else socket.TCP_KEEPINTVL, TCP_KEEPALIVE_TIMEOUT)
        else:
            print ("* Socket Keepalive already on")

        try:
            # Assigning IP and port num to socket
            self.server_socket.bind((host, port))
        except socket.error:
            print ("* Socket bind failed!")
            traceback.print_exc()
            sys.exit(1)

        try:
            # Putting server into listening mode
            self.server_socket.listen(quantity)
        except socket.error:
            print ("* Socket listen failed!")
            traceback.print_exc()
            sys.exit(1)

        signal.signal(signal.SIGINT, self.sighandler)
        print("* Socket initializing completed!")


    def sighandler(self, signum, frame):

        print("* Disconnecting clients...")

        for client in self.connection_list:
            if client != self.server_socket and client != sys.stdin:
                client.shutdown(socket.SHUT_RDWR)
                client.close()

        self.server_socket.close()
        sys.exit(1)


    def serve(self):

        self.connection_list = [self.server_socket, sys.stdin]

        work = True

        while work:

            try:
                read_sockets, write_sockets, error_sockets = select.select(self.connection_list,[],[])
            except Exception:
                traceback.print_exc()
                break

            for sock in read_sockets:

                if sock == self.server_socket:
                    # Processing new client
                    client, address = self.server_socket.accept()
                    print(f"[Server]: New connection with {str(address)} requested...")
                    self.connection_list.append(client)
                    self.clientdict[client] = address

                # Incoming message from a client
                else:
                    try:
                        data = sock.recv(BUFSIZE)
                        if data:
                            if data.startswith(b'$'):
                                data = data.decode(ENCODE)
                                data = data[1:-1]
                                fileheader = data.split("_")
                                filename = fileheader[0]
                                filelength = int(fileheader[1])

                                sock.sendall("$filenamereceived$".encode(ENCODE))
                                #print("[Server]: receiving...")
                                file = open('n_' +filename, 'wb')
                                chunks = b''
                                bytes_recd = 0
                                while bytes_recd < filelength:
                                    chunk = sock.recv(min(filelength - bytes_recd, BUFSIZE))
                                    if chunk == b'':
                                        raise RuntimeError("socket connection broken")
                                    chunks = chunks + chunk
                                    bytes_recd = bytes_recd + len(chunk)

                                #print("[Server]: done receiving! Writing... ")
                                bytes_wrt = 0
                                try:
                                    file.write(chunks)
                                except Exception:
                                    traceback.print_exc()

                                #print("[Server]: done writing!")
                                file.close()
                                sock.sendall("$filereceived$".encode(ENCODE))
                    except socket.error:
                        # Remove sock
                        del self.clientdict[sock]
                        self.connection_list.remove(sock)
                    except Exception:
                        traceback.print_exc()


        self.server_socket.close()


if __name__ == "__main__":
    host = str(input("Input server IP adress: "))
    port = int(input("Input server port: "))
    quantity = int(input("Input max quantity of users: "))

    FileServer = TcpServer(port, quantity, host)
    FileServer.serve()












