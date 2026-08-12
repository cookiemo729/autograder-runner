import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class HiddenTest {

    public static void main(String[] args) {

        if (args.length != 1) {
            System.exit(2);
        }

        boolean passed;

        switch (args[0]) {

            case "max_basic":
                passed = testMaxBasic();
                break;

            case "duplicates_basic":
                passed = testDuplicatesBasic();
                break;

            case "unique_basic":
                passed = testUniqueBasic();
                break;

            case "hidden_case":
                passed = testHiddenCase();
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


    private static boolean testMaxBasic() {

        Integer[] input = {
            7, 2, 11, 4, 3
        };

        return NumbersArray.findMax(input) == 11;
    }


    private static boolean testDuplicatesBasic() {

        Integer[] input = {
            1, 2, 3, 2, 4, 1, 5
        };

        Integer[] actual =
            NumbersArray.findDuplicates(input);

        return sameValues(
            actual,
            new Integer[]{1, 2}
        );
    }


    private static boolean testUniqueBasic() {

        Integer[] input = {
            1, 2, 3, 2, 4, 1, 5
        };

        Integer[] actual =
            NumbersArray.findUnique(input);

        return sameValues(
            actual,
            new Integer[]{3, 4, 5}
        );
    }


    private static boolean testHiddenCase() {

        Integer[] input = {
            20, 7, 20, 8, 9, 8, 11, 12
        };

        boolean maxCorrect =
            NumbersArray.findMax(input) == 20;

        boolean duplicatesCorrect =
            sameValues(
                NumbersArray.findDuplicates(input),
                new Integer[]{20, 8}
            );

        boolean uniqueCorrect =
            sameValues(
                NumbersArray.findUnique(input),
                new Integer[]{7, 9, 11, 12}
            );

        return (
            maxCorrect
            && duplicatesCorrect
            && uniqueCorrect
        );
    }


    private static boolean sameValues(
        Integer[] actual,
        Integer[] expected
    ) {

        if (actual == null) {
            return false;
        }

        Set<Integer> actualSet =
            new HashSet<>(
                Arrays.asList(actual)
            );

        Set<Integer> expectedSet =
            new HashSet<>(
                Arrays.asList(expected)
            );

        return (
            actual.length == expected.length
            && actualSet.equals(expectedSet)
        );
    }
}