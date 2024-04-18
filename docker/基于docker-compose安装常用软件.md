[[_TOC_]]

# include使用

```yaml
include:
  - orienlink-auth.yml
  - orienlink-evaluator.yml
  - orienlink-mfs.yml

version: "3"
services:
  orienlink-gateway:
    image: orienlink-gateway:1.3.0.2
    container_name: orienlink-gateway
    restart: always
    environment:
      - TZ=${TZ}
      - NACOS_IP=${NACOS_IP}
      - NACOS_IPADDR=${NACOS_IPADDR}
    ports:
      - 15001:9697
    depends_on:
      - orienlink-auth
      - orienlink-evaluator
      - orienlink-mfs
```

# 安装redis

* `redis.conf`文件

  ```bash
  bind 0.0.0.0
  protected-mode no
  appendonly yes
  requirepass 123456
  ```

* `docker-compose.yml`文件

  ```yaml
  version: '3'
  services:
    redis:
        image: redis:7
        container_name: redis
        restart: always
        command: redis-server /etc/redis.conf
        volumes:
          - $PWD/data:/data
          - $PWD/redis.conf:/etc/redis.conf
        ports:
          - 6379:6379
  ```

# 安装nginx

* `domain.conf`文件

  ```nginx
  server {
  
          listen 8188;
          server_name orienlink;
          location / {
                  root /usr/share/nginx/html;
                  index index.html index.htm;
          }
  
  }
  ```

* `nginx.conf`文件

  ```nginx
  user  nginx;
  worker_processes  auto;
  
  error_log  /var/log/nginx/error.log notice;
  pid        /var/run/nginx.pid;
  
  
  events {
      worker_connections  1024;
  }
  
  
  http {
      include       /etc/nginx/mime.types;
      default_type  application/octet-stream;
  
      log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
  
      access_log  /var/log/nginx/access.log  main;
  
      sendfile        on;
      #tcp_nopush     on;
  
      keepalive_timeout  65;
  
      #gzip  on;
  
      include /etc/nginx/conf.d/*.conf;
  }
  ```

* `docker-compose.yml`文件

  ```yaml
  version: "3"
  services:
     nginx:
       privileged: true
       image: nginx
       restart: always
       container_name: nginx
       ports:
         - "80:80"
         - "15100:15100"
         - "15101:15101"
       volumes:
         - $PWD/html:/usr/share/nginx/html
         - $PWD/conf.d:/etc/nginx/conf.d
         - $PWD/nginx.conf:/etc/nginx/nginx.conf
         - $PWD/logs:/var/log/nginx
  ```

# 安装nacos

```yaml
version: "3"
services:
  nacos:
    image: nacos_custom:1.0
    restart: always
    container_name: nacos_custom
    ports:
      - 8858:8858
      - 9858:9858
    environment:
      - TZ=Asia/Shanghai
      - NACOS_SERVER_PORT=8858
      - SPRING_DATASOURCE_PLATFORM=mysql
      - MYSQL_SERVICE_HOST=192.168.30.62
      - MYSQL_SERVICE_PORT=3306
      - MYSQL_SERVICE_DB_NAME=nacos_test
      - MYSQL_SERVICE_USER=root
      - MYSQL_SERVICE_PASSWORD=hirain123
      - LDAP_URL=ldap://10.10.0.55:389
      - LDAP_BASE_DC=dc=chinahirain,dc=com
      - LDAP_USER_DN=cn=ldap_user,dc=chinahirain,dc=com
      - LDAP_USER_PASSWORD=ldap_user
      - LDAP_UID=uid
      - LDAP_CASE_SENSITIVE=false
    volumes:
      - $PWD/logs:/home/nacos/logs/
```

# 安装mysql5.7

* `my.cnf`文件

  ```bash
  [mysqld]
  pid-file        = /var/run/mysqld/mysqld.pid
  socket          = /var/run/mysqld/mysqld.sock
  datadir         = /var/lib/mysql
  lower_case_table_names=1
  #bind-address   = 127.0.0.1
  default-time_zone = '+8:00'
  
  symbolic-links=0
  character-set-server=utf8mb4
  [client]
  default-character-set=utf8mb4
  [mysql]
  default-character-set=utf8mb4
  ```

* `docker-compose.yml`文件

  ```yaml
  version: "3"
  services:
    mysql:
      restart: always
      image: mysql:5.7.31
      container_name: mysql_5.7.31
      privileged: true
      command:
        --character-set-server=utf8mb4
        --collation-server=utf8mb4_general_ci
        --explicit_defaults_for_timestamp=true
      volumes:
        - $PWD/data:/var/lib/mysql
        - $PWD/conf/my.cnf:/etc/mysql/my.cnf
        - $PWD/logs:/logs
      environment:
        - "MYSQL_ROOT_PASSWORD=hirain123"
        - "MYSQL_ROOT_HOST=%"
        - "TZ=Asia/Shanghai"
      ports:
        - 3306:3306
  ```
