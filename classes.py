class Entity: 
    def __init__(self, name, entity_tag):
        self.name = name
        self.entity_tag = entity_tag

    def __str__(self):
        return f"Entity(name={self.name}, uid={self.entity_tag})"

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class CircularLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            new_node.next = new_node
            self.head = new_node
        else:
            current = self.head
            while current.next != self.head:
                current = current.next
            current.next = new_node
            new_node.next = self.head