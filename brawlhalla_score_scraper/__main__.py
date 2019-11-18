from .gui.gui import GUI
gui = GUI()
gui.run()


# from .constants import Positions
# from .screen import is_on_scores_screen
# import time
# COUNT = 10
#
# times = []
# for _ in range(COUNT):
#     start = time.time()
#     _ = is_on_scores_screen()
#     times.append(time.time() - start)
#
#
# print('TOTAL %.4f - AVG %.4f' % (sum(times), sum(times) / COUNT))


# from .delegate import SocketDelegate, SocketEmitter
# from typing import Any
# from threading import Thread
# import time
#
#
# class Receiver(SocketDelegate):
#
#     def on_event(self, event: str, data: Any = None):
#         print(event, data)
#
#     def check_event(self, event: str, data: Any = None):
#         return int(event)
#
#
# PORT = 2000
# r = Receiver()
# e = SocketEmitter()
# e.connect(PORT)
# r.connect(PORT)
# e.wait_for_client()
#
# e.on_event('stuff', {'a': 1, 'b': [1, 2]})
# print(e.check_event('2'))
