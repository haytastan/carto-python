import os
import pytest
import time

from carto.exceptions import CartoException
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient


SETUP_QUERIES = [
    'DROP TABLE IF EXISTS carto_python_sdk_copy_test',
    """
    CREATE TABLE carto_python_sdk_copy_test (
      the_geom geometry(Geometry,4326),
      name text,
      age integer
    )
    """,
    "SELECT CDB_CartodbfyTable(current_schema, 'carto_python_sdk_copy_test')"
]
BATCH_TERMINAL_STATES = ['done', 'failed', 'cancelled', 'unknown']

# Please note the newline characters to delimit rows
TABLE_CONTENTS=[
    b'the_geom,name,age\n',
    b'SRID=4326;POINT(-126 54),North West,89\n',
    b'SRID=4326;POINT(-96 34),South East,99\n',
    b'SRID=4326;POINT(-6 -25),Souther Easter,124\n'
]


@pytest.fixture(scope="module")
def test_table(api_key_auth_client_usr):
    batch_client = BatchSQLClient(api_key_auth_client_usr)
    job = batch_client.create(SETUP_QUERIES)
    while not job['status'] in BATCH_TERMINAL_STATES:
        time.sleep(1)
        job = batch_client.read(job['job_id'])
    assert job['status'] == 'done'


def test_copyfrom(api_key_auth_client_usr):
    copy_client = CopySQLClient(api_key_auth_client_usr)

    query = 'COPY carto_python_sdk_copy_test (the_geom, name, age) FROM stdin WITH (FORMAT csv, HEADER true)'
    data = iter(TABLE_CONTENTS)
    result = copy_client.copyfrom(query, data)

    assert result['total_rows'] == 3
