from weaviate.classes.config import Property, DataType


# Note that you can use `client.collections.create_from_dict()` to create a collection from a v3-client-style JSON object
"""
collectionent.collections.create(
    "Article",
    properties=[
        Property(name="title", data_type=DataType.TEXT),
        Property(name="body", data_type=DataType.TEXT),
    ]
)
"""
