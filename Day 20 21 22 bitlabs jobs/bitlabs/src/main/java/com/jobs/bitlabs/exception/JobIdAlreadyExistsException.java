package com.jobs.bitlabs.exception;
@SuppressWarnings("serial")
public class JobIdAlreadyExistsException extends RuntimeException {

	public JobIdAlreadyExistsException(String message) {
        super(message);
    }
}

