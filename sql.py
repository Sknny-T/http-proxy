import psycopg2


def connect():
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(
        host="192.168.56.1",
        database="Proxy_Log",
        user="postgres",
        password="pass")

    cur = conn.cursor()

    cur.execute('SELECT * from Proxy_Log')

    results = cur.fetchall()
    for result in results:
        print(result)


def insert_proxy_log(packet_info, destination, packet_type, module):
    cur.execute("insert into Proxy_Log(packet_info) Values('"
                + packet_info + "'" + "'" + destination + "'" + packet_type + "'" + module + "')")
    conn.commit()


if __name__ == '__main__':
    print("_________________________START______________________")
    connect()
    print("____________________________________________________")

# cur.close()
# conn.close()
# print('Database connection closed.')