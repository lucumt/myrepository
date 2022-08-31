pipeline {
  agent {
    node {
      label 'nodejs'
    }

  }
  stages {
    stage('初始阶段') {
      parallel {
        stage('拉取代码') {
          agent none
          steps {
            git(credentialsId: 'gitlab-account', url: 'http://gitlab.xxx.com/lucumt-group/lucumt-common-web.git', branch: '$BRANCH_NAME', changelog: true, poll: false)
            sh '''ls -al
echo “拉取代码成功“'''
          }
        }

        stage('识别系统环境') {
          agent none
          steps {
            script {
              switch(PRODUCT_PHASE) {
                case "sit":
                env.NODE_PORT = 13000
                env.CONFIG_FILE = “.env.sit“
                break
                case "test":
                env.NODE_PORT = 14000
                env.CONFIG_FILE = ".env.test"
                break
                case “prod“:
                env.NODE_PORT = 15000
                env.CONFIG_FILE = ".env.production"
                break
              }
              print(env.NODE_PORT)
              env.BUILD_TAG = new Date().format("yyyyMMdd-HHmmss")
            }

          }
        }

      }
    }

    stage('端口替换') {
      agent none
      steps {
        sh '''sed -i "s/10.30.5.150/10.30.5.170/g" $CONFIG_FILE

cat $CONFIG_FILE'''
      }
    }

    stage('项目编译') {
      agent none
      steps {
        container('nodejs') {
          sh '''npm install node@16.13.1 --registry https://mirrors.hirain.com/repository/NPM/

# 根据不同阶段进行编译构建
npm run build:${PRODUCT_PHASE}'''
        }

      }
    }

    stage('镜像构建') {
      agent none
      steps {
        container('nodejs') {
          sh 'docker build -f kubesphere/Dockerfile -t lucumt-common-web:$BUILD_TAG .'
        }

      }
    }

    stage('镜像推送') {
      agent none
      steps {
        container('nodejs') {
          withCredentials([usernamePassword(credentialsId : 'harbor-account' ,usernameVariable : 'DOCKER_USER_VAR' ,passwordVariable : 'DOCKER_PWD_VAR' ,)]) {
            sh 'echo "$DOCKER_PWD_VAR" | docker login $REGISTRY -u "$DOCKER_USER_VAR" --password-stdin'
            sh '''docker tag  lucumt-common-web:$BUILD_TAG $REGISTRY/$DOCKERHUB_NAMESPACE/lucumt-common-web:$BUILD_TAG
docker push  $REGISTRY/$DOCKERHUB_NAMESPACE/lucumt-common-web:$BUILD_TAG'''
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