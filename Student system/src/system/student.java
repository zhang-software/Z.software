package system;

public class student extends user{
    double grand;
    int classes;

    public student() {
    }

    public student(String name, int age, String sex, String phonenumber, String address, String email, int classes, double grand) {
        super(name, age, sex, phonenumber, address, email);
        this.classes = classes;
        this.grand = grand;
    }

    public double getGrand() {
        return grand;
    }

    public void setGrand(double grand) {
        this.grand = grand;
    }

    public int getClasses() {
        return classes;
    }

    public void setClasses(int classes) {
        this.classes = classes;
    }
}
