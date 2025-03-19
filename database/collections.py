from database.weaviate import connect_database
from weaviate.classes.config import Property, DataType, Configure, VectorDistances


def create_person_collection():
    client = connect_database()
    client.collections.create(
        "Person",
        vector_index_config=Configure.VectorIndex.hnsw(distance_metric=VectorDistances.L2_SQUARED),
        properties=[
            Property(name="identification", data_type=DataType.TEXT),
            Property(name="name", data_type=DataType.TEXT),
            Property(name="age", data_type=DataType.TEXT),
            Property(name="role", data_type=DataType.TEXT),
            Property(name="phone_number", data_type=DataType.TEXT),
            Property(name="registration_date", data_type=DataType.TEXT),
            Property(name="last_update_date", data_type=DataType.TEXT),
        ],
    )
    client.close()
