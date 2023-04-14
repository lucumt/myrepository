pipeline {
  agent {
    node {
      label 'maven'
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

          switch(MODULE_NAME) {
            case "idp-gateway":
            GIT_URL = "http://gitlab.xxx.com/idp-group/idp-gateway.git"
            break
            case "idp-system":
            GIT_URL = "http://gitlab.xxx.com/idp-group/system.git"
            break
            case "idp-data":
            GIT_URL = "http://gitlab.xxx.com/idp-group/idp-data.git"
            break
            case "idp-label":
            GIT_URL = "http://gitlab.xxx.com/idp-group/idp-label.git"
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
        container('maven') {
          sh '''if [[ $MODULE_NAME == idp-gateway ]]; then
  configFile=src/main/resources/bootstrap.yml
else
  configFile=app/src/main/resources/bootstrap.yml
fi

sed -i "s/10.30.5.170/$SERVER_IP/g" $configFile
sed -i "s/10.30.5.150/$SERVER_IP/g" $configFile
sed -i "s/10.10.1.145/$SERVER_IP/g" $configFile

echo "============修改后的配置文件如下=============="
cat $configFile'''
          script {
            def PROJECT_NAME='idp-system'
            def BUILD_TYPE="idp-"+PRODUCT_PHASE
            def NACOS_NAMESPACE=''

            response = sh(script: "curl -X GET 'http://10.10.1.145:8848/nacos/v1/console/namespaces'", returnStdout: true)
            jsonData = readJSON text: response
            namespaces = jsonData.data
            for(nm in namespaces){
              if(BUILD_TYPE==nm.namespaceShowName){
                NACOS_NAMESPACE = nm.namespace
              }
            }

            boolean isGateway = MODULE_NAME=='idp-gateway'
            response = sh(script: "curl -X GET 'http://10.10.1.145:8848/nacos/v1/cs/configs?dataId=idp-custom-config.json&group=idp-custom-config&tenant=0f894ca6-4231-43dd-b9f3-960c02ad20fa'", returnStdout: true)
            jsonData = readJSON text: response
            configs = jsonData.portConfig
            for(config in configs){
              project = config.project
              if(project!=MODULE_NAME){
                continue
              }
              ports = config.ports
              for(port in ports){
                if(port.env!=BUILD_TYPE){
                  continue
                }
                env.NODE_PORT = port.server
                if(!isGateway){
                  env.DUBBO_PORT = port.dubbo
                }
              }
            }

            //网关没有dubbo配置，同时其结构与其它项目不同，故需要分别处理
            yamlFile = ''
            if(isGateway){
              yamlFile='src/main/resources/bootstrap-dev.yml'
            }else{
              yamlFile='app/src/main/resources/bootstrap-dev.yml'
            }
            yamlData = readYaml file: yamlFile
            if(!isGateway){
              env.DUBBO_IP = SERVER_IP
              yamlData.dubbo.registry.group = BUILD_TYPE
              yamlData.dubbo.registry.parameters.namespace = NACOS_NAMESPACE
            }
            yamlData.spring.cloud.nacos.discovery.group = BUILD_TYPE
            yamlData.spring.cloud.nacos.discovery.namespace = NACOS_NAMESPACE
            yamlData.spring.cloud.nacos.config.namespace = NACOS_NAMESPACE
            sh "rm $yamlFile"


            writeYaml file: yamlFile, data: yamlData
          }

        }

      }
    }

    stage('单元测试') {
      agent none
      steps {
        container('maven') {
          sh '''mvn clean compile -Dmaven.test.skip=true
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
          withCredentials([string(credentialsId : 'idp-sonar-token' ,variable : 'SONAR_TOKEN' ,)]) {
            withSonarQubeEnv('sonar') {
              sh '''echo $PROJECT_VERSION
mvn sonar:sonar \\
  -Dsonar.projectKey=$MODULE_NAME \\
  -Dsonar.host.url=http://10.30.5.170:9990 \\
  -Dsonar.login=$SONAR_TOKEN'''
            }

          }

          timeout(unit: 'HOURS', activity: true, time: 1) {
            waitForQualityGate 'false'
          }

        }

      }
    }

    stage('编译打包') {
      agent none
      steps {
        container('maven') {
          sh 'ls'
          sh 'mvn clean compile package -Dmaven.test.skip=true'
        }

      }
    }

    stage('下载文件') {
      agent none
      steps {
        archiveArtifacts 'target/*.jar,app/target/*.jar'
        echo '请下载生成的jar文件!'
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