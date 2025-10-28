
import Manipulator
import Communicator
import threading

import WorldEvent
# Syncs events with server events
# 


# Passes proper events for execution and fixes broken order upon update
class EventManager:

    world = None
    manipulator = None
    communicator = None

    authoritative = True
    serving = False

    history = []

    old_local = []
    new_local = []
    new_official = []

    def __init__(self, world, authoritative=True, serving=False):
        self.world = world
        self.manipulator = Manipulator.Manipulator(world)

        self.authoritative = authoritative
        self.serving = serving

        if self.serving:
            self.communicator = Communicator.Server() # Managing a server
            listener_thread = threading.Thread(target=self.communicator.start_listener)
            listener_thread.start()

        if not self.authoritative:
            self.communicator = Communicator.Client() # Playing on a server
            listener_thread = threading.Thread(target=self.communicator._start_receiver)
            listener_thread.start()

        if self.authoritative and not self.serving:
            pass # Playing offline



    # Events caused by player input or physics
    def add_local_event(self, event):
        self.new_local.append(event)


    def _evaluate_event_log(self, user_id, event_log):
        
        for event in event_log:
            
            # Check order
            event.order = len(self.history) + len(self.new_local) + 1

            match type(event):

                case WorldEvent.AddPositionEvent:
                    # Check if that user_id has autority over that particular Position object ... ?
                    self.add_local_event(event)
                case _:
                    print("That's a weird ass event EventManager.py (server side)")

    def update(self):


        # Offline
        if self.authoritative and not self.serving:

            # Apply
            for new_event in self.new_local:
                self.manipulator.incorporate(new_event)
                self.history.append(new_event)

            self.new_local = []


        # As server
        if self.authoritative and self.serving:
            
            # Get, Apply
            client_event_logs = self.communicator.get_events()

            for user_id in client_event_logs.keys():
                self._evaluate_event_log(user_id, client_event_logs[user_id])

            for new_event in self.new_local:
                self.manipulator.incorporate(new_event)
                self.history.append(new_event)

            # Upload
            self.communicator.upload_local_events(self.new_local)
            self.new_local = []


        # As client
        if not self.authoritative:

            # Get, Apply
            official_events = self.communicator.get_events()
            self.communicator.reset_events()

            for old_local_event in self.old_local:
                self.manipulator.revert(old_local_event)

            for official_event in official_events:
                self.manipulator.incorporate(official_event)

            for new_local_event in self.new_local:
                self.manipulator.incorporate(new_local_event)

            # Upload
            self.communicator.upload_local_events(self.new_local)
            self.old_local = self.new_local
            self.new_local = []

