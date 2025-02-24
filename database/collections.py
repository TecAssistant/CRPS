from database.weaviate import connect_database
from weaviate.classes.config import Property, DataType


def create_person_collection():
    client = connect_database()
    client.collections.create(
        "Person",
        properties=[
            Property(name="identification", data_type=DataType.INT),
            Property(name="name", data_type=DataType.TEXT),
            Property(name="age", data_type=DataType.INT),
            Property(name="role", data_type=DataType.TEXT),
            Property(name="phone_number", data_type=DataType.TEXT),
            Property(name="registration_date", data_type=DataType.DATE),
            Property(name="last_update_date", data_type=DataType.DATE),
        ],
    )
    client.close()
