package com.springboot.app;


import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;

@SpringBootApplication
public class SpringbootfirstappApplication {

	public static void main(String[] args) {
		
		
		
		ApplicationContext context = SpringApplication.run(SpringbootfirstappApplication.class, args);
		Dev dev = context.getBean(Dev.class);
	     dev.build();
	}

}
