#! /bin/bash
function read_file(){
  basepath=`echo $1 | sed -e "s/convert/convert_result/g"`
  for file in `ls $1`
  do
	  if [ -d $1"/"$file ] 
	  then
		  read_file $1"/"$file
	  else
		  # 读取文件名称
		  filename=`echo $1"/"$file | rev | cut -d'/' -f 1 | cut -d'.' -f 2 | rev`
		  drcfile=$basepath
		  drcfile+="/"
		  drcfile+=$filename
		  drcfile+=".drc"
		  #echo $drcfile
         
		  mkdir -p $basepath
		  echo "--------------------"
		  #echo $basepath
		  #echo $drcfile
		  inputfile=$1"/"$file
          outputfile=$drcfile

		  #./draco_encoder -point_cloud -i test_data/test.ply -o result_data/test.drc
		  echo "输入文件$inputfile"
		  ./draco_encoder -point_cloud -i $inputfile -o $outputfile
		  echo "生成文件$outputfile"

	  fi
  done

}

#result=`echo $1 | sed -e "s/convert/convert_result/g"`
#mkdir $result
read_file $1

# 使用命令 bash file_convert.sh /root/test/draco/build/convert
