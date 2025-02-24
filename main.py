import weaviate, os
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import MetadataQuery
from utils.embeddings import preload_image, generate_artificial_embedding
from database.weaviate import (
    connect_database,
    insert_into_collection,
    print_collection,
    search_by_vector,
)
from database.collections import create_person_collection


def test():
    # create_person_collection()
    # print_collection("Person")
    # newVec = preload_image("beast.json", "img/beast.jpg", "output/")
    # search_by_vector("Person", newVec, 2)
    # print_collection("Person")

    test_properties = {
        "identification": 122223,
        "name": "Maria Gonzales",
        "age": 23,
        "role": "Teacher",
        "phone_number": "+506 7777777",
        "registration_date": "2023-07-03T00:00:00Z",
        "last_update_date": "2025-07-03T00:00:00Z",
    }

    test_vector = generate_artificial_embedding(2048)
    insert_into_collection("Person", test_vector, test_properties)

    # print_collection("Person")
    # search_by_vector("Person", test_vector, 3)


def main():
    test()
    print_collection("Person")


if __name__ == "__main__":
    main()
