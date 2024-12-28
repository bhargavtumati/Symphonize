package com.springboot.banking.controller;

import java.util.List;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.springboot.banking.dto.AccountDto;
import com.springboot.banking.service.AccountService;

@RestController
@RequestMapping("/api/accounts")
public class AccountController {
 
	// create object for service class
	private AccountService accountservice;

	// constructor for controller 
	public AccountController(AccountService accountservice) {
		this.accountservice = accountservice;
	}
	
	// Add Account REST API
	@PostMapping("/addAccount")
	public ResponseEntity<AccountDto> addAccount(@RequestBody AccountDto accountDto){
		
		return new ResponseEntity<>(accountservice.createAccount(accountDto), HttpStatus.CREATED);
		
	}
	
	// Get Account REST API
	@GetMapping("/getAccount/{id}")
	public ResponseEntity<AccountDto> getAccountbyId(@PathVariable Long id){
		AccountDto accountDto =accountservice.getAccountById(id);
		return ResponseEntity.ok(accountDto);
	}
	
	//Deposit REST API
	@PutMapping("/{id}/deposit")
	public ResponseEntity<AccountDto> deposite(@PathVariable Long id, @RequestBody Map<String,Double> request){
		Double amount = request.get("amount");
		AccountDto accountDto = accountservice.deposit(id,amount);
		return ResponseEntity.ok(accountDto);
	}
	
	//Withdraw REST API
	@PutMapping("/{id}/withdraw")
	public ResponseEntity<AccountDto> withdraw(@PathVariable Long id, @RequestBody Map<String,Double> request){
		Double amount = request.get("amount");
		AccountDto accountDto = accountservice.withdraw(id,amount);
		return ResponseEntity.ok(accountDto);
	}
	
	//Change Name REST API
		@PutMapping("/{id}/changeName")
		public ResponseEntity<AccountDto> changeName(@PathVariable Long id, @RequestBody Map<String,String> request){
			String name = request.get("name");
			AccountDto accountDto = accountservice.changeName(id,name);
			return ResponseEntity.ok(accountDto);
		}
	
	//Get All Accounts REST API
	@GetMapping("/getAllAccounts")
	public ResponseEntity<List<AccountDto>> getAllAccounts(){
		List<AccountDto> accounts = accountservice.getAllAccounts();
		return ResponseEntity.ok(accounts);
	}
	
	//Delete Account REST API
	@DeleteMapping("deleteAccount/{id}")
	public ResponseEntity<String> deleteAccount(@PathVariable Long id){
		accountservice.deleteAccount(id);
		return ResponseEntity.ok("Account is deleted successfully!");
	}
	 
}
