package com.jobs.bitlabs.exception;

@SuppressWarnings("serial")
public class InvalidTitleException extends RuntimeException {
    public InvalidTitleException(String message) {
        super(message);
    }
}

