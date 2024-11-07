package com.jobs.bitlabs.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(InvalidTitleException.class)
    public ResponseEntity<ErrorResponse> handleInvalidTitleException(InvalidTitleException ex, WebRequest request) {
        ErrorResponse errorResponse = new ErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                ex.getMessage(),
                System.currentTimeMillis()
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(JobIdAlreadyExistsException.class)
    public ResponseEntity<ErrorResponse> handleJobIdAlreadyExistsException(JobIdAlreadyExistsException ex, WebRequest request) {
        ErrorResponse errorResponse = new ErrorResponse(
                HttpStatus.CONFLICT.value(),
                ex.getMessage(),
                System.currentTimeMillis()
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.CONFLICT);
    }

    @ExceptionHandler(CompanyIdAlreadyExistsException.class)
    public ResponseEntity<ErrorResponse> handleCompanyIdAlreadyExistsException(CompanyIdAlreadyExistsException ex, WebRequest request) {
        ErrorResponse errorResponse = new ErrorResponse(
                HttpStatus.CONFLICT.value(),
                ex.getMessage(),
                System.currentTimeMillis()
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.CONFLICT);
    }

    @ExceptionHandler(CompanyIdNotYetRegisteredException.class) 
    public ResponseEntity<ErrorResponse> handleCompanyIdNotYetRegisteredException(CompanyIdNotYetRegisteredException ex, WebRequest request) {
    	ErrorResponse errorResponse = new ErrorResponse(
    			HttpStatus.NOT_FOUND.value(), 
    			ex.getMessage(), 
    			System.currentTimeMillis() 
    			); 
    	return new ResponseEntity<>(errorResponse, HttpStatus.NOT_FOUND); 
    	}
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneralException(Exception ex, WebRequest request) {
        ErrorResponse errorResponse = new ErrorResponse(
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                ex.getMessage(),
              //  "An unexpected error occurred",
                System.currentTimeMillis()
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
