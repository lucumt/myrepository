pipeline {
  agent {
    node {
      label 'nodejs'
    }

  }
  stages {
    stage('获取代码地址') {
      agent none
      steps {
        script {
          print "镜像版本: " + IMAGE_VERSION
          print "服务器ip: " + SERVER_IP

          if (IMAGE_VERSION.isEmpty()) {
            error("镜像版本为空，构建过程终止!")
          }

          if (SERVER_IP.isEmpty()) {
            error("服务器IP为空，构建过程终止!")
          }

          env.BUILD_TIME = new Date().format("yyyyMMdd-HHmmss")

          switch(MODULE_NAME) {
            case "idp-common-web":
            GIT_URL = "http://gitlab.xxx.com/idp-group/idp-common-web.git"
            break
            case "idp-system-web":
            GIT_URL = "http://gitlab.xxx.com/idp-group/idp-system-web.git"
            break
            case "idp-data-web":
            GIT_URL = "http://gitlab.xxx.com/idp-group/idp-data-web.git"
            break
            case "idp-label-web":
            GIT_URL = "http://gitlab.xxx.com/idp-group/idp-label-web.git"
            break
            case "idp-data-playback-web":
            GIT_URL = "http://gitlab.xxx.com/idp-group/idp-data-playback-web.git"
            break
          }

          print "代码仓库地址: " + GIT_URL
        }

      }
    }

    stage('拉取代码') {
      agent none
      steps {
        git(credentialsId: 'gitlab-account', url: GIT_URL, branch: '$BRANCH_NAME', changelog: true, poll: false)
      }
    }

    stage('识别系统环境') {
      agent none
      steps {
        container('nodejs') {
          script {
            def BUILD_TYPE="idp-"+PRODUCT_PHASE
            env.BUILD_TAG = new Date().format("yyyyMMdd-HHmmss")

            response = sh(script: "curl -X GET 'http://10.10.1.145:8848/nacos/v1/cs/configs?dataId=idp-custom-config.json&group=idp-custom-config&tenant=0f894ca6-4231-43dd-b9f3-960c02ad20fa'", returnStdout: true)
            jsonData = readJSON text: response
            configs = jsonData.portConfig

            for(config in configs){
              project = config.project
              ports = config.ports
              for(port in ports){
                if(port.env!=BUILD_TYPE){
                  continue
                }

                if(project=='idp-gateway'){
                  env.GATEWAY_PORT = port.server
                }

                if(project==MODULE_NAME){
                  env.NODE_PORT = port.server
                }

                if(MODULE_NAME == 'idp-common-web'){
                  if(project=='idp-system-web'){
                    env.SYSTEM_PORT = port.server
                  }
                  if(project=='idp-data-web'){
                    env.DATA_PORT = port.server
                  }
                  if(project=='idp-label-web'){
                    env.LABEL_PORT = port.server
                  }
                  if(project=='idp-data-playback-web'){
                    env.PLAYBACK_PORT = port.server
                  }
                }

              }
            }
          }

          sh '''rm .env.sit
touch .env.sit

# 根据不同的模块进行不同的打印输出
case "$MODULE_NAME" in
   "idp-common-web") echo "idp-common-web"
      echo "VITE_BASE_API = \'http://$SERVER_IP:$GATEWAY_PORT/idp-system\'" >> .env.sit
      echo "VITE_SYSTEM_URL = \'http://$SERVER_IP:$SYSTEM_PORT\'" >> .env.sit
      echo "VITE_DATA_URL = \'http://$SERVER_IP:$DATA_PORT\'" >> .env.sit
      echo "VITE_LABEL_URL = \'http://$SERVER_IP:$LABEL_PORT\'" >> .env.sit
      echo "VITE_DATA_PLAYBACK_URL = \'http://$SERVER_IP:$PLAYBACK_PORT\'" >> .env.sit
      echo "VITE_TRAINING_SOCKET_URL = \'ws://$TRAINING_IP:$TRAINING_PORT\'" >> .env.sit
      
      #替换跳转端口 
      sed -i "s/10.10.3.11/idp-train-ip/g" src/views/CommonApp.vue
      cat src/views/CommonApp.vue
   ;;
   "idp-system-web") echo "idp-system-web"
      echo "VITE_BASE_API = \'http://$SERVER_IP:$GATEWAY_PORT/idp-system\'" >> .env.sit
      echo "VITE_SYSTEM_URL = \'http://$SERVER_IP:$NODE_PORT\'" >> .env.sit
   ;;
   "idp-data-web") echo "idp-data-web"
      echo "VITE_BASE_API = \'http://$SERVER_IP:$GATEWAY_PORT/idp-data\'" >> .env.sit
      echo "VITE_DATA_URL = \'http://$SERVER_IP:$NODE_PORT\'" >> .env.sit
   ;;
   "idp-label-web") echo "idp-label-web"
      echo "VITE_BASE_API = \'http://$SERVER_IP:$GATEWAY_PORT/idp-label\'" >> .env.sit
      echo "VITE_LABEL_URL = \'http://$SERVER_IP:$NODE_PORT\'" >> .env.sit
   ;;
  "idp-data-playback-web") 
      echo "VITE_BASE_API = \'http://$SERVER_IP:$GATEWAY_PORT/idp-data/play/\'" >> .env.sit
      echo "VITE_DATAPLAYBACK_URL = \'http://$SERVER_IP:$NODE_PORT\'" >> .env.sit
   ;;
   *) echo "No option is matched"
   ;;
esac

cat .env.sit'''
        }

      }
    }

    stage('项目编译') {
      agent none
      steps {
        container('nodejs') {
          sh '''npm install node@16.13.1 --registry https://mirrors.xxx.com/repository/NPM/

# 根据不同阶段进行编译构建
npm run build:sit'''
        }

      }
    }

    stage('镜像构建') {
      agent none
      steps {
        container('nodejs') {
          sh '''rm -rf /temp/idp-images
mkdir -p /temp/idp-images

echo "[config]" >> /temp/idp-images/config.ini
echo "node_port=$NODE_PORT" >> /temp/idp-images/config.ini

if [[ -n "$GATEWAY_PORT" ]]
then
  echo "gateway_port=$GATEWAY_PORT" >> /temp/idp-images/config.ini
fi

if [[ -n "$SYSTEM_PORT" ]]
then
  echo "system_port=$SYSTEM_PORT" >> /temp/idp-images/config.ini
fi

if [[ -n "$DATA_PORT" ]]
then
  echo "data_port=$DATA_PORT" >> /temp/idp-images/config.ini
fi

if [[ -n "$LABEL_PORT" ]]
then
  echo "label_port=$LABEL_PORT" >> /temp/idp-images/config.ini
fi

if [[ -n "$PLAYBACK_PORT" ]]
then
  echo "playback_port=$PLAYBACK_PORT" >> /temp/idp-images/config.ini
fi

echo "module_name=$MODULE_NAME" >> /temp/idp-images/config.ini
echo "server_ip=$SERVER_IP" >> /temp/idp-images/config.ini
echo "image_name=${MODULE_NAME}:${IMAGE_VERSION}" >> /temp/idp-images/config.ini
echo "build_time=$BUILD_TIME" >> /temp/idp-images/config.ini
cat /temp/idp-images/config.ini

#构建镜像
docker build -f kubesphere/Dockerfile -t $MODULE_NAME:$IMAGE_VERSION .


#保存镜像
docker save -o  /temp/idp-images/${MODULE_NAME}_${BUILD_TIME}.tar $MODULE_NAME:$IMAGE_VERSION 

# 打包文件
zip -r -j ${MODULE_NAME}_${BUILD_TIME}.zip  /temp/idp-images/*

# 清空多余镜像
docker image prune'''
        }

      }
    }

    stage('下载文件') {
      agent none
      steps {
        archiveArtifacts '*_*.zip'
        echo '请下载生成的zip文件!'
      }
    }

  }
  environment {
    DOCKER_CREDENTIAL_ID = 'harbor-id'
    GITHUB_CREDENTIAL_ID = 'gitlab-id'
    KUBECONFIG_CREDENTIAL_ID = 'idp-kubeconfig'
    REGISTRY = '10.30.5.170:30005'
    DOCKERHUB_NAMESPACE = 'idp-library'
    GITHUB_ACCOUNT = 'kubesphere'
  }
}