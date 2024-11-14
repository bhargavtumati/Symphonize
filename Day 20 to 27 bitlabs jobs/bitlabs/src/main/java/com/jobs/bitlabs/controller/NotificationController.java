package com.jobs.bitlabs.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.jobs.bitlabs.entity.Notification;
import com.jobs.bitlabs.service.NotificationService;

@RestController
@RequestMapping("bitlabs.com/notifications")
public class NotificationController {

	@Autowired
	NotificationService notificationService;
	
	@GetMapping("/getjobappplicantnotifications")
	public ResponseEntity<List<Notification>> getNotifications(@RequestParam String companyId) {
	    
		List<Notification> notifications = notificationService.getNotifications(companyId);
	    return new ResponseEntity<>(notifications, HttpStatus.OK);
	}

}
