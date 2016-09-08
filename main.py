from collections import defaultdict
import defopt
from matrix_client.client import MatrixClient, Room
from influxdb import InfluxDBClient


def transform_matrix_to_influxdb(matrix_event: dict):
    result = defaultdict(dict)

    result['tags']['sender'] = matrix_event['sender']

    m_e_content = matrix_event['content']

    m_e_content.pop('body') # don't care about body
    result['measurement'] = m_e_content.pop('msgtype')
    result['time'] = int(m_e_content.pop('timestamp'))
    result['fields'] = m_e_content # all things left

    return result


def main(access_token: str, room_id: str, influx_dsn: str, hs: str='https://matrix.org'):
    """Listen for events happening in a Matrix room."""
    matrix = MatrixClient(hs, token=access_token)
    influxdb = InfluxDBClient.from_DSN(influx_dsn)

    my_room = list(filter(lambda x: x[0] == room_id, matrix.get_rooms().items()))[0][1]

    my_room.add_listener(lambda x: print(x))
    my_room.add_listener(lambda x: influxdb.write_points([transform_matrix_to_influxdb(x)], time_precision='ms'))

    matrix.listen_forever()


if __name__ == '__main__':
    defopt.run(main)
