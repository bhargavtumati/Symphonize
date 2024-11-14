package com.jobs.bitlabs;

import org.modelmapper.ModelMapper;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;


@SpringBootApplication
public class BitlabsApplication {

	public static void main(String[] args) {
		SpringApplication.run(BitlabsApplication.class, args);
	}

	@Bean
	public ModelMapper modelMapper() {
		
		
		return new ModelMapper();
	}

}
