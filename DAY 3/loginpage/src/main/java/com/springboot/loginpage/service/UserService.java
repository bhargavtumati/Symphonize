package com.springboot.loginpage.service;

import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.springboot.loginpage.entity.users;
import com.springboot.loginpage.repository.usersrepo;
import com.springboot.loginpage.requests.LoginRequest;

@Service
public class UserService {
	
	 @Autowired
	 usersrepo usersrepo;
	 
      public users addUser(users user) {
    	  
			return usersrepo.save(user);
		
      }
      public Boolean loginUser(LoginRequest loginRequest) {
    	  
    	  Optional<users>  user = usersrepo.findById(loginRequest.getEmail());
    		  
    		  if (user.isPresent()) {
    			    return false;
    			}
    		  users user1 = user.get();
    		  
    		  if(!user1.getPassword().equals(loginRequest.getPassword())) {
    			  return false;
    			  
    		  }
    		  return true;
    		  
    	  }
      
}
