package com.springboot.loginpage.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.springboot.loginpage.entity.users;
import com.springboot.loginpage.requests.LoginRequest;
import com.springboot.loginpage.service.UserService;

@RestController
public class userscontroller {
	
	 @Autowired
	 UserService userService;
	
     @PostMapping("/addUser")
     public users addUser(@RequestBody users user){
    	 return  userService.addUser(user);
     }
     
     @PostMapping("/loginUser")
     public Boolean loginUser(@RequestBody LoginRequest loginrequest) {
    	 return userService.loginUser(loginrequest);
     }
}

