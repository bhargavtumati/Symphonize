package com.symphonize.banking.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;


import com.symphonize.banking.requests.BankLoginRequest;
import com.symphonize.banking.service.BankService;

@RestController
public class bankController {
	
	@Autowired
	BankService bankservice;
	
	@PostMapping("/deposit")
	public String deposit(@RequestBody BankLoginRequest banklr, @RequestParam double amount) {
	    return bankservice.deposite(banklr.getaccountNumber(), amount);
	}

	@PostMapping("/withdraw")
	public String withdraw(@RequestBody BankLoginRequest banklr, @RequestParam double amount) {
	    return bankservice.withdraw(banklr.getaccountNumber(), amount);
	}

	
	

}
