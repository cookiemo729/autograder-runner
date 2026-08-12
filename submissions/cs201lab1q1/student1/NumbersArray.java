import java.util.*;

public class NumbersArray {
    public static void main(String[] args) {
        Integer[] input = {1,2,3,4,1,5};

        System.out.println("Input : " + Arrays.toString(input));
        System.out.println("Max number : " + findMax(input));
        System.out.println("Duplicate numbers : " + Arrays.toString(findDuplicates(input)));
        System.out.println("Unique numbers : " + Arrays.toString(findUnique(input)));       
        
        System.out.println();

        input = new Integer[] {1,2,3,4,1,2,5,3};

        System.out.println("Input : " + Arrays.toString(input));
        System.out.println("Max number : " + findMax(input));
        System.out.println("Duplicate numbers : " + Arrays.toString(findDuplicates(input)));
        System.out.println("Unique numbers : " + Arrays.toString(findUnique(input))); 
    }
    
    public static int findMax(Integer[] input){
        int max = input[0];
        for (int i = 1; i < input.length; i++) {
            if (input[i] > max){
                max = input[i];
            }        
        } 
        return max;
    }

    public static int findMax_A(Integer[] input){
        Arrays.sort(input); 
        return input[input.length-1];
    }

    public static Integer[] findDuplicates(Integer[] input){
        ArrayList<Integer> result = new ArrayList<>();
  
        for (int i = 0; i < input.length; i++) {
            for (int j = i + 1 ; j < input.length; j++) { 
                if (input[i] == input[j]){
                    boolean isAdded = false;
                    for (Integer r : result){
                        if (r == input[i]){
                            isAdded = true;
                        }
                    }
                    if (!isAdded){
                        result.add(input[i]);
                    }
                }
            }
        } 
        return result.toArray(new Integer[result.size()]);
    }

    public static Integer[] findDuplicates_A(Integer[] input){
        HashSet<Integer> hs = new HashSet<>();
        ArrayList<Integer> result = new ArrayList<>();
        
        for(Integer i : input){
            if (!hs.add(i)){
                result.add(i);
            }
        }
        return result.toArray(new Integer[result.size()]);
    }

    public static Integer[] findUnique(Integer[] input){
        ArrayList<Integer> result = new ArrayList<>();
        Integer[] duplicates = findDuplicates(input);

        for (int i = 0; i < input.length; i++) {
            boolean isFound = false;
            for (int j = 0  ; j < duplicates.length; j++) { 
                if (input[i] == duplicates[j]){
                    isFound = true;
                    break;
                }
            }
            if (!isFound){
                result.add(input[i]);
            }
        } 
        return result.toArray(new Integer[result.size()]);
    }

    public static Integer[] findUnique_A(Integer[] input){
        HashSet<Integer> numbers = new HashSet<>();
        HashSet<Integer> result = new HashSet<>();

        for(Integer i: input){
            if (numbers.add(i)){
                result.add(i);
            } else {
                result.remove(i);
            }
        }
        return result.toArray(new Integer[result.size()]);
    }
}