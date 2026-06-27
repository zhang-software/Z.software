package JiSuanQI;

import java.util.Scanner;

public class system {
    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);
        system bb = new system();


        System.out.println("--------------------");
        System.out.println("please enter two number~");
        System.out.println("--------------------");
        System.out.println("click 1 to add");
        System.out.println("click 2 to subtract");
        System.out.println("click 3 to multiply");
        System.out.println("click 4 to divide");

        double a = sc.nextInt();
        double b = sc.nextInt();
        int c = sc.nextInt();
        switch (c) {
            case 1:
                bb.add(a, b);
                break;
            case 2:
                bb.subtract(a, b);
                break;
            case 3:
                bb.multiply(a, b);
                break;
            case 4:
                bb.divide(a, b);
                break;
        }


    }

    public void add(double a, double b) {
        double result = a + b;
        System.out.println(result);
    }
    public void subtract(double a, double b) {
        double result = a - b;
        System.out.println(result);
    }
    public void multiply(double a, double b) {
        double result = a * b;
        System.out.println(result);
    }
    public void divide(double a, double b) {
        if(b==0){
            System.out.println("zero");
        }
        else {
            double result = a / b;
            System.out.println(result);
        }

    }
}

