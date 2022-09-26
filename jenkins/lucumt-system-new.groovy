pipeline {
  agent {
    node {
      label 'maven'
    }

  }
  stages {
    stage('拉取代码') {
      agent none
      steps {
        git(credentialsId: 'gitlab-account', url: 'http://gitlab.xxx.com/lucumt-group/system.git', branch: '$BRANCH_NAME', changelog: true, poll: false)
      }
    }

    stage('识别系统环境') {
      agent none
      steps {
        sh 'sed -i "s/10.30.5.150/10.30.5.170/g" app/src/main/resources/bootstrap.yml'
        script {
          def PROJECT_NAME='lucumt-system'
          def BUILD_TYPE="lucumt-"+PRODUCT_PHASE
          def NACOS_NAMESPACE=''
          env.DUBBO_IP = "10.30.5.170"

          response = sh(script: "curl -X GET 'http://xxx.xxx.xxx.xxx:8848/nacos/v1/console/namespaces'", returnStdout: true)
          jsonData = readJSON text: response
          namespaces = jsonData.data
          for(nm in namespaces){
            if(BUILD_TYPE==nm.namespaceShowName){
              NACOS_NAMESPACE = nm.namespace
            }
          }

          response = sh(script: "curl -X GET 'http://xxx.xxx.xxx.xxx:8848/nacos/v1/cs/configs?dataId=lucumt-custom-config.json&group=lucumt-custom-config&tenant=0f894ca6-4231-43dd-b9f3-960c02ad20fa'", returnStdout: true)
          jsonData = readJSON text: response
          configs = jsonData.portConfig
          for(config in configs){
            project = config.project
            if(project!=PROJECT_NAME){
              continue
            }
            ports = config.ports
            for(port in ports){
              if(port.env!=BUILD_TYPE){
                continue
              }
              env.NODE_PORT = port.server
              env.DUBBO_PORT = port.dubbo
            }
          }

          yamlFile = 'app/src/main/resources/bootstrap-dev.yml'
          yamlData = readYaml file: yamlFile
          yamlData.dubbo.registry.group = BUILD_TYPE
          yamlData.dubbo.registry.parameters.namespace = NACOS_NAMESPACE
          yamlData.spring.cloud.nacos.discovery.group = BUILD_TYPE
          yamlData.spring.cloud.nacos.discovery.namespace = NACOS_NAMESPACE
          yamlData.spring.cloud.nacos.config.namespace = NACOS_NAMESPACE
          sh "rm $yamlFile"


          writeYaml file: yamlFile, data: yamlData
        }

      }
    }

    stage('单元测试') {
      agent none
      steps {
        container('maven') {
          sh '''mvn clean compile test
echo "执行相关的单元测试"'''
          script {
            env.PROJECT_VERSION = sh(script: 'mvn help:evaluate -Dexpression=project.version -q -DforceStdout', returnStdout: true)
            env.BUILD_TIME = new Date().format("yyyyMMdd-HHmmss")
            env.BUILD_TAG = PROJECT_VERSION + "-" + BUILD_TIME
          }

        }

      }
    }

    stage('代码分析') {
      agent none
      steps {
        container('maven') {
          withCredentials([string(credentialsId : 'lucumt-sonar-token' ,variable : 'SONAR_TOKEN' ,)]) {
            withSonarQubeEnv('sonar') {
              sh '''echo $PROJECT_VERSION
mvn sonar:sonar \\
  -Dsonar.projectKey=lucumt-system \\
  -Dsonar.host.url=http://10.30.5.170:32387 \\
  -Dsonar.login=$SONAR_TOKEN'''
            }

          }

          timeout(unit: 'HOURS', activity: true, time: 1) {
            waitForQualityGate 'false'
          }

        }

      }
    }

    stage('项目编译') {
      agent none
      steps {
        container('maven') {
          sh 'ls'
          sh 'mvn clean compile package -Dmaven.test.skip=true'
        }

      }
    }

    stage('制品保存') {
      agent none
      steps {
        container('maven') {
          archiveArtifacts 'app/target/*.jar'
        }

      }
    }

    stage('镜像构建') {
      agent none
      steps {
        container('maven') {
          sh '''docker build -f kubesphere/Dockerfile \\
-t lucumt-system:$BUILD_TAG  \\
--build-arg  PROJECT_VERSION=$PROJECT_VERSION \\
--build-arg  NODE_PORT=$NODE_PORT \\
--build-arg  DUBBO_PORT=$DUBBO_PORT \\
--build-arg PRODUCT_PHASE=dev .

echo $DUBBO_IP'''
        }

      }
    }

    stage('镜像推送') {
      agent none
      steps {
        container('maven') {
          withCredentials([usernamePassword(credentialsId : 'harbor-account' ,usernameVariable : 'DOCKER_USER_VAR' ,passwordVariable : 'DOCKER_PWD_VAR' ,)]) {
            sh 'echo "$DOCKER_PWD_VAR" | docker login $REGISTRY -u "$DOCKER_USER_VAR" --password-stdin'
            sh '''docker tag  lucumt-system:$BUILD_TAG $REGISTRY/$DOCKERHUB_NAMESPACE/lucumt-system:$BUILD_TAG
docker push  $REGISTRY/$DOCKERHUB_NAMESPACE/lucumt-system:$BUILD_TAG'''
          }

        }

      }
    }

    stage('部署到容器') {
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
    REGISTRY = 'xxx.xxx.xx.xxx:30005'
    DOCKERHUB_NAMESPACE = 'lucumt-library'
    GITHUB_ACCOUNT = 'kubesphere'
  }
}