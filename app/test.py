from flask import Flask, Blueprint, request, send_file
from flask_restx import Api, Namespace, Resource, fields
from io import BytesIO

import os, qrcode

# Create Flask app
app = Flask(__name__)

# Associate Api with Blueprint
api_blueprint = Blueprint('API', __name__)
api = Api(api_blueprint,
          title='Api for QR code app',
          version='1.0',
          description='This is an API for QR code app',
          # All API metadatas
          )

# Create namespace for containing Qr Code related operations
qrcode_namespace = Namespace('QrCode', description='Qr code related operations')
# Specify uri of qrcode namespace as /qrcode
api.add_namespace(qrcode_namespace, path='/qrcode')
# Specify uri of api blueprint as /api
app.register_blueprint(api_blueprint, url_prefix='/api')

# Define input model
qrcode_creation_input = qrcode_namespace.model('QRCode creation Input', {
    'value': fields.String(required=True, description='The value that is supposed to be encoded into qrcode'),
})


# Define API endpoint for creating Qr Code image
@qrcode_namespace.route('/')
@qrcode_namespace.doc('Creates a QRCode image based on a string value.')
class QrCodeRoot(Resource):
    @qrcode_namespace.expect(qrcode_creation_input)
    @qrcode_namespace.produces(['image/png'])
    @qrcode_namespace.response(200, description='Return QR Code png image file.')
    @qrcode_namespace.response(400, description='Invalid input provided.')
    def post(self):
        # Get value to encode into QR Code
        json_input = request.get_json()
        value_to_turn_into_qrcode = json_input['value']

        # Create qr code image and return it as HTTP response
        pil_img = qrcode.make(value_to_turn_into_qrcode)
        img_io = BytesIO()
        pil_img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    port = int(os.getenv("PORT", "5678"))
    app.run(host='0.0.0.0', port=port)
