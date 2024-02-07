import json
from authlib.integrations.flask_client import OAuth
from flask import Flask, abort, redirect, render_template, session, url_for
from config import OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET, FLASK_SECRET


app = Flask(__name__)

appConf = {
    "OAUTH2_CLIENT_ID":  OAUTH2_CLIENT_ID,
    "OAUTH2_CLIENT_SECRET": OAUTH2_CLIENT_SECRET,
    "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
    "FLASK_SECRET": FLASK_SECRET,
    "FLASK_PORT": 5000
}

app.secret_key = appConf.get("FLASK_SECRET")

oauth = OAuth(app)
oauth.register(
    "myApp",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'{appConf.get("OAUTH2_META_URL")}',
)


@app.route("/")
def home():
    try:
        user_data = session.get("user", {})
        pretty_user_data = json.dumps(user_data, indent=4)
        return render_template("home.html", session=user_data, pretty=pretty_user_data)
    except Exception as e:
        # Handle specific exceptions or log the general exception
        print(f"Error in home route: {e}")
        return "An error occurred."


@app.route("/signin-google")
def googleCallback():
    try:
        token = oauth.myApp.authorize_access_token()
        session["user"] = token
        return redirect(url_for("home"))
    except Exception as e:
        # Handle specific exceptions or log the general exception
        print(f"Error in googleCallback route: {e}")
        return "An error occurred."


@app.route("/google-login")
def googleLogin():
    try:
        session.clear()
        if "user" in session:
            abort(404)
        return oauth.myApp.authorize_redirect(redirect_uri=url_for("googleCallback", _external=True), prompt="login")
    except Exception as e:
        # Handle specific exceptions or log the general exception
        print(f"Error in googleLogin route: {e}")
        return "An error occurred."


@app.route("/logout")
def logout():
    try:
        session.pop("user", None)
        return redirect(url_for("home"))
    except Exception as e:
        # Handle specific exceptions or log the general exception
        print(f"Error in logout route: {e}")
        return "An error occurred."


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=appConf.get("FLASK_PORT"), debug=True)
    except Exception as e:
        # Handle specific exceptions or log the general exception
        print(f"Error in app run: {e}")
