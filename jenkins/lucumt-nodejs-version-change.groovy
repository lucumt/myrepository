pipeline {
  agent {
    kubernetes {
      inheritFrom 'nodejs base'
      containerTemplate {
        name 'nodejs'
        image 'node:16.16.0'
      }

    }

  }
  stages {
    stage('拉取') {
      agent none
      steps {
        container('nodejs') {
          git(url: 'http://gitlab.xxx.com/xxxxx-frontend/xxxxx-evaluator-web.git', credentialsId: 'gitlab-token', branch: '$BRANCH_NAME', changelog: true, poll: false)
        }

      }
    }

    stage('识别系统环境') {
      agent none
      steps {
        container('nodejs') {
          script {
            env.PROJECT_NAME="xxxxx-evaluator-web"


            response = sh(script: "curl -X GET 'http://aeectss.xxx.local:8858/nacos/v1/cs/configs?dataId=xxxxx-custom-server-config.json&group=xxxxx-custom-config&tenant=26e0c3df-a0c7-4fe0-9b59-d04c5ac48481'", returnStdout: true)
            jsonData = readJSON text: response
            configs = jsonData.portConfig
            for(config in configs){
              project = config.project
              ports = config.ports
              for(port in ports){
                if(port.env!=PRODUCT_PHASE){
                  continue
                }
                if(project=='xxxxx-gateway'){
                  env.GATEWAY_PORT = port.server
                }
              }
            }
            print env.GATEWAY_PORT

            response = sh(script: "curl -X GET 'http://aeectss.xxx.local:8858/nacos/v1/cs/configs?dataId=xxxxx-custom-front-config.json&group=xxxxx-custom-config&tenant=26e0c3df-a0c7-4fe0-9b59-d04c5ac48481'", returnStdout: true)
            jsonData = readJSON text: response

            configs = jsonData.portConfig
            for(config in configs){
              project = config.project
              ports = config.ports
              for(port in ports){
                if(port.env!=PRODUCT_PHASE){
                  continue
                }
                if(project!=PROJECT_NAME){
                  continue
                }
                env.NODE_PORT = port.server
              }
            }
            print env.NODE_PORT

            env.BUILD_TAG = "" + new Date().format("yyyyMMdd-HHmmss")
          }

        }

        sh '''SERVER_GATEWAY_URL="http:\\/\\/${TARGET_IP}:${GATEWAY_PORT}\\/"
sed -i "s/SERVER_GATEWAY_URL/${SERVER_GATEWAY_URL}/g" cicd/xxxxx.conf

cat cicd/xxxxx.conf'''
      }
    }

    stage('编译') {
      agent none
      steps {
        container('nodejs') {
          sh '''rm -rf node_modules package-lock.json yarn.lock
npm cache clean --force

npm config set registry https://mirrors.xxx.com/repository/NPM/

npm install
npm run build:qiankun'''
        }

      }
    }

    stage('镜像构建') {
      agent none
      steps {
        container('base') {
          sh '''echo $NODE_PORT
cat cicd/Dockerfile
docker build -f cicd/Dockerfile  --build-arg  PRODUCT_PHASE=$PRODUCT_PHASE -t xxxxx-evaluator-web:$BUILD_TAG .'''
        }

      }
    }

    stage('推送') {
      agent none
      steps {
        container('base') {
          withCredentials([usernamePassword(credentialsId : 'harbor-account' ,passwordVariable : 'DOCKER_PWD_VAR' ,usernameVariable : 'DOCKER_USER_VAR' ,)]) {
            sh 'echo "$DOCKER_PWD_VAR" | docker login $REGISTRY -u "$DOCKER_USER_VAR" --password-stdin'
            sh '''docker tag  xxxxx-evaluator-web:$BUILD_TAG $REGISTRY/$DOCKERHUB_NAMESPACE/xxxxx-evaluator-web:$BUILD_TAG
docker push  $REGISTRY/$DOCKERHUB_NAMESPACE/xxxxx-evaluator-web:$BUILD_TAG'''
          }

        }

      }
    }

    stage('部署') {
      agent none
      steps {
        sshagent(credentials: ['10-30-31-60-key']) {
          sh '''if [ $TARGET_IP = \'10.30.31.60\' ];then 
            ssh -o StrictHostKeyChecking=no root@10.30.31.60  \'bash -s\' < cicd/ssh_front_deploy.sh "${REGISTRY}/${DOCKERHUB_NAMESPACE}"  ${NODE_PORT} ${PRODUCT_PHASE} "$PROJECT_NAME:${BUILD_TAG}" 
            fi'''
        }

        sshagent(credentials: ['10-30-31-61-key']) {
          sh '''if [ $TARGET_IP = \'10.30.31.61\' ];then 
          ssh -o StrictHostKeyChecking=no root@10.30.31.61  \'bash -s\' < cicd/ssh_front_deploy.sh "${REGISTRY}/${DOCKERHUB_NAMESPACE}"  ${NODE_PORT} ${PRODUCT_PHASE} "$PROJECT_NAME:${BUILD_TAG}"
          fi'''
        }

      }
    }

  }
  environment {
    DOCKER_CREDENTIAL_ID = 'harbor-id'
    GITHUB_CREDENTIAL_ID = 'gitlab-id'
    KUBECONFIG_CREDENTIAL_ID = 'xxxxx-kubeconfig'
    REGISTRY = 'aeectss.xxx.local:30005'
    DOCKERHUB_NAMESPACE = 'xxxxx-front-library'
    GITHUB_ACCOUNT = 'kubesphere'
  }
}