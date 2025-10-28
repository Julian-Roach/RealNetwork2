

import socket
import threading
import sys
import json

import copy

import WorldEvent

import macros as M

# TODO: "new_official_events" here and a few other synonyms are used in different places. Those are horrible naming choices.
# come up with a better nomenclature for temporarily storing new external events

class Communicator:

    def get_events(self):
        pass

    def upload_local_events(self):
        pass

    def _serialize_event(self, event):
        return "|" + json.dumps({M.JTAG_CHUNK_TYPE : M.JKEY_CHUNK_TYPE_EVENT, M.JTAG_EVENT : event.decompose()}) + "|"

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

    new_official_events = []

    def __init__(self):
        self.csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.csock.connect((socket.gethostname(), M.SERVER_PORT))
        
        self.csock.send(("|" + json.dumps({M.JTAG_CHUNK_TYPE: M.JKEY_CHUNK_TYPE_JOIN_REQUEST, M.JTAG_USERNAME: "Bonkers"}) + "|").encode()) # TODO it cannot stay Bonkers.


    def _start_receiver(self):

        chunk_rest = ""
        while self.running:    
            chunk_stream = self.csock.recv(1024).decode()

            if not chunk_stream:
                break
            print("(Client) New stream:", chunk_stream)



            old_rest = chunk_rest
            chunks, chunk_rest = self._slice_chunks(chunk_stream)
            if not chunks:
                break

            chunks[0] = old_rest + chunks[0]

            # Process the request
            for chunk in chunks:
                data = json.loads(chunk)

                match data.get(M.JTAG_CHUNK_TYPE):
                
                    case M.JKEY_CHUNK_TYPE_JOIN_RESPONSE:

                        user_id = data.get(M.JTAG_USER_ID)
                        if data.get(M.JTAG_SUCCESS):
                            print(f"Successfully logged in with ID {user_id}")

                    case M.JKEY_CHUNK_TYPE_EVENT:

                        try:
                            event_json = data.get(M.JTAG_EVENT)
                            event = WorldEvent.compose_world_event(event_json)
                            self.new_official_events.append(event)
                        except:
                            print("The server sent a weird JSON structure for the event")
                            break

                    case _:
                        print("The server sent a weird ass request")


    def get_events(self):
        return self.new_official_events

    def reset_events(self):
        self.new_official_events = []


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
        self.ssock.bind((socket.gethostname(), M.SERVER_PORT))
        self.ssock.listen(3)
        self.running = True        
        
        
        #sys.stdout = open(f"/proc/{SERVER_OUTPUT_PID}/fd/1", "w")
        


    def _start_receiver_for(self, connection):
        
        csock = connection.socket
        chunk_rest = ""

        while self.running:

            chunk_stream = csock.recv(1024).decode()
            print("(Server) New stream:", chunk_stream)

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

                #print(str(JKEY_CHUNK_TYPE_JOIN_REQUEST))
                #print("root cause", data.get(JTAG_CHUNK_TYPE))
                

                match data.get(M.JTAG_CHUNK_TYPE):
                
                    case M.JKEY_CHUNK_TYPE_JOIN_REQUEST:

                        if connection.user_id:
                            break

                        success = False
                        username = data.get(M.JTAG_USERNAME)
                        user_id = self.registered_users + 1
                        
                        if username:
                            success = True
                            self.registered_users += 1
                            print(f"registered user with username {username} and user id  {user_id}")

                            connection.username = username
                            connection.user_id = user_id

                            
                        # Response
                        csock.send(("|" + json.dumps({M.JTAG_CHUNK_TYPE: M.JKEY_CHUNK_TYPE_JOIN_RESPONSE, M.JTAG_SUCCESS: success, M.JTAG_USERNAME: username, M.JTAG_USER_ID : user_id}) + "|").encode())

                    # The only thing the communicator has to check is whether the event actually originates from
                    # the particular user ID

                    case  M.JKEY_CHUNK_TYPE_EVENT:
                    
                        try:
                            event_json = data.get(M.JTAG_EVENT)
                            event = WorldEvent.compose_world_event(event_json)
                            # Perform checks, perhaps? Oh well.. maybe it can be done by the event manager as well . ? Presumably so
                            connection.recent_events.append(event)
                        except:
                            print("The client sent a weird JSON structure for the event")
                            break

                    case _:
                        print("The client sent a weird ass request")


    def start_listener(self):
        while self.running:
            new_socket, new_address = self.ssock.accept()
            new_connection = ClientConnection(new_socket, new_address, None)
            self.connections.append(new_connection)

            new_thread = threading.Thread(target=self._start_receiver_for, args=(new_connection,))
            new_thread.start()


    def get_events(self):

        event_log = { connection.user_id : connection.recent_events for connection in self.connections} # probably requires copy.copy()-ing

        # for v in event_log.values():
        #     if v:
        #         print(event_log, 'ye')
        #         break

        for connection in self.connections:
            connection.recent_events = []

        return event_log

    def upload_local_events(self, local_events):
        
        serialized_local_events = [ self._serialize_event(local_event) for local_event in local_events]

        for serialized_local_event in serialized_local_events:
            for connection in self.connections:
                if serialized_local_event:
                    connection.socket.send(serialized_local_event.encode())


