import socket
from threading import Thread
import time

class TcpPool(object):
    def Get_Protocol(self):
        protocol = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        protocol.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return protocol
    def __init__(self, port=80):
        self.list_connected = {} # id: [connection, address] #put address because when the connection closed, address is dissappear
        self.id_connected = 0 #id that not yet used
        
    def __str__(self):
        return "TCP Module"
    
    def Search_Id(self, address):
        for id in self.list_connected:
            if (self.list_connected[id][1]==adress):
                return id
        return -1

    def Connect_By_Id(self, connection_id, address):
        self.list_connected[connection_id][0].connect(address)

    def Connect(self, address = []):       
        address = tuple(address)
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(address)
            self.list_connected[self.id_connected] = [connection, address]
            self.id_connected += 1
        except Exception as error:
            raise ConnectionError("Cant connect to %s. %s" %(str(address), str(error)))
        
    def Disconnect_By_Id(self, connection_id):
        self.list_connected[connection_id][0].close()
        #del self.list_connected[connection_id]
        
    def Disconnect(self, address=[]):
        self.Check_Is_Address(address)
        connection_id = -1
        address = tuple(address)
        #looking for existing connection...
        try:
            connection_id = self.Search_Id(address)
        except ValueError:
            pass

        if (connection_id==-1):
            raise ValueError("Address %s is not connected yet" %(str(address)))
        
        #closing connection
        try:
            self.list_connected[connection_id][0].close()
            #del self.list_connected[connection_id]
        except Exception as err:
            raise ConnectionError("Cannot close connection with %s. id: %s" %(str(address), connection_id))
        
        
    def Send(self, address, data, close_after_send=1):
        try:
            data = data.encode("utf-8")
        except:
            pass
        
        connection_id = -1
        
        #looking for existing connection
        try:
                connection_id = self.Search_Id(address)
                #print("Found existing connection to {s}\twith id: {l}".format(s=str(self.list_connected[connection_id][1]), l=connection_id))
        except ValueError:
            pass
        
        #if neither existing connection, lets connect
        if (connection_id==-1):
            self.Connect(address=address)
            connection_id = self.id_connected-1
            
        try:
            self.list_connected[connection_id][0].send(data)
            
            #close it, after sending data, so the browser know its end
            if (close_after_send):
                self.list_connected[connection_id][0].close()
        except Exception as err:
            raise ConnectionError("Error while sending data to %s. Closing Connection... : %s" %(str(self.list_connected[connection_id][1]), str(err)))

    def Send_By_Id(self, connection_id, data, close_after_send=1):
        try:
            data = data.encode("utf-8")
        except:
            pass
        
        self.list_connected[connection_id][0].send(data)
        if (close_after_send):
            self.list_connected[connection_id][0].close()
        
    def Recv_Data(self, connection_id, buffer=1024):
        return self.list_connected[connection_id][0].recv(buffer)
        
    def Start_Listen(self, func=[], black_list_address=[]):
        def listen0():
            self.connection[self.id_connected] = self.Get_Protocol()
            self.id_connected+=1
            self.connection[self.id_connected].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.connection[self.id_connected].bind(("0.0.0.0", self.port))
            self.connection[self.id_connected].listen()
            
            while (not self.connection[self.id_connected]._closed):
                client, addr = self.connection[self.id_connected].accept()
                for f in func:
                    Thread(target=f, args=[client, addr]).start()

        Thread(target=listen0, args=[]).start()

    def Stop_Listen(self, id):
        self.connection[self.id_connected].close()
