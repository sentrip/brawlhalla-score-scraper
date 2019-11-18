import os
import logging
from abc import abstractmethod
from multiprocessing import Process

from flask import Flask, Blueprint, request, render_template, make_response, current_app

from ..constants import Events, Numbers, Runnable
from ..delegate import Delegate, check_event, on_event, SocketDelegate, SocketEmitter


__all__ = [
    'PlayerServer',
    'PlayerServerDelegate'
]


os.environ['WERKZEUG_RUN_MAIN'] = 'true'
logging.getLogger('werkzeug').setLevel(logging.ERROR)

delegate = None
player_gui = Blueprint('player_gui', __name__, template_folder='templates')


class PlayerServerDelegate(Delegate):
    @abstractmethod
    def get_accounts(self) -> [str]:
        pass


class PlayerServer(Runnable):

    def __init__(self, host: str):
        self.address = (host, Numbers.Port)
        self._process = None

    @property
    def delegate(self):
        # return 0
        return delegate

    @delegate.setter
    def delegate(self, value: PlayerServerDelegate):
        # pass
        global delegate
        delegate = value

    def run(self):
        self._process = Process(target=_run_app, args=(self.address,))
        self._process.start()

        print('\033[91m' 
              '* Running on http://%s:%d/ (Press CTRL+C to quit)'
              '\033[0m' % self.address)

    def stop(self):
        self._process.terminate()
        self._process.join()


@player_gui.route('/', methods=['GET', 'POST', 'DELETE', 'UPDATE'])
def home():

    # delegate = current_app.delegate

    if request.method == "GET":  # Players GUI
        return render_template('index.html', accounts=delegate.get_accounts())

    elif request.method == "POST":  # Add player
        name, legend = request.args['name'], request.args['legend'].upper()

        code = check_event(delegate, Events.Server.SetPlayer, [name, legend])
        if code:
            return make_response("", 400 + code)

        on_event(delegate, Events.Server.SetPlayer, [name, legend])

    elif request.method == "DELETE":  # Remove player
        name = request.args['name']
        if not check_event(delegate, Events.Server.DeletePlayer, [name]):
            return make_response("", 401)

        on_event(delegate, Events.Server.DeletePlayer, [name])

    elif request.method == "UPDATE":  # Update player account
        name, account = request.args['name'], request.args['account']

        code = check_event(delegate, Events.Server.SetAccount, [name, account])
        if code:
            return make_response("", 400 + code)

        on_event(delegate, Events.Server.SetAccount, [name, account])

    return make_response("", 200)


def _run_app(address: (str, int)):
    app = Flask(__name__)
    app.register_blueprint(player_gui)
    # app.delegate = SocketEmitter()
    # app.delegate.connect(4000)
    # app.delegate.wait_for_client()
    app.run(host=address[0], port=address[1], threaded=False)

