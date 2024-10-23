package com.springboot.app;

import org.springframework.stereotype.Component;

@Component
public class Laptop implements Computer {

	public void print() {
		System.out.println("This is a Laptop");
	}
	
	
	
}
