package com.springboot.banking.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.springboot.banking.entity.Account;

public interface AccountRepository extends JpaRepository<Account, Long>{
	

}
