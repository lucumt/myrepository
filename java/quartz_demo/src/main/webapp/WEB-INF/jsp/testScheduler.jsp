<%@ page language="java" import="java.util.*" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8">
	<title>动态设置quartz</title>
	<script type="text/javascript" src="js/jquery-2.1.1.min.js"></script>
	<link rel="stylesheet" type="text/css" href="js/bootstrap/css/bootstrap.min.css"/>
	<script type="text/javascript" src="js/bootstrap/js/bootstrap.min.js"></script>
	<style type="text/css">
	  .container{
	     margin-top: 30px;
	     margin-left: auto;
	     margin-right: auto;
	     padding: 10px;
	     background-color: #d0d0d0;
	     border-radius: 5px;
	     min-height:400px;
	  }
	  
	  .hidden{
	     display: none;
	  }
	</style>
	<script type="text/javascript">
	  function changeScheduler(){
		  var hiddenId = $(".hidden").attr("id");
		  var expression = null;
		  if(hiddenId=="scheduler_one"){
			  $("#scheduler_one").removeClass("hidden");
			  $("#scheduler_two").addClass("hidden");
			  expression="0/10 * * * * ?";
		  }else{
			  $("#scheduler_one").addClass("hidden");
			  $("#scheduler_two").removeClass("hidden");
			  expression="0/30 * * * * ?";
		  }
		  sendChangeRequest(expression);
	  }
	  
	  function sendChangeRequest(expression){
		  $.ajax({
			  url:"changeScheduler",
			  type:"post",
			  data:{
				  expression:expression
			  },
			  success:function(){
			  }
		  });
	  }
	</script>
</head>
<body>
<div class="container-fluid container">
     <div id="scheduler_one">
                      当前定时任务的表达式为<b>0/10 * * * * ?</b>,每隔10秒输出一次
     </div>
     <div id="scheduler_two" class="hidden">
                      当前定时任务的表达式为<b>0/30 * * * * ?</b>,每隔30秒输出一次
     </div>
     <button type="button" class="btn btn-primary btn-sm" onclick="changeScheduler()">切换定时时间</button>
</div>
</body>
</html>