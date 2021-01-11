from flask import *

from routes import main


def create_app(config_file="settings.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    app.register_blueprint(main)
    return app


if __name__ == "__main__":
    app = create_app(config_file="settings.py")
    app.run(debug=True)
