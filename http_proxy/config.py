import folder_search
import os

websites_path = os.environ['HONEY_ROOT']
server_IP = os.environ['IP_HOST']
proxy_IP = os.environ['IP_PROXY']
page_list = folder_search.file_names(websites_path)

sql_server_ip = os.environ['LOG_DB_HOST']
sql_server_port = os.environ['LOG_DB_PORT']
sql_database = os.environ['LOG_DB_NAME']
sql_user = os.environ['LOG_DB_USERNAME']
sql_password = os.environ['LOG_DB_PASSWORD']
