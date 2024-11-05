import java.util.Scanner;

public class StudentManagementSystem {
    public static void main(String[] args) {
        Reception reception = new Reception();
        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("-----------------");
            System.out.println("1. Add Student");
            System.out.println("2. Update Student");
            System.out.println("3. Delete Student");
            System.out.println("4. Search Student by ID");
            System.out.println("5. Display All Students");
            System.out.println("6. Exit");
            System.out.print("Enter your choice: ");
            int choice = scanner.nextInt();
            scanner.nextLine(); // Consume newline

            switch (choice) {
                case 1:
                    System.out.print("Enter Student ID: ");
                    String id = scanner.nextLine();
                    System.out.print("Enter Name: ");
                    String name = scanner.nextLine();
                    System.out.print("Enter Age: ");
                    int age = scanner.nextInt();
                    scanner.nextLine(); // Consume newline
                    System.out.print("Enter Grade: ");
                    String grade = scanner.nextLine();
                    Student student = new Student(id, name, age, grade);
                    reception.addStudent(student);
                    break;
                case 2:
                    System.out.print("Enter Student ID to update: ");
                    id = scanner.nextLine();
                    System.out.print("Enter New Name: ");
                    name = scanner.nextLine();
                    System.out.print("Enter New Age: ");
                    age = scanner.nextInt();
                    scanner.nextLine(); // Consume newline
                    System.out.print("Enter New Grade: ");
                    grade = scanner.nextLine();
                    reception.updateStudent(id, name, age, grade);
                    break;
                case 3:
                    System.out.print("Enter Student ID to delete: ");
                    id = scanner.nextLine();
                    reception.deleteStudent(id);
                    break;
                case 4:
                    System.out.print("Enter Student ID to search: ");
                    id = scanner.nextLine();
                    Student foundStudent = reception.searchStudentById(id);
                    if (foundStudent != null) {
                        System.out.println("Student found: " + foundStudent);
                    } else {
                        System.out.println("Student not found with ID: " + id);
                    }
                    break;
                case 5:
                    reception.displayAllStudents();
                    break;
                case 6:
                    System.out.println("Exiting...");
                    scanner.close();
                    return;
                default:
                    System.out.println("Invalid choice. Please try again.");
            }
        }
    }
}
