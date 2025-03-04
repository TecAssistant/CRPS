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
from utils.encryption import encrypt_data, encrypt_dictionary, decrypt_dictionary

test_properties = {
    "identification": 8849382934,
    "name": "Juan Gonzales",
    "age": 23,
    "role": "Teacher",
    "phone_number": "+506 39292292",
    "registration_date": "2024-05-04T00:00:00Z",
    "last_update_date": "2025-010-04T00:00:00Z",
}
# print([generate_artificial_embedding(2048) for _ in range(10)])

test_vector = generate_artificial_embedding(2048)


def test_db():
    create_person_collection()
    # print_collection("Person")
    # newVec = preload_image("beast.json", "img/beast.jpg", "output/")
    # search_by_vector("Person", newVec, 2)
    # print_collection("Person")

    insert_into_collection("Person", test_vector, test_properties)

    print_collection("Person")
    search_by_vector("Person", test_vector, 1)


def test_encryption():
    encrypted_dictionary = encrypt_dictionary(test_properties)
    print(encrypted_dictionary)
    print("-" * 40)
    decrypted_dictionary = decrypt_dictionary(encrypted_dictionary)
    print(decrypted_dictionary)


def main():
    # test_db()
    # test_encryption()
    # client = connect_database()
    # client.collections.delete("Person")
    test_db()


if __name__ == "__main__":
    main()
