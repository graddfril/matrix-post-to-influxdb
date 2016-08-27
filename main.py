import defopt
from matrix_client.client import MatrixClient, Room


def main(access_token: str, room_id: str, hs: str='https://matrix.org'):
    """Listen for events happening in a Matrix room."""
    client = MatrixClient(hs, token=access_token)

    my_room = list(filter(lambda x: x[0] == room_id, client.get_rooms().items()))[0][1]
    my_room.add_listener(lambda x: print(x))

    client.listen_forever()


if __name__ == '__main__':
    defopt.run(main)
