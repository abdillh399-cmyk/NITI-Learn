import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
db=SQLAlchemy(); login_manager=LoginManager(); migrate=Migrate()
def _database_url():
    url=os.environ.get("DATABASE_URL","").strip()
    if not url: return "sqlite:///peerlearn.db"
    return url.replace("postgres://","postgresql://",1) if url.startswith("postgres://") else url
def create_app():
    app=Flask(__name__)
    app.config["SECRET_KEY"]=os.environ.get("SECRET_KEY","dev-only-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"]=_database_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
    app.config["MAX_CONTENT_LENGTH"]=int(os.environ.get("MAX_UPLOAD_MB","500"))*1024*1024
    db.init_app(app); login_manager.init_app(app); migrate.init_app(app,db)
    login_manager.login_view="auth.login"; login_manager.login_message_category="info"
    import models
    from routes.auth import auth_bp
    from routes.videos import videos_bp
    from routes.main import main_bp
    app.register_blueprint(auth_bp); app.register_blueprint(videos_bp); app.register_blueprint(main_bp)
    @app.get("/health")
    def health(): return jsonify({"status":"ok"})
    with app.app_context(): db.create_all()
    return app
app=create_app()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT","5000")),debug=False)
