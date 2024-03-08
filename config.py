from flask_sqlalchemy import SQLAlchemy
import yaml

def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()

#contient la configuration de l'app, et peut lire des paramètres depuis config.yaml ou db.yaml

