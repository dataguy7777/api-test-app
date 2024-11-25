import streamlit as st
import requests
from zeep import Client
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

# Define API URLs
REST_API_URL = "http://127.0.0.1:5000/api/item"
SOAP_API_URL = "http://127.0.0.1:8001/soap?wsdl"

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Secure API Testing Interface")
    st.markdown("""
    This application allows you to interact with the Flask REST and SOAP APIs.
    Please provide your credentials to authenticate and perform API operations.
    """)

    # Sidebar for Authentication
    st.sidebar.header("Authentication")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    # Create an auth object if credentials are provided
    auth = HTTPBasicAuth(username, password) if username and password else None

    st.header("REST API Operations")

    # GET All Items
    if st.button("GET All Items"):
        try:
            response = requests.get(REST_API_URL, auth=auth)
            if response.status_code == 200:
                st.success("Retrieved all items successfully!")
                st.json(response.json())
            elif response.status_code == 401:
                st.error("Unauthorized: Please check your credentials.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except RequestException as e:
            st.error(f"Request failed: {e}")

    # POST a New Item
    st.subheader("POST a New Item")
    post_data = st.text_area("Enter item data (JSON format)", '{"name": "New Item", "description": "Item description"}')
    if st.button("POST Item"):
        try:
            json_data = requests.utils.json.loads(post_data)
            response = requests.post(REST_API_URL, json=json_data, auth=auth)
            if response.status_code == 201:
                st.success("Item created successfully!")
                st.json(response.json())
            elif response.status_code == 400:
                st.error("Bad Request: Invalid JSON data.")
            elif response.status_code == 401:
                st.error("Unauthorized: Please check your credentials.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except ValueError:
            st.error("Invalid JSON format. Please correct the JSON data.")
        except RequestException as e:
            st.error(f"Request failed: {e}")

    # GET, PUT, DELETE an Item by ID
    st.subheader("GET, PUT, DELETE an Item by ID")
    item_id = st.number_input("Enter Item ID", min_value=1, step=1, format="%d")

    # GET Item
    if st.button("GET Item"):
        try:
            response = requests.get(f"{REST_API_URL}/{item_id}", auth=auth)
            if response.status_code == 200:
                st.success(f"Retrieved item with ID {item_id} successfully!")
                st.json(response.json())
            elif response.status_code == 404:
                st.error("Item not found.")
            elif response.status_code == 401:
                st.error("Unauthorized: Please check your credentials.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except RequestException as e:
            st.error(f"Request failed: {e}")

    # PUT (Update) Item
    new_data = st.text_area("Enter new data for PUT (JSON format)", '{"name": "Updated Item", "description": "Updated description"}')
    if st.button("PUT Item"):
        try:
            json_data = requests.utils.json.loads(new_data)
            response = requests.put(f"{REST_API_URL}/{item_id}", json=json_data, auth=auth)
            if response.status_code == 200:
                st.success(f"Item with ID {item_id} updated successfully!")
                st.json(response.json())
            elif response.status_code == 400:
                st.error("Bad Request: Invalid JSON data.")
            elif response.status_code == 404:
                st.error("Item not found.")
            elif response.status_code == 401:
                st.error("Unauthorized: Please check your credentials.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except ValueError:
            st.error("Invalid JSON format. Please correct the JSON data.")
        except RequestException as e:
            st.error(f"Request failed: {e}")

    # DELETE Item
    if st.button("DELETE Item"):
        try:
            response = requests.delete(f"{REST_API_URL}/{item_id}", auth=auth)
            if response.status_code == 200:
                st.success(f"Item with ID {item_id} deleted successfully!")
                st.json(response.json())
            elif response.status_code == 404:
                st.error("Item not found.")
            elif response.status_code == 401:
                st.error("Unauthorized: Please check your credentials.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except RequestException as e:
            st.error(f"Request failed: {e}")

    st.header("SOAP API Operations")

    # SOAP: Call say_hello
    if st.button("Call SOAP say_hello"):
        if not auth:
            st.error("Please provide username and password in the sidebar.")
        else:
            try:
                # Initialize a session with authentication
                session = requests.Session()
                session.auth = (username, password)
                transport = Transport(session=session)
                client = Client(SOAP_API_URL, transport=transport)

                # Call the SOAP method
                response = client.service.say_hello("Streamlit User")
                st.success("SOAP request successful!")
                st.write(f"Response from SOAP: {response}")
            except Exception as e:
                st.error(f"SOAP Error: {e}")


if __name__ == "__main__":
    main()
