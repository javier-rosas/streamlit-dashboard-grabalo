# pylint: disable=W0718

"""
Helpers for the Grabalo Concurrency Dashboard
"""

import os

import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import (  # More specific MongoDB errors
    ConnectionFailure,
    OperationFailure,
)

# Load environment variables from .env file
load_dotenv()


def get_active_keys():
    """Fetch the number of active Deepgram API keys."""
    deepgram_project_id = os.getenv("DEEPGRAM_PROJECT_ID")
    deepgram_api_key = os.getenv("DEEPGRAM_CREATE_AND_DELETE_KEYS_KEY")
    deepgram_base_url = "https://api.deepgram.com/v1"
    deepgram_keys_endpoint = f"{deepgram_base_url}/projects/{deepgram_project_id}/keys"

    if not deepgram_project_id or not deepgram_api_key:
        return "Error: Deepgram ENV VARS not set"

    try:
        response = requests.get(
            f"{deepgram_keys_endpoint}?status=active",
            headers={"Authorization": f"Token {deepgram_api_key}"},
            timeout=10,
        )
        response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # Assuming the -3 logic is specific and correct for your use case
        return len(data.get("api_keys", [])) - 3
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP Error: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request Error: {req_err}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_active_meeting_count():
    """
    Counts the number of currently active meetings from MongoDB,
    based on an 'isRecording': True field.
    """
    mongodb_uri = os.getenv("MONGODB_URI")
    # You might want to make these configurable via .env as well
    database_name = os.getenv(
        "MONGODB_DATABASE_NAME", "your_app_database"
    )  # Default if not in .env
    collection_name = os.getenv(
        "MONGODB_MEETINGS_COLLECTION", "meetings"
    )  # Default if not in .env

    if not mongodb_uri:
        return "Error: MONGODB_URI not set"
    if not database_name:  # Or handle default more explicitly if needed
        return "Error: MONGODB_DATABASE_NAME not set and no default"
    if not collection_name:
        return "Error: MONGODB_MEETINGS_COLLECTION not set and no default"

    client = None  # Initialize client to None for finally block
    try:
        client = MongoClient(
            mongodb_uri, serverSelectionTimeoutMS=5000
        )  # Added timeout
        # The ismaster command is cheap and does not require auth.
        client.admin.command("ismaster")  # Verify connection
        db = client[database_name]
        meetings_collection = db[collection_name]

        # A meeting is considered active if its 'isRecording' field is true.
        active_meetings_query = {"isRecording": True}
        active_count = meetings_collection.count_documents(active_meetings_query)
        return active_count
    except ConnectionFailure:
        return "Error: MongoDB connection failed"
    except OperationFailure as op_err:
        return f"MongoDB Op Error: {op_err}"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if client:
            client.close()
