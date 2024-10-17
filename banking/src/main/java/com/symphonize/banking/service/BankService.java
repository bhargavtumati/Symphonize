package com.symphonize.banking.service;

import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.symphonize.banking.entity.BankUser;
import com.symphonize.banking.repository.bankRepo;
import com.symphonize.banking.requests.BankLoginRequest;

@Service
public class BankService {

	@Autowired
	bankRepo bankrepo;
	
	
	
	
	
	
public String deposite(BankLoginRequest bankLR, double amount) {
	
		Optional<BankUser> User = bankrepo.findById(bankLR.getaccountNumber());
		if(!User.isPresent()) {
			return "No Account";
		}
		BankUser user = User.get();
		
		user.setBalance(user.getBalance()+amount);
		
		
		return "balance set"+ Double.toString(user.getBalance());
	}
	
	
	
	
public String withdraw(BankLoginRequest bankLR, double amount) {
	
	Optional<BankUser> User = bankrepo.findById(bankLR.getaccountNumber());
	if(!User.isPresent()) {
		return "No Account";
	}
	BankUser user = User.get();
	
	user.setBalance(user.getBalance()-amount);
	
	
	return "balance set"+ Double.toString(user.getBalance());
}
	
	
}
