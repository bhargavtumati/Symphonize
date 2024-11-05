import java.util.HashMap;
import java.util.InputMismatchException;
import java.util.Map;
import java.util.Scanner;

public class Reception {
    private Map<String, Student> studentRecords = new HashMap<>();

    public void addStudent(Student student) {
        studentRecords.put(student.getStudentId(), student);
        System.out.println("Student added: " + student);
    }

    public void updateStudent(String studentId, String name, int age, String grade) {
        Student student = studentRecords.get(studentId);
        if (student != null) {
            student.setName(name);
            student.setAge(age);
            student.setGrade(grade);
            System.out.println("Student updated: " + student);
        } else {
            System.out.println("Student not found with ID: " + studentId);
        }
    }

    public void deleteStudent(String studentId) {
        
        Student removedStudent = studentRecords.get(studentId);
       
        if (removedStudent != null ) {
            Scanner sc = new Scanner(System.in);
            System.out.println("please confirm the deletion(y/n):"+removedStudent);
            
            try{
            String y = sc.nextLine();
            
            if (y.equals("y")){
                removedStudent = studentRecords.remove(studentId);
                System.out.println("Student removed: " + removedStudent);}
                else if(y.equals("n")){
                    System.out.println("deletion aborted");
                }
          
        
    }
    catch(InputMismatchException e){
        System.out.println("Input Mismatch");
    }
    }
    else {
        System.out.println("Student not found with ID: " + studentId);
    }
    
   // sc.close();
    }

    public Student searchStudentById(String studentId) {
        return studentRecords.get(studentId);
    }

    public void displayAllStudents() {
        for (Student student : studentRecords.values()) {
            System.out.println(student);
        }
        if (studentRecords.size()==0){
           System.out.println("No Records to Display");
        }
    }
}
