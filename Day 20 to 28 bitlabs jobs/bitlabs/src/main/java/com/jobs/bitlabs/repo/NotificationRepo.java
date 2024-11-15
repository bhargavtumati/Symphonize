package com.jobs.bitlabs.repo;

import com.jobs.bitlabs.entity.Notification;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
@Repository
public interface NotificationRepo extends JpaRepository<Notification, Long> {
    List<Notification> findByCompanyId(String companyId);
}