import folder_search

websites_path = "/home/osboxes/PycharmProjects/Proxy/Websites/"
server_IP = "192.168.56.102"
proxy_IP = "192.168.56.101"
page_list = folder_search.file_names(websites_path)

sql_server_ip = "192.168.56.1"
sql_database = "Proxy_Log"
sql_user = "postgres"
sql_password = "pass"