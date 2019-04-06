import socket
from threading import Thread
import time
import sys
class TCP(object):
    def Get_Protocol(self):
        protocol = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        protocol.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return protocol
    def __init__(self, port=80):
        self.name = "TCP"
        self.protocol = self.Get_Protocol()
        self.port = port
        self.listen = False
        #id = [connection, [ip, port]]
        self.list_connected = {}
        self.id_connected = 0 #id that not yet used
        
    def __str__(self):
        return "TCP Module"
    
    def Check_Is_Address(self, address):
        success = 1
        ip, port = address
        ip = ip.split(".")
        if (len(ip)!=4):
            success = 0
        for i in ip:
            try:
                if not ((int(i) >= 0) and (int(i) <= 256)):
                    success = 0
            except:
                success = 0
        try:
            port = int(port)
        except:
            success = 0
        if (not success):
            raise ValueError("%s is not an address. expected: ['ip', port]")
        return success
    def Search_Id(self, address):
        self.Check_Is_Address(address)
        angka = 0
        for i in self.list_connected:
            if (self.list_connected[i][1]==address):
                return angka
            angka+=1
        raise ValueError("Address %s is not in list connected" %(str(address)))
    
    def Connect_By_ID(self, connection_id, address):
        self.Check_Is_Address(address)      
        self.list_connected[connection_id][0].connect(address)
    def Connect(self, address = []):
        self.Check_Is_Address(address)        
        address = tuple(address)
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(address)
            self.list_connected[self.id_connected] = [connection, address]
            self.id_connected += 1
        except Exception as error:
            raise ConnectionError("Cant connect to %s. %s" %(str(address), str(error)))
        
    def Disconnect_By_ID(self, connection_id=0):
        self.list_connected[connection_id][0].close()
        #del self.list_connected[connection_id]
        
    def Disconnect(self, address=[]):
        self.Check_Is_Address(address)
        connection_id = "Unknown"
        address = tuple(address)
        #looking for existing connection...
        try:
            connection_id = self.Search_Id(address)
        except ValueError:
            pass

        if (connection_id=="Unknown"):
            raise ValueError("Address %s is not connected yet" %(str(address)))
        
        #closing connection
        try:
            self.list_connected[connection_id][0].close()
            #del self.list_connected[connection_id]
        except Exception as err:
            raise ConnectionError("Cannot close connection with %s. id: %s" %(str(address), connection_id))
        
        
    def Send(self, address, data, close_after_send=1):
        self.Check_Is_Address(address)
        try:
            data = data.encode("utf-8")
        except:
            pass
        
        connection_id = "Unknown"
        
        #looking for existing connection
        try:
                connection_id = self.Search_Id(address)
                #print("Found existing connection to {s}\twith id: {l}".format(s=str(self.list_connected[connection_id][1]), l=connection_id))
        except ValueError:
            pass
        
        #if neither existing connection, lets connect
        if (connection_id=="Unknown"):
            self.Connect(address=address)
            connection_id = self.id_connected-1
            
        try:
            self.list_connected[connection_id][0].send(data)
            
            #close it, after sending data, so the browser know its end
            if (close_after_send):
                self.list_connected[connection_id][0].close()
        except Exception as err:
            raise ConnectionError("Error while sending data to %s. Closing Connection... : %s" %(str(self.list_connected[connection_id][1]), str(err)))
    def Send_By_ID(self, connection_id, data, close_after_send=1):
        try:
            data = data.encode("utf-8")
        except:
            pass
        
        self.list_connected[connection_id][0].send(data)
        if (close_after_send):
            self.list_connected[connection_id][0].close()
        
    def Get_Data(self, connection_id, buffer=1024):
        return self.list_connected[connection_id][0].recv(buffer)
        
    def Start_Listen(self, func=[], address=["Unknown"], allow_multiple_connection=True):
        if (not self.listen):
            

            self.protocol.bind(("0.0.0.0", self.port))
            self.protocol.listen()
            self.listen = True
            while (self.listen):
                try:
                    client, addr = self.protocol.accept();
                except OSError:
                    if ((self.listen)):
                        raise OSError
                        return
                    break
                addr = list(addr)
                allowed = 0
                #handling address allowed to receive
                if (address!=["Unknown"]):
                    for i in address:
                        if(i!=addr[0]):
                            continue
                        else:
                            allowed = 1
                #handling allow_multiple_connection
                try:
                    self.Search_Id(addr)
                    continue
                except ValueError:
                    pass
                self.list_connected[self.id_connected] = [client, addr]
                #change the dynamic port to listen port
                addrr = [addr[0], self.port]
                for i in func:
                    Thread(target=i, args=[self.Get_Data(self.id_connected), self.id_connected, addr, addrr]).start()
                self.id_connected+=1
        else:
            raise SystemError("This protocol is already listening with port %s" %(self.port))
    def Stop_Listen(self):
        if (not self.listen):
            return
        self.listen = False;
        self.protocol.shutdown(socket.SHUT_RDWR);
        self.protocol.close();
        del self.protocol
        self.protocol = self.Get_Protocol()

        
