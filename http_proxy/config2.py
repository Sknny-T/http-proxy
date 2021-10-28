import folder_search
import os

websites_path = "/http_proxy/Websites/"
server_IP = "192.168.56.102"
proxy_IP = "192.168.56.106"
page_list = folder_search.file_names(websites_path)

sql_server_ip = "172.19.0.1"
sql_server_port = "5432"
sql_database = "Proxy_Log"
sql_user = "postgres"
sql_password = "pass"
test_config = "This is a test to see if config gets read right" 
