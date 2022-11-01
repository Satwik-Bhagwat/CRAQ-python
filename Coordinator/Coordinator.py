import socket
import os
import threading
import json
import shutil

HEADER = 16
PORT = 5051
SERVER_IP = "192.168.1.12"
#SERVER_IP = socket.gethostbyname(socket.gethostname())
# gw = os.popen("ip -4 route show default").read().split()
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect((gw[2], 0))
# ipaddr = s.getsockname()[0]
# gateway = gw[2]
# host = socket.gethostname()
# print ("IP:", ipaddr, " GW:", gateway, " Host:", host)
ADDRESS = (SERVER_IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
READ = 0

config_file = open("./Coordinator_config.json","r+")
config = json.load(config_file)
no_of_nodes = config["number_of_nodes"]
head_node = config["head_node"]
tail_node = config["tail_node"]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def register_node():
    global no_of_nodes
    global config
    global tail_node
    no_of_nodes = no_of_nodes + 1
    config["number_of_nodes"] += 1
    new_tail_node = "NODE" + str(no_of_nodes)
    shutil.copytree("../" + tail_node, "../" + new_tail_node)
    config["tail_node"] = new_tail_node
    tail_node = new_tail_node
    config["nodes_list"].append(new_tail_node)
    config_file.seek(0)
    config_file.truncate(0)
    json.dump(config, config_file, indent=4)

def write_data(data):
    key = data.partition("\n")[0]
    value = "\n".join(data.split("\n")[1:])
    print(f"We are writing files. Key:{key}, Value:{value}")
    ADDRESS1 = (SERVER_IP, 5053)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind(('192.168.1.12',5060))
    client.connect(ADDRESS1)

    message = data.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def read_data(key):
    print("We are reading files. Key:{key}")

def handle_client(connection, address):
    print(f"Client with IP {address} connected")
    connected = True
    while connected:
        read_write_choice = connection.recv(1).decode(FORMAT)
        if read_write_choice:
            read_write_choice = int(read_write_choice)
            msg_length = int(connection.recv(HEADER).decode(FORMAT))
            received_data = connection.recv(msg_length).decode(FORMAT)
            if read_write_choice == READ:
                print(f"Received read request from [{address}]")
                connection.send("Received read request".encode(FORMAT))
                read_data(received_data)
            else:
                print(f"Received write request from [{address}]")
                write_data(received_data)
                connection.send("Write Successful".encode(FORMAT))
            connected = False
    print()
    connection.close()

def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn,addr))
        thread.start()
        print(f"Active Connections: {threading.activeCount() - 1}")

if __name__ == "__main__":
    Node_register = int(input("[Coordinator] Do you want to register a Node? [1]-Yes, [0]-No: "))
    if Node_register:
        register_node()
        print("New Node Created Successfully.\nTotal number of Nodes: ",no_of_nodes)
    print("Starting Coordinator...")
    start()
