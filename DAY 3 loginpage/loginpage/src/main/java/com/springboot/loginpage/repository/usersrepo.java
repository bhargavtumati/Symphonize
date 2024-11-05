package com.springboot.loginpage.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.springboot.loginpage.entity.users;

@Repository
public interface usersrepo extends JpaRepository< users, String > {

	
	
       
}
