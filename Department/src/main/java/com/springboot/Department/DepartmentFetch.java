package com.springboot.Department;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.cfg.Configuration;

public class DepartmentFetch {
    public static void main(String[] args) {
        // Step 1: Create SessionFactory from hibernate.cfg.xml
        SessionFactory sessionFactory = new Configuration()
                .configure("hibernate.cfg.xml")
                .addAnnotatedClass(Department.class)
                .buildSessionFactory();

        // Step 2: Open a new session
        Session session = sessionFactory.openSession();

        try {
            // Step 3: Get the Department entity by its ID (replace 121 with actual ID you want to query)
            Department department = session.get(Department.class, 121);

            if (department != null) {
                // Step 4: Print out the department details (you can modify this based on your actual properties)
                System.out.println("Department ID: " + department.getCustomerId());
                System.out.println("Department Name: " + department.getCustomerName());
                System.out.println("Department Email: " + department.getCustomerEmail());
                System.out.println("Department City: " + department.getCustomerCity());
            } else {
                System.out.println("Department with ID 121 not found.");
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // Step 5: Close the session
            session.close();

            // Step 6: Close the session factory (optional but good practice)
            sessionFactory.close();
        }
    }
}
