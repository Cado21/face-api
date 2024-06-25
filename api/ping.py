from flask_restful import Resource
from flasgger import swag_from

class Ping(Resource):
    @swag_from({
        'tags': ['Ping'],
        'responses': {
            '200': {
                'description': 'OK',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            '500': {
                'description': 'Something went wrong!',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def get(self):
        try:
            return {'message': 'OK' }, 200
        except Exception as e:
            print(e)
            return {'error': 'Something went wrong!'}, 500
