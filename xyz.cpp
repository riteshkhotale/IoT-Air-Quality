#include <iostream>
using namespace std;

#define MAX 5

class PriorityQueue {
    int data[MAX];
    int priority[MAX];
    int size;

public:
    PriorityQueue() {
        size = 0;
    }

    void insert(int value, int pr) {
        if (size == MAX) {
            cout << "Queue is Full\n";
            return;
        }

        int i = size - 1;
        while (i >= 0 && priority[i] > pr) {
            data[i + 1] = data[i];
            priority[i + 1] = priority[i];
            i--;
        }

        data[i + 1] = value;
        priority[i + 1] = pr;
        size++;
    }

    void remove() {
        if (size == 0) {
            cout << "Queue is Empty\n";
            return;
        }

        cout << "Removed element: " << data[0] << endl;

        for (int i = 0; i < size - 1; i++) {
            data[i] = data[i + 1];
            priority[i] = priority[i + 1];
        }

        size--;
    }

    void display() {
        if (size == 0) {
            cout << "Queue is Empty\n";
            return;
        }

        cout << "Element\tPriority\n";
        for (int i = 0; i < size; i++) {
            cout << data[i] << "\t" << priority[i] << endl;
        }
    }
};

int main() {
    PriorityQueue pq;

    pq.insert(101, 2);
    pq.insert(102, 1);
    pq.insert(103, 3);

    cout << "Priority Queue:\n";
    pq.display();

    pq.remove();

    cout << "\nAfter Deletion:\n";
    pq.display();

    return 0;
}