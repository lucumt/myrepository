package com.lucumt.quartz;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller("/")
public class QuartzController {
	
	@Autowired
	private JobScheduler jobScheduler;

	@RequestMapping("testScheduler")
	public String testScheduler(){
		return "testScheduler";
	}
	
	@RequestMapping("changeScheduler")
	@ResponseBody
	public String changeScheduler(String expression){
		System.out.println("执行时间被修改为:\t"+expression);
		jobScheduler.resetJob(expression);
		return "SUCCESS";
	}

}
