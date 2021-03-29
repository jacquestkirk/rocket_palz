"""Client for Rocket Pals game."""
import copy
import queue
import json
import socket
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QComboBox, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer

import common

POLLING_PERIOD = 10  # mili-seconds, poll the server at this rate


class GameClient(object):
    """Class to manage the game client."""
    def __init__(self,
                 server_location: str,
                 player: common.PlayerEnum,
                 command_queue: queue.Queue):
        """
        Args:
            server_location (str): server ip address and port. e.g. localhost:10018
            player (common.PlayerEnum): the player that this client is playing as.
            command_queue (queue.Queue): Command queue. Contains common.Messages. Commands to be sent to the server are
                                            put on this queue.
        """

        self.player = player
        self.command_queue = command_queue

        # create socket
        hostname, port = server_location.split(':')
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('connecting to {}:{}'.format(hostname, port))
        self.client_socket.connect((hostname, int(port)))
        self.player_locations = {}

    def poll(self):
        """Poll the server. Send it your command and get a dictionary of player locations back."""
        if self.command_queue.empty():
            # If there are no commands in the queue send a none message to just get player locations back.
            next_command = common.Messages.none
        else:
            next_command = self.command_queue.get()
        # Send data
        message_dict = {
            'name': self.player.value,
            'command': next_command.value
        }
        message = json.dumps(message_dict)
        common.debug_print('message sent: {}'.format(message_dict))
        self.client_socket.sendall(message.encode())

        # receive player locations
        locations_str = self.client_socket.recv(common.BUFFER_SIZE).decode()
        common.debug_print('message received: {}'.format(locations_str))
        self.player_locations = json.loads(locations_str)

    def cleanup(self):
        """Close socket"""
        print('closing socket')
        self.client_socket.close()

    def __del__(self):
        self.cleanup()


class ServerSelector(QWidget):
    """Window that allows you to select a server and player."""
    def __init__(self):
        super().__init__()

        # server selector
        self.server_label = QLabel(self)
        self.server_label.setText('Enter server to connect to. e.g. localhost:10018')
        self.server_label.move(20, 10)

        self.server_input = QLineEdit(self)
        self.server_input.move(20, 30)
        self.server_input.resize(200, 20)

        # character selector
        self.player_label = QLabel(self)
        self.player_label.setText('Select the character you want to play as.')
        self.player_label.move(20, 60)

        self.player_combo = QComboBox(self)
        for player, _ in common.images.items():
            self.player_combo.addItem(player.value)
        self.player_combo.move(20, 80)

        # go button
        self.go_button = QPushButton(self)
        self.go_button.setText("Let's go!!!")
        self.go_button.move(20, 110)
        self.go_button.clicked.connect(self.start_the_game_already)

        self.resize(400, 140)

        self.show()

    def start_the_game_already(self):
        """Callback function for go_button."""
        self.hide()
        print(self.server_input.text())
        print(str(self.player_combo.currentText()))

        main_window.show()
        main_window.connect(self.server_input.text(), str(self.player_combo.currentText()))


class MainWindow(QWidget):
    """The main game window."""
    def __init__(self):
        super().__init__()
        self.resize(750, 750)

        self.setWindowTitle("Game")
        self.players = {}

        self.load_players()
        self.command_queue = queue.Queue()
        self.game_client = None

        self.timer = None

    def connect(self, server_address, player):
        """
        Connect to the game server. Spin up a QTimer that repeatedly sends commands and queries the server for player
        locations.
        Args:
            server_address (str): server ip address and port. e.g. localhost:10018
            player (str): the player that this client is playing as. Should correspond to common.PlayerEnum

        """
        self.game_client = GameClient(
            server_address,
            common.PlayerEnum(player),
            self.command_queue
        )
        self.timer = QTimer()
        self.timer.setInterval(POLLING_PERIOD)
        self.timer.timeout.connect(self.poll_server)
        self.timer.start()

    def poll_server(self):
        """
        Get player locations from the server. Move players on the screen to match.
        """
        self.game_client.poll()
        self.update_display()

    def initialize_player(self, player: common.PlayerEnum):
        """
        Create an image for the given player. Hide it for now.
        Args:
            player (common.PlayerEnum): player to intialize
        """
        print(player)
        if player in common.images.keys():
            print(common.images[player])
            image = QPixmap(common.images[player])
            player_image = QLabel(self)
            player_image.setPixmap(image)
            player_image.hide()
            self.players[player.value] = player_image

    def load_players(self):
        """
        Create an image for all possible players.
        """
        for player in common.PlayerEnum:
            self.initialize_player(player)

    def update_display(self):
        """
        Move players around the screen with location information from the server. If the server doesn't have information
        on the player, they levt the game, so hide them.
        """
        player_locations = copy.deepcopy(self.game_client.player_locations)
        for player_name, player_image in self.players.items():
            if player_name in player_locations.keys():
                player_image.show()
                player_image.move(
                    player_locations[player_name]['x'],
                    player_locations[player_name]['y'])
            else:
                player_image.hide()

    def keyPressEvent(self, event):
        """
        Executes when a key is pressed.
        Add a command to the command queue based on which key is pressed.
        Args:
            event: The key that was pressed.
        """
        if event.key() == Qt.Key_Up:
            self.command_queue.put(common.Messages.up)
        elif event.key() == Qt.Key_Down:
            self.command_queue.put(common.Messages.down)
        elif event.key() == Qt.Key_Left:
            self.command_queue.put(common.Messages.left)
        elif event.key() == Qt.Key_Right:
            self.command_queue.put(common.Messages.right)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    server_selector = ServerSelector()
    main_window = MainWindow()

    sys.exit(app.exec_())
