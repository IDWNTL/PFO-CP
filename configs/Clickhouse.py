import clickhouse_connect

from configs.Environment import get_environment_variables

env = get_environment_variables()

client = clickhouse_connect.get_client(
    host=env.CLICKHOUSE_HOST, port=env.CLICKHOUSE_PORT, database=env.CLICKHOUSE_DATABASE
)
