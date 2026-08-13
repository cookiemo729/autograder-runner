import java.util.*;

public class Q1Test {

    public static void main(String[] args) {

        String result, traversal1, traversal2, traversal3;

        traversal1 = "1-2";
        traversal2 = "2-1-3";
        traversal3 = "1-3-2";

        result = verify(
            traversal1,
            traversal2,
            traversal3
        );

        System.out.println(
            "Actual Result : " + result
        );

        traversal1 = "1-2-3";
        traversal2 = "2-1-3";
        traversal3 = "1-3-2";

        result = verify(
            traversal1,
            traversal2,
            traversal3
        );

        System.out.println(
            "Actual Result : " + result
        );

        traversal1 = "1-2-3";
        traversal2 = "3-2-1";
        traversal3 = "2-3-1";

        result = verify(
            traversal1,
            traversal2,
            traversal3
        );

        System.out.println(
            "Actual Result : " + result
        );

        traversal1 = "3-1-2-5-4";
        traversal2 = "2-1-4-5-3";
        traversal3 = "1-2-3-4-5";

        result = verify(
            traversal1,
            traversal2,
            traversal3
        );

        System.out.println(
            "Actual Result : " + result
        );

        traversal1 = "10-20-30-40-50";
        traversal2 = "20-10-30-40-50";
        traversal3 = "10-50-40-30-20";

        result = verify(
            traversal1,
            traversal2,
            traversal3
        );

        System.out.println(
            "Actual Result : " + result
        );
    }


    public static String verify(
        String traversal1,
        String traversal2,
        String traversal3
    ) {

        int[] t1 = parse(traversal1);
        int[] t2 = parse(traversal2);
        int[] t3 = parse(traversal3);

        if (
            t1 == null
            || t2 == null
            || t3 == null
        ) {
            return "Invalid traversals";
        }

        if (
            t1.length != t2.length
            || t1.length != t3.length
            || t1.length == 0
        ) {
            return "Invalid traversals";
        }

        if (
            !sameValues(t1, t2)
            || !sameValues(t1, t3)
        ) {
            return "Invalid traversals";
        }

        int[][] traversals = {
            t1,
            t2,
            t3
        };

        /*
         * Try every possible assignment of:
         * inorder, preorder, postorder.
         */
        int[][] permutations = {
            {0, 1, 2},
            {0, 2, 1},
            {1, 0, 2},
            {1, 2, 0},
            {2, 0, 1},
            {2, 1, 0}
        };

        for (int[] p : permutations) {

            int inorderIndex = p[0];
            int preorderIndex = p[1];
            int postorderIndex = p[2];

            int[] inorder =
                traversals[inorderIndex];

            int[] preorder =
                traversals[preorderIndex];

            int[] postorder =
                traversals[postorderIndex];

            if (
                !isStrictlyIncreasing(inorder)
            ) {
                continue;
            }

            Node root =
                buildFromPreorder(
                    preorder
                );

            if (root == null) {
                continue;
            }

            List<Integer> generatedInorder =
                new ArrayList<>();

            List<Integer> generatedPreorder =
                new ArrayList<>();

            List<Integer> generatedPostorder =
                new ArrayList<>();

            inorder(
                root,
                generatedInorder
            );

            preorder(
                root,
                generatedPreorder
            );

            postorder(
                root,
                generatedPostorder
            );

            if (
                matches(
                    generatedInorder,
                    inorder
                )
                && matches(
                    generatedPreorder,
                    preorder
                )
                && matches(
                    generatedPostorder,
                    postorder
                )
            ) {

                String[] names = new String[3];

                names[inorderIndex] =
                    "Inorder";

                names[preorderIndex] =
                    "Preorder";

                names[postorderIndex] =
                    "Postorder";

                return (
                    "Traversal 1 - "
                    + names[0]
                    + ", Traversal 2 - "
                    + names[1]
                    + ", Traversal 3 - "
                    + names[2]
                );
            }
        }

        return "Invalid traversals";
    }


    private static int[] parse(
        String traversal
    ) {

        if (
            traversal == null
            || traversal.trim().isEmpty()
        ) {
            return null;
        }

        try {

            String[] parts =
                traversal.split("-");

            int[] values =
                new int[parts.length];

            Set<Integer> seen =
                new HashSet<>();

            for (
                int i = 0;
                i < parts.length;
                i++
            ) {

                values[i] =
                    Integer.parseInt(
                        parts[i].trim()
                    );

                if (!seen.add(values[i])) {
                    return null;
                }
            }

            return values;

        } catch (
            NumberFormatException exception
        ) {
            return null;
        }
    }


    private static boolean sameValues(
        int[] a,
        int[] b
    ) {

        Set<Integer> first =
            new HashSet<>();

        Set<Integer> second =
            new HashSet<>();

        for (int value : a) {
            first.add(value);
        }

        for (int value : b) {
            second.add(value);
        }

        return first.equals(second);
    }


    private static boolean
    isStrictlyIncreasing(
        int[] values
    ) {

        for (
            int i = 1;
            i < values.length;
            i++
        ) {

            if (
                values[i]
                <= values[i - 1]
            ) {
                return false;
            }
        }

        return true;
    }


    private static Node buildFromPreorder(
        int[] preorder
    ) {

        Node root = null;

        for (int value : preorder) {

            root = insert(
                root,
                value
            );
        }

        return root;
    }


    private static Node insert(
        Node root,
        int value
    ) {

        if (root == null) {
            return new Node(value);
        }

        if (value < root.value) {

            root.left =
                insert(
                    root.left,
                    value
                );

        } else if (value > root.value) {

            root.right =
                insert(
                    root.right,
                    value
                );
        }

        return root;
    }


    private static void inorder(
        Node node,
        List<Integer> result
    ) {

        if (node == null) {
            return;
        }

        inorder(
            node.left,
            result
        );

        result.add(
            node.value
        );

        inorder(
            node.right,
            result
        );
    }


    private static void preorder(
        Node node,
        List<Integer> result
    ) {

        if (node == null) {
            return;
        }

        result.add(
            node.value
        );

        preorder(
            node.left,
            result
        );

        preorder(
            node.right,
            result
        );
    }


    private static void postorder(
        Node node,
        List<Integer> result
    ) {

        if (node == null) {
            return;
        }

        postorder(
            node.left,
            result
        );

        postorder(
            node.right,
            result
        );

        result.add(
            node.value
        );
    }


    private static boolean matches(
        List<Integer> actual,
        int[] expected
    ) {

        if (
            actual.size()
            != expected.length
        ) {
            return false;
        }

        for (
            int i = 0;
            i < expected.length;
            i++
        ) {

            if (
                actual.get(i)
                != expected[i]
            ) {
                return false;
            }
        }

        return true;
    }


    private static class Node {

        int value;
        Node left;
        Node right;

        Node(int value) {
            this.value = value;
        }
    }
}