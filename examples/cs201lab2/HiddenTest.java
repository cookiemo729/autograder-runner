import java.util.*;

public class HiddenTest {

    public static void main(String[] args) {

        if (args.length != 1) {
            System.exit(2);
        }

        boolean passed;

        switch (args[0]) {

            case "odd_basic":
                passed = testOddBasic();
                break;

            case "even_basic":
                passed = testEvenBasic();
                break;

            case "double_values":
                passed = testDoubleValues();
                break;

            case "ascending_large":
                passed = testAscendingLarge();
                break;

            case "descending_large":
                passed = testDescendingLarge();
                break;

            case "random_large_1":
                passed = testRandomLarge1();
                break;

            case "random_large_2":
                passed = testRandomLarge2();
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


    private static boolean testOddBasic() {

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        list.addLast(3);
        list.addLast(2);
        list.addLast(1);

        list.swap();

        return (
            list.size() == 3
            && Objects.equals(list.first(), 1)
            && Objects.equals(list.last(), 3)
            && list.toString().equals("1 2 3 ")
        );
    }


    private static boolean testEvenBasic() {

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        list.addLast(5);
        list.addLast(1);
        list.addLast(2);
        list.addLast(3);

        list.swap();

        return (
            list.size() == 4
            && Objects.equals(list.first(), 1)
            && Objects.equals(list.last(), 2)
            && list.toString().equals("1 5 3 2 ")
        );
    }


    private static boolean testDoubleValues() {

        SinglyLinkedList<Double> list =
            new SinglyLinkedList<>();

        list.addLast(5.0);
        list.addLast(3.0);
        list.addLast(4.0);
        list.addLast(1.0);
        list.addLast(2.0);

        list.swap();

        return (
            list.size() == 5
            && Objects.equals(list.first(), 1.0)
            && Objects.equals(list.last(), 4.0)
            && list.toString().equals(
                "1.0 3.0 2.0 5.0 4.0 "
            )
        );
    }


    private static boolean testAscendingLarge() {

        final int n = 50000;

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        for (int i = 1; i <= n; i++) {
            list.addLast(i);
        }

        long start = System.nanoTime();

        list.swap();

        long elapsed =
            System.nanoTime() - start;

        printTiming(
            "ascending_large",
            elapsed
        );

        return (
            list.size() == n
            && Objects.equals(list.first(), n)
            && Objects.equals(list.last(), 1)
            && validateMappedSequence(
                list,
                n,
                i -> n + 1 - i
            )
        );
    }


    private static boolean testDescendingLarge() {

        final int n = 50000;

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        for (int i = n; i >= 1; i--) {
            list.addLast(i);
        }

        long start = System.nanoTime();

        list.swap();

        long elapsed =
            System.nanoTime() - start;

        printTiming(
            "descending_large",
            elapsed
        );

        return (
            list.size() == n
            && Objects.equals(list.first(), 1)
            && Objects.equals(list.last(), n)
            && validateDescendingMappedSequence(
                list,
                n
            )
        );
    }


    private static boolean testRandomLarge1() {

        final int n = 50000;

        int[] data = createRandomPermutation(
            n,
            12345L
        );

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        for (int value : data) {
            list.addLast(value);
        }

        int[] expected =
            expectedSwap(data);

        long start = System.nanoTime();

        list.swap();

        long elapsed =
            System.nanoTime() - start;

        printTiming(
            "random_large_1",
            elapsed
        );

        return validateAgainstExpected(
            list,
            expected
        );
    }


    private static boolean testRandomLarge2() {

        final int n = 50000;

        int[] data = createRandomPermutation(
            n,
            98765L
        );

        SinglyLinkedList<Integer> list =
            new SinglyLinkedList<>();

        for (int value : data) {
            list.addLast(value);
        }

        int[] expected =
            expectedSwap(data);

        long start = System.nanoTime();

        list.swap();

        long elapsed =
            System.nanoTime() - start;

        printTiming(
            "random_large_2",
            elapsed
        );

        return validateAgainstExpected(
            list,
            expected
        );
    }


    private static int[] createRandomPermutation(
        int n,
        long seed
    ) {

        List<Integer> values =
            new ArrayList<>();

        for (int i = 1; i <= n; i++) {
            values.add(i);
        }

        Collections.shuffle(
            values,
            new Random(seed)
        );

        int[] result = new int[n];

        for (int i = 0; i < n; i++) {
            result[i] = values.get(i);
        }

        return result;
    }


    private static int[] expectedSwap(
        int[] original
    ) {

        int n = original.length;

        int[] expected =
            new int[n];

        for (int i = 0; i < n; i++) {

            expected[i] =
                n + 1 - original[i];
        }

        return expected;
    }


    private static boolean validateAgainstExpected(
        SinglyLinkedList<Integer> list,
        int[] expected
    ) {

        String[] actual =
            list.toString()
                .trim()
                .split("\\s+");

        if (actual.length != expected.length) {
            return false;
        }

        for (int i = 0; i < expected.length; i++) {

            if (
                Integer.parseInt(actual[i])
                != expected[i]
            ) {
                return false;
            }
        }

        return true;
    }


    private static boolean validateMappedSequence(
        SinglyLinkedList<Integer> list,
        int n,
        java.util.function.IntUnaryOperator mapper
    ) {

        String[] actual =
            list.toString()
                .trim()
                .split("\\s+");

        if (actual.length != n) {
            return false;
        }

        for (int i = 1; i <= n; i++) {

            int expected =
                mapper.applyAsInt(i);

            int actualValue =
                Integer.parseInt(
                    actual[i - 1]
                );

            if (actualValue != expected) {
                return false;
            }
        }

        return true;
    }


    private static boolean validateDescendingMappedSequence(
        SinglyLinkedList<Integer> list,
        int n
    ) {

        String[] actual =
            list.toString()
                .trim()
                .split("\\s+");

        if (actual.length != n) {
            return false;
        }

        for (int i = 0; i < n; i++) {

            int expected = i + 1;

            int actualValue =
                Integer.parseInt(
                    actual[i]
                );

            if (actualValue != expected) {
                return false;
            }
        }

        return true;
    }


    private static void printTiming(
        String testName,
        long elapsedNanoseconds
    ) {

        double elapsedMs =
            elapsedNanoseconds
            / 1_000_000.0;

        System.err.printf(
            "%s runtime: %.3f ms%n",
            testName,
            elapsedMs
        );
    }
}