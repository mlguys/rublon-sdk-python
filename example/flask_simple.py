from flask import Flask, request, redirect, session
app = Flask(__name__)

from rublon import Rublon2Factor, Rublon2FactorCallback, Rublon2FactorGUI


class Rublon2FactorCallbackFlask(Rublon2FactorCallback):
    def get_raw_request_body(self):
        return request.get_data()

    def get_state(self):
        return request.args.get(self.PARAMETER_STATE)

    def get_access_token(self):
        return request.args.get(self.PARAMETER_ACCESS_TOKEN)


RUBLON_SYSTEM_TOKEN = 'your_system_token'
RUBLON_SECRET_KEY = 'your_secret_key'
USER_PASSWORD = 'rublon123'


@app.route("/")
def hello():
    if 'user_id' in session:
        rublon = Rublon2Factor(RUBLON_SYSTEM_TOKEN, RUBLON_SECRET_KEY)
        return """You are logged in. {0} <a href="/logout">Logout</a>""".format(
            Rublon2FactorGUI(rublon, user_id=session['user_id'], user_email=session['user_id'])
        )
    else:
        return """<form method="POST" action="/auth">
    <input name="email" type="email">
    <input type="password" name="pass">
    <input type="submit">
</form>"""


@app.route("/logout")
def logout():
    del session['user_id']
    return redirect(request.url_root)


@app.route("/rublon_callback")
def rublon_callback():
    rublon = Rublon2Factor(RUBLON_SYSTEM_TOKEN, RUBLON_SECRET_KEY)
    callback = Rublon2FactorCallbackFlask(rublon)
    callback.call(success_handler=rublon_user_logged_in_callback,
                  cancel_handler=rublon_cancel_callback)
    # redirect to main page
    return redirect(request.url_root)


def rublon_user_logged_in_callback(user_id, callback):
    session['user_id'] = user_id


def rublon_cancel_callback(callback):
    raise Exception('Request cancelled')


@app.route("/auth", methods=['POST'])
def auth():
    user_email = request.form['email']
    password = request.form['pass']

    if password == USER_PASSWORD:
        # internal auth ok
        callback_url = request.url_root + 'rublon_callback'
        user_id = user_email
        extra_params = {}

        rublon = Rublon2Factor(RUBLON_SYSTEM_TOKEN, RUBLON_SECRET_KEY)
        url = rublon.auth(callback_url, user_id, user_email, extra_params)

        if not url:
            return 'User is not protected with Rublon'

        return redirect(url)
    else:
        return 'Invalid credentials'


if __name__ == "__main__":
    app.secret_key = 'secretkey'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)