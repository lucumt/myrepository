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
          print "服务器ip: " + SERVER_IP
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

    stage('项目打包') {
      agent none
      steps {
        container('nodejs') {
          sh 'zip -r ${MODULE_NAME}_${BUILD_TIME}.zip  dist/*'
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