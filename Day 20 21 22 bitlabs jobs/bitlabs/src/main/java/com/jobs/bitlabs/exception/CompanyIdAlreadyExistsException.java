package com.jobs.bitlabs.exception;


@SuppressWarnings("serial")
public class CompanyIdAlreadyExistsException extends RuntimeException {
    public CompanyIdAlreadyExistsException(String message) {
        super(message);
    }
}
