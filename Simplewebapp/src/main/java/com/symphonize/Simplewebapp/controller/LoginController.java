package com.symphonize.Simplewebapp.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LoginController {
	
	  @RequestMapping("/login")
      public String Login() {
    	  return "please login...!!!";
      }
}
