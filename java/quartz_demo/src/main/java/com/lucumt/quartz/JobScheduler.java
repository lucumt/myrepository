package com.lucumt.quartz;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

import javax.servlet.ServletContext;

import org.quartz.Scheduler;
import org.quartz.SchedulerException;
import org.quartz.TriggerKey;
import org.quartz.impl.triggers.CronTriggerImpl;
import org.springframework.context.ApplicationContext;
import org.springframework.web.context.ServletContextAware;
import org.springframework.web.context.support.WebApplicationContextUtils;

public class JobScheduler implements ServletContextAware {

	private DateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
	
	private ServletContext context;
	
	@Override
	public void setServletContext(ServletContext context) {
       this.context=context;		
	}

	public void schedulerJob() {
		System.out.println("=========定时输出:\t" + df.format(new Date())); 
	}
	
	public void resetJob(String expression){
		ApplicationContext applicationContext = WebApplicationContextUtils.getRequiredWebApplicationContext(context);
		Scheduler scheduler = (Scheduler) applicationContext.getBean("testScheduler");
		CronTriggerImpl trigger = null;
		try {
			TriggerKey triggerKeys = TriggerKey.triggerKey("testJobTrigger",Scheduler.DEFAULT_GROUP);
			trigger = new CronTriggerImpl();
			trigger.setCronExpression(expression);
			trigger.setKey(triggerKeys);
			scheduler.rescheduleJob(triggerKeys,trigger);
		} catch (ParseException | SchedulerException e) {
			e.printStackTrace();
		}
	}
}
