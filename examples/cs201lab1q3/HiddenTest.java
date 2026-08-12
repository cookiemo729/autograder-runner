import java.util.Objects;

public class HiddenTest {

    public static void main(String[] args) {

        if (args.length != 1) {
            System.exit(2);
        }

        boolean passed;

        switch (args[0]) {

            case "example_one":
                passed = testExampleOne();
                break;

            case "example_two":
                passed = testExampleTwo();
                break;

            case "no_nulls":
                passed = testNoNulls();
                break;

            case "all_nulls":
                passed = testAllNulls();
                break;

            case "nulls_at_ends":
                passed = testNullsAtEnds();
                break;

            default:
                System.exit(2);
                return;
        }

        if (passed) {
            System.out.print("PASS");
            System.exit(0);
        }

        System.out.print("FAIL");
        System.exit(1);
    }


    private static boolean testExampleOne() {

        DoublyLinkedList<Integer> list =
            new DoublyLinkedList<>();

        list.addLast(1);
        list.addLast(null);
        list.addLast(2);

        list.group();

        return (
            list.size() == 3
            && list.first() == null
            && Objects.equals(list.last(), 2)
            && list.toString().equals("null 1 2 ")
        );
    }


    private static boolean testExampleTwo() {

        DoublyLinkedList<Integer> list =
            new DoublyLinkedList<>();

        list.addLast(4);
        list.addLast(null);
        list.addLast(1);
        list.addLast(null);
        list.addLast(3);

        list.group();

        return (
            list.size() == 5
            && list.first() == null
            && Objects.equals(list.last(), 3)
            && list.toString().equals(
                "null null 4 1 3 "
            )
        );
    }


    private static boolean testNoNulls() {

        DoublyLinkedList<Integer> list =
            new DoublyLinkedList<>();

        list.addLast(7);
        list.addLast(8);
        list.addLast(9);

        list.group();

        return (
            list.size() == 3
            && Objects.equals(list.first(), 7)
            && Objects.equals(list.last(), 9)
            && list.toString().equals("7 8 9 ")
        );
    }


    private static boolean testAllNulls() {

        DoublyLinkedList<Integer> list =
            new DoublyLinkedList<>();

        list.addLast(null);
        list.addLast(null);
        list.addLast(null);

        list.group();

        return (
            list.size() == 3
            && list.first() == null
            && list.last() == null
            && list.toString().equals(
                "null null null "
            )
        );
    }


    private static boolean testNullsAtEnds() {

        DoublyLinkedList<Integer> list =
            new DoublyLinkedList<>();

        list.addLast(null);
        list.addLast(5);
        list.addLast(6);
        list.addLast(null);

        list.group();

        return (
            list.size() == 4
            && list.first() == null
            && Objects.equals(list.last(), 6)
            && list.toString().equals(
                "null null 5 6 "
            )
        );
    }
}