package system;

public class teacher extends user{
    double rate;
    String subject;

    public teacher() {
    }

    public teacher(String name, int age, String sex, String phonenumber, String address, String email, String subject, double rate) {
        super(name, age, sex, phonenumber, address, email);
        this.subject = subject;
        this.rate = rate;
    }

    public double getRate() {
        return rate;
    }

    public void setRate(double rate) {
        this.rate = rate;
    }

    public String getSubject() {
        return subject;
    }

    public void setSubject(String subject) {
        this.subject = subject;
    }
}




























