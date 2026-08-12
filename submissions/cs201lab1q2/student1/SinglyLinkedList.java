import java.util.*;

public class SinglyLinkedList<E extends Comparable<E>> {
    private Node<E> head = null;
    private Node<E> tail = null;
    private int size = 0;

    public SinglyLinkedList(){

    }

    public int size(){
        return size;
    }

    public boolean isEmpty(){
        return size == 0;
    }

    public E first(){
        if (isEmpty()){
            return null;
        } 
        return head.getElement();
    }

    public E last(){
        if (isEmpty()){
            return null;
        }
        return tail.getElement();
    }

    public void addFirst(E e){
        head = new Node<>(e, head);

        if (isEmpty()){
            tail = head;
        }
        size++;
    }

    public void addLast(E e){
        Node<E> newest = new Node<>(e, null);
        if (isEmpty()){
            head = newest;
        } else {
            tail.setNext(newest);
        }
        tail = newest;
        size++;
    }

    public E removeFirst(){
        if (isEmpty()){
            return null;
        }

        E answer = head.getElement();
        head = head.getNext();
        size--;

        if (isEmpty()){
            tail = null;
        }
        return answer;
    }

    /*************************************/
    public String toString(){
        String result = "";
        if (isEmpty()){
            return result;
        }

        Node<E> current = head;
        while (current != null){
            result += current.getElement();
            current = current.getNext();
        }
        return result;
    }

    public E removeLast(){
        if (isEmpty()){
            return null;
        }

        Node<E> last = tail;
        
        if (head == tail){
            head = null;
            tail = null;
            size--;
            return last.getElement();
        }

        Node<E> current = head;
        while (current.getNext() != tail){
            current = current.getNext();
        }
        current.setNext(null);
        tail = current;
        size--;
        return last.getElement();
    }

    public void reverse(){      
        Node<E> previous = null; 
        Node<E> current = head; 
        Node<E> next = null; 
        
        tail = head; 
        while (current != null) {
			next = current.getNext(); 
			current.setNext(previous); 
			previous = current; 
			current = next; 
        }
        head = previous; 
    }
}