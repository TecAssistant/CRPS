import weaviate
import os
from dotenv import load_dotenv
from weaviate.classes.query import MetadataQuery
from weaviate.classes.init import Auth
from utils.encryption import encrypt_dictionary, decrypt_data

def connect_database():
    client = connect_remote_database()
    # client = connect_local_database()
    return client


def connect_remote_database():
    load_dotenv()
    url = os.getenv("WEAVIATE_URL", "")
    api_key = os.getenv("WEAVIATE_API_KEY", "")

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=url,
        auth_credentials=Auth.api_key(api_key),
    )

    return client

def connect_local_database():
    load_dotenv()
    host = os.getenv("DATABASE_HOST", "localhost")
    port = int(os.getenv("DATABASE_PORT", 8090))
    grpc_port = int(os.getenv("DATABASE_GRPC_PORT", 50051))

    client = weaviate.connect_to_local(host, port, grpc_port)
    return client


def insert_into_collection(collection, vector, properties):
    client = connect_database()
    collection = client.collections.get(collection)
    properties = encrypt_dictionary(properties)
    collection.data.insert(
        properties=properties,
        vector=vector,
    )
    client.close()


def print_collection(collection):
    client = connect_database()
    collection = client.collections.get(collection)
    for item in collection.iterator(include_vector=True):
        print(
            item.uuid,
            item.properties,
            # item.vector
        )
    client.close()


def search_by_vector(collection, vector, limit):
    client = connect_database()
    collection = client.collections.get(collection)
    response = collection.query.near_vector(
        near_vector=vector,
        limit=limit,
        return_metadata=MetadataQuery(distance=True),
    )

    print("-" * 40)
    for o in response.objects:
        properties = o.properties
        distance = o.metadata.distance

        for key, value in properties.items():
            decrypted_value = value
            if value is not None:
                decrypted_value = decrypt_data(value)
            print(f"{key.capitalize()}: {decrypted_value}")

        if distance is not None:
            confidence = (1 - distance) * 100
            print(f"Confidence: {confidence:.2f}%")

        print("-" * 40)

    client.close()
