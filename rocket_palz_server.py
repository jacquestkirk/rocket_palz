import json
import socket
import threading
import common

PORT = 10018
UPDATE_TIME_SEC = 1  # seconds


class PlayerLocations(object):
    def __init__(self):
        self.player_locations = {}  # key =player name, value = x and y coordinates of player

    def update_locaton(self, player, command):
        # add new player if it doesn't exist
        if player not in self.player_locations.keys():
            self.player_locations[player] = {
                'x': 0,
                'y': 0
            }

        # interpret commands
        if command == common.Messages.up.value:
            self.player_locations[player]['y'] -= 1
        elif command == common.Messages.down.value:
            self.player_locations[player]['y'] += 1
        elif command == common.Messages.left.value:
            self.player_locations[player]['x'] -= 1
        elif command == common.Messages.right.value:
            self.player_locations[player]['x'] += 1

    def remove_player(self, player):
        del self.player_locations[player]

    def json(self):
        return json.dumps(self.player_locations)


class ClientManagementThread(threading.Thread):
    def __init__(
            self,
            connection,
            client_address,
            player_locations
    ):
        super().__init__()
        self.connection = connection
        self.client_address = client_address
        self.player_name = None
        self.player_locations = player_locations

    def run(self):
        try:
            print('{} connected'.format(self.client_address))
            # print received data
            while True:
                message = self.connection.recv(common.BUFFER_SIZE)
                if not message:
                    break

                common.debug_print('message_received: {}'.format(message))

                message_dict = json.loads(message.decode())
                self.player_locations.update_locaton(
                    player=message_dict['name'],
                    command=message_dict['command']
                )

                self.player_name = message_dict['name']

                common.debug_print('message sent: {}'.format(self.player_locations.json()))
                self.connection.sendall(self.player_locations.json().encode())

        finally:
            # Clean up the connection
            print('{} closed'.format(self.client_address))
            self.connection.close()
            self.player_locations.remove_player(self.player_name)


class GameServer(object):
    def __init__(self):
        self.player_locations = PlayerLocations()

        self.client_threads = []

        # Create a TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        host_ip = self.get_ip_address()
        print("Starting game server at {}:{}".format(host_ip, PORT))
        self.socket.bind((host_ip, PORT))

        # Listen for incoming connections
        self.socket.listen()

    @staticmethod
    def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    def run(self):
        while True:
            # Wait for a connection
            print("waiting for connections")
            connection, client_address = self.socket.accept()
            newthread = ClientManagementThread(
                connection,
                client_address,
                self.player_locations
            )
            newthread.start()
            self.client_threads.append(newthread)

        for client_thread in self.client_threads:
                client_thread.join()


if __name__ == '__main__':
    game_server = GameServer()
    game_server.run()
