package com.springboot.banking.impl;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;

import com.springboot.banking.dto.AccountDto;
import com.springboot.banking.entity.Account;
import com.springboot.banking.mapper.AccountMapper;
import com.springboot.banking.repository.AccountRepository;
import com.springboot.banking.service.AccountService;

@Service
public class AccountServiceImpl implements AccountService{

	private AccountRepository accountrepository;
	
	
	
	public AccountServiceImpl(AccountRepository accountrepository) {
		super();
		this.accountrepository = accountrepository;
	}



	@Override
	public AccountDto createAccount(AccountDto accountDto) {
		// TODO Auto-generated method stub
		Account account = AccountMapper.mapToAccount(accountDto);
		Account savedAccount = accountrepository.save(account);
		return AccountMapper.mapToAccountDto(savedAccount);
	}



	@Override
	public AccountDto getAccountById(Long id) {
		// TODO Auto-generated method stub
		
		
		Account account = accountrepository.findById(id).orElseThrow(() -> new RuntimeException("Account does not exists"));
		return AccountMapper.mapToAccountDto(account);
	}



	@Override
	public AccountDto deposit(Long id, double amount) {
		// TODO Auto-generated method stub
		Account account = accountrepository.findById(id).orElseThrow(() -> new RuntimeException("Account does not exists"));
		
		double total = account.getBalance() + amount;
		account.setBalance(total);
		Account savedAccount = accountrepository.save(account);
		return AccountMapper.mapToAccountDto(savedAccount);
		
	}



	@Override
	public AccountDto withdraw(Long id, double amount) {
		// TODO Auto-generated method stub
		Account account = accountrepository.findById(id).orElseThrow(() -> new RuntimeException("Account does not exists"));
		if (amount>account.getBalance()) 
			throw new RuntimeException("Insufficient Balance");
		
		
		double total = account.getBalance() - amount;
		account.setBalance(total);
		Account savedAccount = accountrepository.save(account);
		return AccountMapper.mapToAccountDto(savedAccount);
	}


	@Override
	public List<AccountDto> getAllAccounts() {
		// TODO Auto-generated method stub
		List<Account> accounts = accountrepository.findAll();
		return accounts.stream().map((account)->AccountMapper.mapToAccountDto(account)).collect(Collectors.toList());
		
	}



	@Override
	public void deleteAccount(Long id) {
		// TODO Auto-generated method stub
		Account account = accountrepository.findById(id).orElseThrow(() -> new RuntimeException("Account does not exists"));
	    
		
		 accountrepository.deleteById(id);
	}
	
	

}
