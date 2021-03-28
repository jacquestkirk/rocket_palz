import argparse
import sys
from PyQt5.QtWidgets import QApplication
import rocket_palz

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('server', type=str,
                        help='server address')
    parser.add_argument('player', type=str,
                        help='name of the person you want to be')
    args = parser.parse_args()

    app = QApplication(sys.argv)

    main_window = rocket_palz.MainWindow()
    main_window.show()
    main_window.connect(args.server, args.player)

    sys.exit(app.exec_())
