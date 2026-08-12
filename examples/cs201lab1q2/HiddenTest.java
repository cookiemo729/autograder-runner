public class HiddenTest {

    public static void main(String[] args) {

        if (args.length != 1) {
            System.exit(2);
        }

        boolean passed;

        switch (args[0]) {

            case "tostring_basic":
                passed = testToStringBasic();
                break;

            case "remove_last_single":
                passed = testRemoveLastSingle();
                break;

            case "remove_last_multiple":
                passed = testRemoveLastMultiple();
                break;

            case "reverse_basic":
                passed = testReverseBasic();
                break;

            case "reverse_single":
                passed = testReverseSingle();
                break;

            case "reverse_empty":
                passed = testReverseEmpty();
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


    private static boolean testToStringBasic() {

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        list.addLast(7);
        list.addLast(8);
        list.addLast(9);

        return list.toString().equals("789");
    }


    private static boolean testRemoveLastSingle() {

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        list.addLast(42);

        Integer removed = list.removeLast();

        return (
            removed != null
            && removed == 42
            && list.size() == 0
            && list.first() == null
            && list.last() == null
        );
    }


    private static boolean testRemoveLastMultiple() {

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        list.addLast(10);
        list.addLast(20);
        list.addLast(30);

        Integer removed = list.removeLast();

        return (
            removed != null
            && removed == 30
            && list.size() == 2
            && list.first() == 10
            && list.last() == 20
            && list.toString().equals("1020")
        );
    }


    private static boolean testReverseBasic() {

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        list.addLast(1);
        list.addLast(2);
        list.addLast(3);
        list.addLast(4);

        list.reverse();

        return (
            list.size() == 4
            && list.first() == 4
            && list.last() == 1
            && list.toString().equals("4321")
        );
    }


    private static boolean testReverseSingle() {

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        list.addLast(99);

        list.reverse();

        return (
            list.size() == 1
            && list.first() == 99
            && list.last() == 99
            && list.toString().equals("99")
        );
    }


    private static boolean testReverseEmpty() {

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        list.reverse();

        return (
            list.size() == 0
            && list.first() == null
            && list.last() == null
            && list.toString().equals("")
        );
    }
}