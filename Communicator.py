

import socket
import threading
import sys
import json

import WorldEvent

SERVER_OUTPUT_PID = 41483
SERVER_PORT = 26004


class Communicator:

    def get_events(self):
        pass

    def upload_local_events(self):
        pass

    def _serialize_event(self, event):

        match type(event):
            case WorldEvent.AddPositionEvent:
                return "|" + json.dumps({"CTYPE" : "EVENT", "ETYPE" : "ADD_POSITION", "ORDER" : event.order, "POSITION" : event.position, "ID" : event.id}) + "|"
            case _:
                return False

    def _slice_chunks(self, chunk_stream):
        chunk_rest_exists = not chunk_stream[-1] == "|"

        chunk_pieces = chunk_stream.split('|')
        content_chunks = []

        for piece in chunk_pieces:
            if piece:
                content_chunks.append(piece)
        
        chunk_rest = content_chunks.pop() if chunk_rest_exists else ""
        
        return (content_chunks, chunk_rest)



class Client(Communicator):

    running = True
    csock = None

    official_events = []

    def __init__(self):
        self.csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.csock.connect((socket.gethostname(), SERVER_PORT))
        
        self.csock.send(("|" + json.dumps({"CTYPE": "JOIN_REQUEST", "USERNAME": "Bonkers"}) + "|").encode())


    def _start_receiver(self):

        chunk_rest = ""
        while self.running:    
            chunk_stream = self.csock[0].recv(1024).decode()

            if not chunk_stream:
                break

            old_rest = chunk_rest
            chunks, chunk_rest = self._slice_chunks(chunk_stream)
            if not chunks:
                break

            chunks[0] = old_rest + chunks[0]

            # Process the request
            for chunk in chunks:
                data = json.loads(chunk)

                match data.get("CTYPE"):
                
                    case "JOIN_RESPONSE":

                        if data.get("SUCCESS"):
                            print(f"Successfully logged in with ID {data.get(user_id)}")

                    case "EVENT":

                        event_type = data.get("ETYPE")

                        match event_type:
                            case "ADD_POSITION":
                                try:
                                    order = data["ORDER"]
                                    id = data["ID"]
                                    position = tuple(data["POSITION"][:2])

                                    self.official_events.append(WorldEvent.AddPositionEvent(order, position, id))
                                
                                except:
                                    print("The server sent improper ADD_POSITION event arguments")


                    case _:
                        print("The server sent a weird ass request")


    def get_events(self):
        return self.official_events


    def upload_local_events(self, local_events):
        
        serialized_local_events = [ self._serialize_event(local_event) for local_event in local_events]

        for serialized_local_event in serialized_local_events:
            if serialized_local_event:
                self.csock.send(serialized_local_event.encode())





class ClientConnection:
    socket = None
    address = None
    user_id = None
    username = None
    recent_events = []

    def __init__(self, socket, address, user_id):
        self.socket = socket
        self.address = address
        self.user_id = user_id

class Server(Communicator):

    running = True

    ssock = None
    connections = []
    registered_users = 0

    def __init__(self):
        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssock.bind((socket.gethostname(), SERVER_PORT))
        self.ssock.listen(3)
        self.running = True        
        
        
        #sys.stdout = open(f"/proc/{SERVER_OUTPUT_PID}/fd/1", "w")
        


    def _start_receiver_for(self, connection):
        
        csock = connection.socket
        chunk_rest = ""

        while self.running:

            chunk_stream = csock.recv(1024).decode()

            if not chunk_stream:
                break


            old_rest = chunk_rest
            chunks, chunk_rest = self._slice_chunks(chunk_stream)
            if not chunks:
                break

            print("cold as the cold wind")
            print(chunks, chunk_rest)

            chunks[0] = old_rest + chunks[0]

            # Process the request
            for chunk in chunks:
                data = json.loads(chunk)

                match data.get("CTYPE"):
                
                    case "JOIN_REQUEST":

                        if connection.user_id:
                            break

                        success = False
                        username = data.get("USERNAME")
                        user_id = self.registered_users
                        
                        if username:
                            success = True
                            self.registered_users += 1
                            print(f"registered user with username {username} and user id  {user_id}")

                            connection.username = username
                            connection.user_id = user_id

                            
                        # Response
                        csock.send(("|" + json.dumps({"CTYPE": "JOIN_RESPONSE", "SUCCESS": success, "USERNAME": username, "USER_ID": user_id}) + "|").encode())

                    # The only thing the communicator has to check is whether the event actually originates from
                    # the particular user ID
                    case "EVENT":

                        event_type = data.get("ETYPE")

                        match event_type:
                            case "ADD_POSITION":
                                try:
                                    order = data["ORDER"]
                                    id = data["ID"]
                                    position = tuple(data["POSITION"][:2])
                                    connection.recent_events.append(WorldEvent.AddPositionEvent(order, position, id))
                                except:
                                    print("The client sent improper ADD_POSITION event arguments")


                    case _:
                        print("The client sent a weird ass request")




    def start_listener(self):
        while self.running:
            new_socket, new_address = self.ssock.accept()
            new_connection = ClientConnection(new_socket, new_address, None)
            new_thread = threading.Thread(target=self._start_receiver_for, args=(new_connection,))
            new_thread.start()


    def get_events(self):

        dictionary = { connection.user_id : connection.recent_events for connection in self.connections}
        for connection in self.connections:
            connection.recent_events = []
        return dictionary

    def upload_local_events(self, local_events):
        
        serialized_local_events = [ self._serialize_event(local_event) for local_event in local_events]

        for serialized_local_event in serialized_local_events:
            print("This is the meaning of life", serialized_local_event)
            for connection in self.connections:
                if serialized_local_event:
                    connection.socket.send(serialized_local_event.encode())


