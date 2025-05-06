import os
from backend import create_app, db

def get_env():
    return os.environ.get('FLASK_ENV', 'development')

def get_debug(env):
    return env == 'development'

if __name__ == '__main__':
    env = get_env()
    app = create_app()
    app.config['ENV'] = env
    app.config['DEBUG'] = get_debug(env)
    with app.app_context():
        db.create_all()
    app.run(debug=app.config['DEBUG']) 