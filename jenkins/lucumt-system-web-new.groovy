pipeline {
  agent {
    node {
      label 'nodejs'
    }

  }
  stages {
    stage('拉取代码') {
      agent none
      steps {
        git(credentialsId: 'gitlab-account', url: 'http://gitlab.xxx.com/lucumt-group/lucumt-system-web.git', branch: '$BRANCH_NAME', changelog: true, poll: false)
      }
    }

    stage('识别系统环境') {
      agent none
      steps {
        script {
          def BUILD_TYPE="lucumt-"+PRODUCT_PHASE
          env.SERVER_IP = "10.30.5.170"
          env.BUILD_TAG = new Date().format(“yyyyMMdd-HHmmss“)



          response = sh(script: "curl -X GET 'http://xxx.xxx.xxx.xxx:8848/nacos/v1/cs/configs?dataId=lucumt-custom-config.json&group=lucumt-custom-config&tenant=0f894ca6-4231-43dd-b9f3-960c02ad20fa'", returnStdout: true)
          jsonData = readJSON text: response
          configs = jsonData.portConfig
          for(config in configs){
            project = config.project
            ports = config.ports
            for(port in ports){
              if(port.env!=BUILD_TYPE){
                continue
              }
              if(project=='lucumt-gateway'){
                env.GATEWAY_PORT = port.server
              }
              if(project=='lucumt-system-web'){
                env.NODE_PORT = port.server
              }
            }
          }
        }

        sh '''rm .env.sit
touch .env.sit

echo "ENV = \'production\'" >> .env.sit
echo "VITE_BASE_API = \'http://$SERVER_IP:$GATEWAY_PORT/lucumt-system\'" >> .env.sit
echo "VITE_SYSTEM_URL = \'http://$SERVER_IP:$NODE_PORT\'" >> .env.sit

cat .env.sit'''
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
          sh 'docker build -f kubesphere/Dockerfile -t lucumt-system-web:$BUILD_TAG .'
        }

      }
    }

    stage('镜像推送') {
      agent none
      steps {
        container('nodejs') {
          withCredentials([usernamePassword(credentialsId : 'harbor-account' ,usernameVariable : 'DOCKER_USER_VAR' ,passwordVariable : 'DOCKER_PWD_VAR' ,)]) {
            sh 'echo "$DOCKER_PWD_VAR" | docker login $REGISTRY -u "$DOCKER_USER_VAR" --password-stdin'
            sh '''docker tag  lucumt-system-web:$BUILD_TAG $REGISTRY/$DOCKERHUB_NAMESPACE/lucumt-system-web:$BUILD_TAG
docker push  $REGISTRY/$DOCKERHUB_NAMESPACE/lucumt-system-web:$BUILD_TAG'''
          }

        }

      }
    }

    stage('部署到dev') {
      agent none
      steps {
        kubernetesDeploy(enableConfigSubstitution: true, deleteResource: false, kubeconfigId: 'lucumt-kubeconfig', configs: 'kubesphere/deploy.yml')
      }
    }

  }
  environment {
    DOCKER_CREDENTIAL_ID = 'harbor-id'
    GITHUB_CREDENTIAL_ID = 'gitlab-id'
    KUBECONFIG_CREDENTIAL_ID = 'lucumt-kubeconfig'
    REGISTRY = '10.30.5.170:30005'
    DOCKERHUB_NAMESPACE = 'lucumt-library'
    GITHUB_ACCOUNT = 'kubesphere'
  }
}