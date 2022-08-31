FROM nginx

RUN mkdir -p /usr/share/nginx/html/idp-web

#将dist目录内容复制到nginx容器html内部
COPY dist /usr/share/nginx/html/idp-web
COPY kubesphere/idp.conf /etc/nginx/conf.d/

EXPOSE 8080