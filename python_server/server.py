import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Type
import psycopg2
import os
import time

DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_NAME = os.environ.get('DB_NAME', 'mydb')
DB_USER = os.environ.get('DB_USER', 'dbuser')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'dbpassword')

def connect_to_db():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Połączono z bazą danych")
            return conn
        except psycopg2.OperationalError:
            print("Błąd połączenia z bazą danych, ponawianie za 5 sekund...")
            time.sleep(5)

conn = connect_to_db()
cursor = conn.cursor()

# Define the request handler class by extending BaseHTTPRequestHandler.
# This class will handle HTTP requests that the server receives.
class SimpleRequestHandler(BaseHTTPRequestHandler):
    # Handle OPTIONS requests (used in CORS preflight checks).
    # CORS (Cross-Origin Resource Sharing) is a mechanism that allows restricted resources
    # on a web page to be requested from another domain outside the domain from which the resource originated.
    def do_OPTIONS(self):
        # Send a 200 OK response to acknowledge the request was processed successfully.
        self.send_response(200, "OK")

        # Set headers to indicate that this server allows any origin (*) to access its resources.
        # This is important for browsers when making cross-origin requests.
        self.send_header("Access-Control-Allow-Origin", "*")

        # Specify the allowed HTTP methods that can be used in the actual request.
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")

        # Indicate what request headers are allowed (e.g., Content-Type for JSON requests).
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        # End headers and complete the response
        self.end_headers()

    # Handle GET requests.
    # When the client sends a GET request, this method will be called.
    def do_GET(self) -> None:
        # Set the HTTP response status to 200 OK, which means the request was successful.
        self.send_response(200)

        # Set the Content-Type header to application/json, meaning the response will be in JSON format.
        self.send_header('Content-type', 'application/json')

        # Allow any domain to make requests to this server (CORS header).
        self.send_header('Access-Control-Allow-Origin', '*')

        # Finish sending headers
        self.end_headers()

        self.user_list = self.get_users()
        # Prepare the response data, which will be returned in JSON format.
        # The response contains a simple message and the path of the request.
        response: dict = {
            "message": "User list",
            "user_list": self.user_list
        }
        # Convert the response dictionary to a JSON string and send it back to the client.
        # `self.wfile.write()` is used to send the response body.
        self.wfile.write(json.dumps(response).encode())

    def get_users(self):
        try:
            cursor.execute("SELECT id,first_name,last_name,role FROM users")
            rows = cursor.fetchall()

            users = [{
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "role": row[3]
            } for row in rows]
            return users

        except Exception as e:
            print("Error:", e)
            return []
    # Handle POST requests.
    # This method is called when the client sends a POST request.
    def do_POST(self) -> None:
        # Retrieve the content length from the request headers.
        # This tells us how much data to read from the request body.
        content_length: int = int(self.headers['Content-Length'])

        # Read the request body based on the content length.
        post_data: bytes = self.rfile.read(content_length)

        # Decode the received byte data and parse it as JSON.
        # We expect the POST request body to contain JSON-formatted data.
        received_data: dict = json.loads(post_data.decode())
        SimpleRequestHandler.pomId += 1
        new_user = received_data
        new_user['id'] = SimpleRequestHandler.pomId
        self.user_list.append(received_data)
        # Prepare the response data.
        # It includes a message indicating it's a POST request and the data we received from the client.
        response: dict = {
            "message": "Item added",
            "user_list": self.user_list 
        }

        # Send the response headers.
        # Set the status to 200 OK and indicate the response content will be in JSON format.
        self.send_response(200)
        self.send_header('Content-type', 'application/json')

        # Again, allow any origin to access this resource (CORS header).
        self.send_header('Access-Control-Allow-Origin', '*')

        # Finish sending headers.
        self.end_headers()

        # Convert the response dictionary to a JSON string and send it back to the client.
        self.wfile.write(json.dumps(response).encode())

    def do_DELETE(self) -> None:
        content_length: int = int(self.headers['Content-Length'])
        delete_data: bytes = self.rfile.read(content_length)
        received_data: dict = json.loads(delete_data.decode())         

        user_id = received_data.get('id')

        SimpleRequestHandler.user_list = [user for user in self.user_list if user['id'] != user_id]

        response: dict = {
            "message": "Item deleted",
            "user_list": self.user_list
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow all origins (CORS).
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())  # Send updated user list as JSON.

# Function to start the server.
# It takes parameters to specify the server class, handler class, and port number.
def run(
        server_class: Type[HTTPServer] = HTTPServer,
        handler_class: Type[BaseHTTPRequestHandler] = SimpleRequestHandler,
        port: int = 8000
) -> None:
    # Define the server address.
    # '' means it will bind to all available network interfaces on the machine, and the port is specified.
    server_address: tuple = ('', port)

    # Create an instance of HTTPServer with the specified server address and request handler.
    httpd: HTTPServer = server_class(server_address, handler_class)

    # Print a message to the console indicating that the server is starting and which port it will listen on.
    print(f"Starting HTTP server on port {port}...")

    # Start the server and make it continuously listen for requests.
    # This method will block the program and keep running until interrupted.
    httpd.serve_forever()


# If this script is executed directly (not imported as a module), this block runs.
# It calls the `run()` function to start the server.
if __name__ == '__main__':
    run()