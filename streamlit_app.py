from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from threading import Thread
from wsgiref.simple_server import make_server

# Initialize Flask application
app = Flask(__name__)

# Initialize HTTP Basic Authentication
auth = HTTPBasicAuth()

# In-memory user store with hashed passwords for demonstration purposes
users = {
    "admin": generate_password_hash("secret"),
    "user": generate_password_hash("password")
}

# In-memory data store to hold items
data_store = {}


@auth.verify_password
def verify_password(username, password):
    """
    Verify the provided username and password against the user store.
    """
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None


@app.route('/api/item', methods=['GET', 'POST'])
@auth.login_required
def handle_items():
    """
    Handle operations for all items.
    """
    if request.method == 'GET':
        return jsonify(data_store), 200
    elif request.method == 'POST':
        item = request.get_json()
        if not item:
            return jsonify({"error": "Invalid JSON data"}), 400
        item_id = len(data_store) + 1
        data_store[item_id] = item
        return jsonify({"id": item_id, "item": item}), 201


@app.route('/api/item/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def handle_item(item_id):
    """
    Handle operations for a specific item identified by item_id.
    """
    if item_id not in data_store:
        return jsonify({"error": "Item not found"}), 404

    if request.method == 'GET':
        return jsonify({item_id: data_store[item_id]}), 200
    elif request.method == 'PUT':
        updated_item = request.get_json()
        if not updated_item:
            return jsonify({"error": "Invalid JSON data"}), 400
        data_store[item_id] = updated_item
        return jsonify({"id": item_id, "item": updated_item}), 200
    elif request.method == 'DELETE':
        del data_store[item_id]
        return jsonify({"message": "Item deleted"}), 200


class HelloWorldService(ServiceBase):
    """
    SOAP Service offering a simple 'say_hello' method.
    """

    @rpc(Unicode, _returns=Unicode)
    def say_hello(ctx, name):
        """
        Return a greeting message to the provided name.
        """
        return f"Hello, {name}! From user authenticated via SOAP."


# Initialize SOAP application using Spyne
soap_app = Application(
    [HelloWorldService],
    tns='spyne.examples.hello',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

soap_wsgi_app = WsgiApplication(soap_app)


def run_soap():
    """
    Run the SOAP server on a separate thread with authentication.
    """
    # Initialize a separate Flask app for SOAP to incorporate authentication
    soap_flask_app = Flask('soap_app')
    soap_auth = HTTPBasicAuth()

    # Reuse the same user store for SOAP authentication
    @soap_auth.verify_password
    def verify_soap_password(username, password):
        """
        Verify credentials for SOAP service.
        """
        if username in users and check_password_hash(users.get(username), password):
            return username
        return None

    @soap_flask_app.route('/soap', methods=['POST'])
    @soap_auth.login_required
    def soap_endpoint():
        """
        Handle SOAP requests with authentication.
        """
        return soap_wsgi_app(request.environ, start_response)

    def start_response(status, headers):
        """
        Minimal start_response function required by WSGI.
        """
        pass

    # Start the SOAP server
    server = make_server('0.0.0.0', 8001, soap_flask_app)
    print("SOAP server with authentication running on http://0.0.0.0:8001/soap")
    server.serve_forever()


# Start the SOAP server in a separate daemon thread
soap_thread = Thread(target=run_soap)
soap_thread.daemon = True
soap_thread.start()

if __name__ == '__main__':
    # Start the Flask REST API server
    app.run(port=5000, debug=True)
