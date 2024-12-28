package com.jobs.bitlabs.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;

@ControllerAdvice
public class GlobalExceptionHandler {

   

    @ExceptionHandler(CustomException.class)
    public ResponseEntity<Response> handleXustomException(CustomException ex, WebRequest request) {
        Response errorResponse = new Response(
                HttpStatus.CONFLICT.value(),
                ex.getMessage(),
                System.currentTimeMillis()
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.CONFLICT);
    }

   
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Response> handleGeneralException(Exception ex, WebRequest request) {
        Response errorResponse = new Response(
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                "An unexpected error occurred",
                System.currentTimeMillis()
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
