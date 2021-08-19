# HTTP Reverse Proxy 
## _Docker Build_

## Prerequisites 

- Docker
- Docker-compose 
- SQL Database 
- Builds on [Insert link to different project]

## Enable IP forwarding

First make sure IP forwarding is set to 1 in `/proc/sys/net/ipv4/ip_forward`. You can check it with:

```sh
# cat /proc/sys/net/ipv4/ip_forward
1
```
Second enable IP forwarding in `/etc/sysctl.conf`. 

```
net.ipv4.ip_forward = 1
```

## Configure config.env

```
IP_HOST= # IP of the host you're redirecting to 
IP_PROXY= # IP of the machine that is running this docker-container

HONEY_ROOT=/http_proxy/Websites/
LOG_TYPE=Console
LOG_FILENAME=log.log
LOG_DB_HOST= # IP of the machine hosting the Database
LOG_DB_PORT= # Port where the Database is hosted
LOG_DB_NAME= # Name of the Database 
LOG_DB_USERNAME= #Username of the database user
LOG_DB_PASSWORD= #Password of the database user
```

If you are using this Proxy with the corresponding dashbaord docker-image, you can leave most of the variables as they are. 

## Build with docker-compose
To build the docker-image just navigate to the folder where the dockerfile lies and use the following command: 
```
sudo docker-compose build
```