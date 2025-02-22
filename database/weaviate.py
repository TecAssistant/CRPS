import weaviate.classes as wvc


def connect_to_client(port):
    client = weaviate.connect_to_local("localhost", 8090, 50051)
    client.is_ready()


def vector_query():
    pass


def main():
    human_path = "img/human-face.jpeg"
    path2 = "img/Selfie.png"
    port = 8090
    connect_to_client(port)

    # dest = "output"
    # # image = Image.open(path)
    # image.show()
    # preload_image("human-face.json", human_path, dest)
