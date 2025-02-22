import weaviate, os
from weaviate.classes.config import Property, DataType


client = weaviate.connect_to_local("localhost", 8080, 50051)

client.collections.create(
    "Person",
    properties=[
        Property(name="identification", data_type=DataType.INT),
        Property(name="name", data_type=DataType.TEXT),
        Property(name="age", data_type=DataType.INT),
        Property(name="role", data_type=DataType.TEXT),
        Property(name="phone_number", data_type=DataType.PHONE_NUMBER),
        Property(name="registration_date", data_type=DataType.DATE),
        Property(name="last_update_date", data_type=DataType.DATE),
    ],
)
