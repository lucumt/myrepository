# 基础镜像
FROM  openjdk:8-jdk
# author
LABEL maintainer=luyunqiang

# 创建目录
RUN mkdir -p /home/hirain
# 指定路径
WORKDIR /home/hirain

ARG PRODUCT_PHASE
ARG NODE_PORT
ARG DUBBO_PORT
ENV PARAMS=“--server.port=${NODE_PORT} --spring.application.name=lucumt-system --spring.profiles.active=${PRODUCT_PHASE} --dubbo.protocol.port=${DUBBO_PORT}“
RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

# 复制jar文件到路径
ARG PROJECT_VERSION
ENV BUILD_FILE=app/target/lucumt-system-app-${PROJECT_VERSION}.jar
RUN echo “build file version: ${BUILD_FILE}“
COPY ${BUILD_FILE} /home/hirain/lucumt-system.jar

ENTRYPOINT [“/bin/sh“,“-c“,“java -Dfile.encoding=utf8  -jar lucumt-system.jar ${PARAMS}“]