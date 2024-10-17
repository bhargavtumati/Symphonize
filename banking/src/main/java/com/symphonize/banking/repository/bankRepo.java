package com.symphonize.banking.repository;

import org.springframework.stereotype.Repository;
import com.symphonize.banking.entity.BankUser;
import org.springframework.data.jpa.repository.JpaRepository;

@Repository
public interface bankRepo extends JpaRepository<BankUser,String> {

	
}
