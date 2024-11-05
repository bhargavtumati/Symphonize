package com.springboot.app;

import org.springframework.stereotype.Component;

@Component
public class Desktop implements Computer {

     public void print() {
    	System.out.println("this is a Desktop Computer");
     }
      
}
