<h1> HTTP Reverse Proxy Honeypot </h1> 


Table of Contents


[TOC]

# Overview

The idea behind this work was to create a plug and play solution for deploying a honeypot on an HTTP level on a reverse proxy server in order to increase security on a web server. The 
honeypot should be able to create decoy web pages, or manipulate existing web pages, to deceive any attacker. All made possible by intercepting the whole TCP traffic coming from and to 
the web sever. By deploying the honeypot on the reverse proxy server, the problem of interfering with the system structure is avoided. The system itself is never touched and therefore the 
deployment will be much easier. The goal was to modify and inject HTTP packages, coming from the server to the client, on the proxy.
There are three different funcionalities of the proxy, which are all made possi- ble by the same technical components. These functionalities enable an analysation and manipulation of TCP 
packets.

# Functionality 

## Injection of a Honeyfile 

This functionality allows the injection of a honeyfile via the HTTP communication. The reverse proxy containing the honeypot forwards all traffic from the client to the server, while also analysing every packet coming through. The image below shows the communication diagram 
between server, proxy and client. If the client request a file, the proxy will forward the request to the  server. The response from the server gets then gets sent to the proxy and the proxy 
sends that file to the client. If the file is present on the server, the client will get a valid response. If the  client requests a file, which is not present on the server, he will then receive a 
"404 file not found" error. The image below shows the communication diagram, where the client requests a file, which  is not present on the server but is in fact a honeyfile. In step 4, the client 
request a file, in this example login.php, and the proxy forwards this request to the server. Since the file is not  present on the server, the response is a "404 file not found" error in step 6. 
Instead of forwarding the packet containing the 404 error, the proxy will drop the packet and acknowledge it  towards the server, so the server will not resend the packet. This is shown in 
Step 6 and 6.1. Next, the proxy will then forge a new packet containing the honeyfile, which matches the  request, and will send it to the client. The client will receive a valid response 
containing a file, which matches his request. Hereby, the deception of a real website is created. The client will see the response and will assume that the website is in fact a real response.


|  ![](readme_imgs/Modified%20Traffic.png)|
|:---:|
| Communication between client, proxy and host  |



### Example Injection

The following picture shows the response of the host (192.168.56.102) for the requested file /login.php. Because the file is not present on the host the client recieves a 404 not found response. 

| ![](readme_imgs/login_host_404.png)|
|:---:|
|  Response for the request of the /login.php file from the host |

</br>
</br>

With the reverse proxy honeypot (192.168.56.106) active the response of the requested file /login.php will be working webpage, as shown in the following picture. This page can then be used to lure the an attacker into waisting time and resources by trying to breach it. 

| ![](readme_imgs/login_proxy_hover.png)|
|:---:|
|  Response of the request of the /login.php file from the reverse proxy honeypot |

## HTML modification of an existing file 

While in the previous section the proxy forged a completely new packet from scratch, matching a non-existing requested file, in this case the proxy edits the HTML file in the response of the server. The proxy receives a response from the server matching, a honeytoken, which will then result in manipulating the HTML file of that response. The manipulation can be in versatile. In this example, the manipulation will be the simple insertion of an HTML comment. The comment will contain login credentials, which seem to be for developing purposes only. It appears like an error, that the comment has not been removed. This is possible by searching the HTML document for any given HTML tag, in this case the closing ```</body>``` tag, removing that tag and then inserting the desired content with the removed tag at the end of it. 

### Example Modification 

The following two pictures show the response of the host (192.168.56.102) for the requested file /home.html and the corresponding source code. 

|  ![](readme_imgs/home_host.png) | ![](readme_imgs/home_host_source.png)  |
| :------------: | :------------: |
|  Response of the host    | Source code |


With the reverse proxy honeypot (192.168.56.106) active the response of the requested file /home.html will be the same webpage, as shown in the following two pictures. But in this case the proxy adds an additional html comment into the /home.html file. 

| ![](readme_imgs/home_proxy.png)   | ![](readme_imgs/home_proxy_source.png) |
| :------------: | :------------: |
|  Response of the honeypot  |  Source code  |







# Prerequisites 

- Docker
- Docker-compose 
- SQL Database 

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


