public class HiddenTest {

    public static void main(String[] args) {

        if (args.length != 1) {
            System.exit(2);
        }

        boolean passed;

        switch (args[0]) {

            case "invalid_different_nodes":
                passed =
                    testInvalidDifferentNodes();
                break;

            case "inorder_pre_post":
                passed =
                    testInorderPrePost();
                break;

            case "invalid_combination":
                passed =
                    testInvalidCombination();
                break;

            case "pre_post_in":
                passed =
                    testPrePostIn();
                break;

            case "larger_valid":
                passed =
                    testLargerValid();
                break;

            case "hidden_balanced":
                passed =
                    testHiddenBalanced();
                break;

            case "hidden_permuted":
                passed =
                    testHiddenPermuted();
                break;

            case "hidden_invalid":
                passed =
                    testHiddenInvalid();
                break;

            default:
                System.exit(2);
                return;
        }

        System.out.print(
            passed ? "PASS" : "FAIL"
        );

        System.exit(
            passed ? 0 : 1
        );
    }


    private static boolean
    testInvalidDifferentNodes() {

        String actual =
            Q1Test.verify(
                "1-2",
                "2-1-3",
                "1-3-2"
            );

        return actual.equals(
            "Invalid traversals"
        );
    }


    private static boolean
    testInorderPrePost() {

        String actual =
            Q1Test.verify(
                "1-2-3",
                "2-1-3",
                "1-3-2"
            );

        return actual.equals(
            "Traversal 1 - Inorder, "
            + "Traversal 2 - Preorder, "
            + "Traversal 3 - Postorder"
        );
    }


    private static boolean
    testInvalidCombination() {

        String actual =
            Q1Test.verify(
                "1-2-3",
                "3-2-1",
                "2-3-1"
            );

        return actual.equals(
            "Invalid traversals"
        );
    }


    private static boolean
    testPrePostIn() {

        String actual =
            Q1Test.verify(
                "3-1-2-5-4",
                "2-1-4-5-3",
                "1-2-3-4-5"
            );

        return actual.equals(
            "Traversal 1 - Preorder, "
            + "Traversal 2 - Postorder, "
            + "Traversal 3 - Inorder"
        );
    }


    private static boolean
    testLargerValid() {

        String actual =
            Q1Test.verify(
                "10-20-30-40-50",
                "20-10-30-40-50",
                "10-50-40-30-20"
            );

        return actual.equals(
            "Traversal 1 - Inorder, "
            + "Traversal 2 - Preorder, "
            + "Traversal 3 - Postorder"
        );
    }


    private static boolean
    testHiddenBalanced() {

        /*
         * BST:
         *
         *        40
         *      /    \
         *    20      60
         *   /  \    /  \
         * 10   30  50  70
         */

        String actual =
            Q1Test.verify(
                "10-20-30-40-50-60-70",
                "40-20-10-30-60-50-70",
                "10-30-20-50-70-60-40"
            );

        return actual.equals(
            "Traversal 1 - Inorder, "
            + "Traversal 2 - Preorder, "
            + "Traversal 3 - Postorder"
        );
    }


    private static boolean
    testHiddenPermuted() {

        /*
         * Same BST, but input order is:
         * postorder, inorder, preorder.
         */

        String actual =
            Q1Test.verify(
                "10-30-20-50-70-60-40",
                "10-20-30-40-50-60-70",
                "40-20-10-30-60-50-70"
            );

        return actual.equals(
            "Traversal 1 - Postorder, "
            + "Traversal 2 - Inorder, "
            + "Traversal 3 - Preorder"
        );
    }


    private static boolean
    testHiddenInvalid() {

        String actual =
            Q1Test.verify(
                "10-20-30-40-50",
                "30-10-20-40-50",
                "10-20-50-40-30"
            );

        return actual.equals(
            "Invalid traversals"
        );
    }
}