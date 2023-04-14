#/!bin/bash

function user_input(){

	# 35m 紫色
	echo -e "\033[35m=================标注与训练平台软件部署与更新操作==================\033[0m"  
	printf "1) 选择要部署功能类别:\n\n\t 1.前端 \t 2.后端\n\n请输入对应数字:"

	# 读取功能类别
	read type

	if [[ $type == 1 ]]; then
		printf "选择的类别是\033[32m前端\033[0m\n"
	elif [[ $type == 2 ]]; then 
		printf "选择的类别是\033[32m后端\033[0m\n"
	else
		printf "\033[31m无效的输入，升级操作终止，请重新执行./deploy.sh\033[0m\n"
		exit 0
	fi

	#前后端模块
	f_mods=('idp-common-web' 'idp-system-web' 'idp-data-web' 'idp-label-web' 'idp-data-playback-web')
	s_mods=('idp-gateway' 'idp-system' 'idp-data' 'idp-label')


	if [[ $type == 1 ]]; then
		mods=( "${f_mods[@]}" )
	else
		mods=( "${s_mods[@]}" )
	fi

	# 根据功能类别选择对应的功能模块
	module_str="\n2) 请选择要部署的模块:\n\n\t"
	for i in "${!mods[@]}";
	do
		module_str="$module_str $(($i+1)).${mods[$i]}\t"
	done 
	module_str="${module_str}\n\n请输入对应数字:"
	printf "$module_str"

    # 读取用户选择并进行判断
	read module

	if [[ $module != ?(-)+([0-9]) ]]; then  
	   printf "\n\033[31m输入的不是数字，升级操作终止，请重新执行./deploy.sh\033[0m\n"
	   exit 0
	fi

	if ! [[ "${mods[$(($module-1))]}" ]]; then
		printf "\n\033[31m选择的模块不存在，升级操作终止，请重新执行./deploy.sh\033[0m\n"
		exit 0
	fi


	printf "选择的模块是\033[32m${mods[$(($module-1))]}\033[0m\n"
    
    load_image $type ${mods[$(($module-1))]}

}

function load_image(){
   type=$1
   module=$2
   
   # 校验升级文件是否存在
   file=$(ls target|sort -r|grep ${module}_20|head -1)
   if [[ -z "$file" ]]
   then    
      printf "\033[31mtarget目录下没有对应的文件，升级操作终止，请重新执行./deploy.sh\033[0m\n"
      exit 0
   fi
   
   # 解压文件
   echo "------------------------------------------------------------------------"
   echo "开始解压镜像压缩文件"
   echo $file
   rm -rf target/data
   mkdir target/data
   unzip -d target/data target/$file
   ls -l target/data

   # 读取ini文件
   ini_path=target/data/config.ini
   node_port=$(awk -F "=" '/node_port/ {print $2}' $ini_path)
   dubbo_port=$(awk -F "=" '/dubbo/ {print $2}' $ini_path)
   server_ip=$(awk -F "=" '/server_ip/ {print $2}' $ini_path)
   image_name=$(awk -F "=" '/image_name/ {print $2}' $ini_path)
   module_name=$(awk -F "=" '/module_name/ {print $2}' $ini_path)
   build_time=$(awk -F "=" '/build_time/ {print $2}' $ini_path)
   echo "------------------------------------------------------------------------"
   echo "config.ini中的配置如下:"
   printf "node   port:\t$node_port\n"
   if [[ -n "$dubbo_port" ]]; then
      printf "dubbo  port:\t$dubbo_port\n"
   fi
   printf "server   ip:\t$server_ip\n"
   printf "module name:\t$module_name\n"
   printf "image  name:\t$image_name\n"
   printf "build  time:\t$build_time\n"
   echo "------------------------------------------------------------------------"

   # 若容器运行，则先关闭
   echo "开始检查并移除旧的容器"
   if [[ -n "$(docker ps -f "name=${module_name}$" -f "status=running" -q )" ]]; then
	  printf "停止镜像: "
      docker stop $module_name
   fi

   # 若容器存在，则删除
   if [[ -n "$(docker ps -a -f "name=${module_name}$"  -q )" ]]; then
      printf "删除镜像: "  
      docker rm $module_name
   fi

   # 加载镜像
   docker load --input target/data/*.tar
   printf "\033[32m完成$module_name对应镜像的导入!\033[0m\n"

   # 拼接成docker要执行字符串
   if [[ $type == 1 ]]; then
       docker_command="docker run -d -p $node_port:8080 --name $module_name $image_name"
   elif [[ $type == 2 && $module_name == "idp-gateway" ]]; then
       docker_command="docker run -d -p $node_port:$node_port -e 'PORT=$node_port' --name $module_name $image_name"
   else
       docker_command="docker run -d -p $node_port:$node_port -p $dubbo_port:$dubbo_port -e 'PORT=$node_port' -e 'DUBBO_IP_TO_REGISTRY=$server_ip'  --name $module_name $image_name"
   fi

   printf "要执行的命令为:\n$docker_command\n"
   container_id=$(eval $docker_command)


   result=$(docker inspect -f {{.State.Running}} $container_id)
   if [[ "$result" = true ]]; then
      printf "\033[32m$module_name对应的容器启动成功,容器id为${container_id:0:12}\033[0m\n"
   else
      printf "\033[31m$module_name对应的容器启动失败,容器id为${container_id:0:12}!\033[0m\n"
   fi
} 

#调用函数执行
user_input
