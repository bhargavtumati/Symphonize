package com.springboot.app;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;




@Component
public class Dev {
	
	@Autowired
	@Qualifier("laptop")
	private Laptop c;
	
	
	public void build() {
		c.print();
		
	}
	

}