package com.jobs.bitlabs.service;

import java.util.List;


import org.springframework.stereotype.Service;

import com.jobs.bitlabs.entity.Notification;
import com.jobs.bitlabs.repo.NotificationRepo;

@Service
public class NotificationService {

	
    private NotificationRepo notificationRepo;


    public NotificationService(NotificationRepo notificationRepo) {
        this.notificationRepo = notificationRepo;
    }

    public Notification createNotification(String CompanyId, String jobId, Long applicantId) {
        Notification notification = new Notification();
        notification.setCompanyId(CompanyId);
        notification.setJobId(jobId);
        notification.setApplicantId(applicantId);
        notification.setMessage("A new application has been submitted.");
        return notificationRepo.save(notification);
    }

    public List<Notification> getNotifications(String companyId) {
        return notificationRepo.findByCompanyId(companyId);
    }
}

