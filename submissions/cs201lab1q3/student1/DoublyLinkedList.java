import java.util.ArrayList;
import java.util.List;

public class DoublyLinkedList<E> {

    private static class Node<E> {
        private E element;
        private Node<E> prev;
        private Node<E> next;
    
        public Node(E e, Node<E> p, Node<E> n){
            element = e;
            prev = p;
            next = n;
        }
    
        public E getElement(){
            return element;
        }
    
        public Node<E> getNext(){
            return next;
        }

        public Node<E> getPrev(){
            return prev;
        }
    
        public void setNext(Node<E> n){
            next = n;
        }

        public void setPrev(Node<E> p){
            prev = p;
        }
    }

    private Node<E> header;
    private Node<E> trailer;
    private int size = 0;

    public DoublyLinkedList(){
        header = new Node<>(null, null, null);
        trailer = new Node<>(null, header, null);
        header.setNext(trailer);
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
        return header.getNext().getElement();
    }

    public E last(){
        if (isEmpty()){
            return null;
        }
        return trailer.getPrev().getElement();
    }

    public void addFirst(E e){
        addBetween(e, header, header.getNext());
    }

    public void addLast(E e){
        addBetween(e, trailer.getPrev(), trailer);
    }

    public E removeFirst(){
        if (isEmpty()){
            return null;
        }
        return remove(header.getNext());
    }

    public E removeLast(){
        if (isEmpty()){
            return null;
        }
        return remove(trailer.getPrev());
    }

    private void addBetween(E e, Node<E> predecessor, Node<E> successor){
        Node<E> newest = new Node<>(e, predecessor, successor);
        predecessor.setNext(newest);
        successor.setPrev(newest);
        size++;
    }

    private E remove(Node<E> node){
        Node<E> predecessor = node.getPrev();
        Node<E> successor = node.getNext();

        predecessor.setNext(successor);
        successor.setPrev(predecessor);
        size--;
        return node.getElement();        
    }

    public String toString(){
        StringBuilder sb = new StringBuilder();
        Node<E> current = header.getNext();
        while (current != trailer) {
            sb.append(current.getElement());
            sb.append(" ");
            current = current.getNext();
        }
        return sb.toString();
    }

    public void group(){
        Node<E> current = header.getNext();
        List<E> holder = new ArrayList<>();
        while(current != trailer){
            if(current.getElement()!=null){ //get all non null values
                holder.add(current.getElement());
            }
            current = current.getNext();
        }
        current = header;
        int numberOfNulls = size -  holder.size();
        while(numberOfNulls != 0){ //adds all the null values. 
            current.setNext(new Node<>(null, current, null));
            current = current.getNext();
            numberOfNulls --;
        }
        int count = 0;
        while(count != holder.size()){ //adds all the non null values. 
            Node<E> newest = new Node<>(holder.get(count), current, null);
            current.setNext(newest);
            current = newest;
            count++;
        }
        current.setNext(new Node<>(null, current, trailer)); // set the next for current to be the trailer
        trailer.setPrev(current); // set the trailer's prev node to be the current
        trailer = current.getNext(); // set the trailer
    }
}