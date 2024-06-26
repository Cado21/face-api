from flask import Flask, Blueprint
from flask_restful import Api
from flasgger import Swagger
from api.add_dataset import AddDataset
from api.train import Train
from api.ping import Ping
from api.storage_data import StorageData

def create_app():
    app = Flask(__name__)
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    api.add_resource(Ping, '/ping')
    api.add_resource(AddDataset, '/add-dataset')
    api.add_resource(Train, '/train')
    api.add_resource(StorageData, '/storage-data')

    template = {
        "swagger": "2.0",
        "info": {
            "title": "Face API",
            "description": "Please works! if not hehe goodluck!",
            "version": "1.0"
        },
        "basePath": "/api",
        "schemes": [
            "http",
            "https"
        ]
    }
    Swagger(app, template=template)

    return app
