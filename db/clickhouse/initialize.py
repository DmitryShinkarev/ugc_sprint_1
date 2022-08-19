import logging
import time
from clickhouse_driver import Client
from clickhouse_driver.errors import Error


logging.basicConfig(format='[%(asctime)s]\t[%(levelname)s]\t%(message)s', level=logging.INFO)


# connect to db
def connection() -> Client:
    while True:
        try:
            client = Client('clickhouse-node1')
            return client
        except Error as e:
            logging.error(e)
            logging.info("still trying to connect...")
            time.sleep(1)


# initialize cluster
def init_cluster(client: Client):
    client.execute("CREATE DATABASE analysis ON CLUSTER 'company_cluster';")
    client.execute(
        """
        CREATE TABLE
            analysis.data_analysis
        ON CLUSTER 'company_cluster' AS analysis.data_analysis
        ENGINE = Distributed('company_cluster', analysis, data_analysis_repl, rand());
        """
    )


if __name__ == '__main__':
    logging.info('Connect')
    client = connection()
    logging.info('Init cluster')
    init_cluster(client)
    logging.info('Success')
