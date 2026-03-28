import firebase_admin
from firebase_admin import credentials
from flask import Flask
from flask_cors import CORS
from config import Config


def create_app(config_object=None):
    app = Flask(__name__)
    cfg = config_object or Config
    app.config.from_object(cfg)

    CORS(app, origins=[cfg.FRONTEND_URL], supports_credentials=True)

    if not cfg.TESTING and cfg.FIREBASE_SERVICE_ACCOUNT:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cfg.FIREBASE_SERVICE_ACCOUNT)
            firebase_admin.initialize_app(cred)

    from auth.routes import auth_bp
    from generation.routes import generation_bp
    from planeaciones.routes import planeaciones_bp
    from billing.routes import billing_bp
    from admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(generation_bp)
    app.register_blueprint(planeaciones_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(admin_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(port=5000, debug=True)
