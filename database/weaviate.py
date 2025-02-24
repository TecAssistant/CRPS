import weaviate
import os
from dotenv import load_dotenv
from weaviate.classes.query import MetadataQuery
from utils.encryption import encrypt_dictionary


def connect_database():
    load_dotenv()
    host = os.getenv("DATABASE_HOST", "localhost")
    port = int(os.getenv("DATABASE_PORT", 8090))
    grpc_port = int(os.getenv("DATABASE_GRPC_PORT", 50051))

    client = weaviate.connect_to_local(host, port, grpc_port)
    return client


def insert_into_collection(collection, vector, properties):
    client = connect_database()
    collection = client.collections.get(collection)
    # properties = encrypt_dictionary(properties)  # check this, we should change all properties types to string
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
            print(f"{key.capitalize()}: {value}")

        if distance is not None:
            confidence = (1 - distance) * 100
            print(f"Confidence: {confidence:.2f}%")

        print("-" * 40)

    client.close()
