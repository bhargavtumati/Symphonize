package com.jobs.bitlabs.exception;


@SuppressWarnings("serial")
public class CompanyIdNotYetRegisteredException extends RuntimeException {
    public CompanyIdNotYetRegisteredException(String message) {
        super(message);
    }
}
