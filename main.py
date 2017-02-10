from os import environ
from collections import defaultdict, namedtuple
import defopt
from matrix_client.client import MatrixClient, Room
from influxdb import InfluxDBClient


MatrixConfig = namedtuple('MatrixConfig', ['hs', 'user_id', 'access_token', 'room_id'])


def transform_matrix_to_influxdb(matrix_event: dict):
    result = defaultdict(dict)

    result['tags']['sender'] = matrix_event['sender']

    m_e_content = matrix_event['content']

    m_e_content.pop('body') # don't care about body
    result['measurement'] = m_e_content.pop('msgtype')
    result['time'] = int(m_e_content.pop('timestamp'))
    result['fields'] = m_e_content # all things left

    return result


def main(matrix_c: MatrixConfig, influx_dsn: str):
    """Listen for events happening in a Matrix room."""
    matrix = MatrixClient(matrix_c.hs, token=matrix_c.access_token)
    influxdb = InfluxDBClient.from_DSN(influx_dsn)

    influxdb.create_database(influxdb._database)

    my_room = matrix.join_room(matrix_c.room_id)

    my_room.add_listener(lambda x: print(x))
    my_room.add_listener(lambda x: influxdb.write_points([transform_matrix_to_influxdb(x)], time_precision='ms'))

    matrix.listen_forever()


def cli(user_id: str, access_token: str, room_id: str, influx_dsn: str, hs: str='https://matrix.org'):
    main(MatrixConfig(hs, user_id, access_token, room_id),
         influx_dsn)


def from_env():
    main(MatrixConfig(environ['MATRIX_HOMESERVER'],
                      environ['MATRIX_USER_ID'],
                      environ['MATRIX_ACCESS_TOKEN'],
                      environ['MATRIX_ROOM_ID']),
                      environ['INFLUXDB_DSN'])


if __name__ == '__main__':
    try:
        from_env()
    # some env variable were not defined
    except KeyError:
        # fall back to cli
        defopt.run(cli)
