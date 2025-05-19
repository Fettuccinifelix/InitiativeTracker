class Entity:
    def __init__(self, name, creature_type, alignment, hit_points, armor_class, speed, challenge_rating, actions, traits):
        self.name = name
        self.creature_type = creature_type
        self.alignment = alignment
        self.hit_points = hit_points
        self.armor_class = armor_class
        self.speed = speed
        self.challenge_rating = challenge_rating
        self.actions = actions
        self.traits = traits

    def __str__(self):
        return (f"Entity(name={self.name}, uid={self.entity_tag}, type={self.creature_type}, "
                f"alignment={self.alignment}, hp={self.hit_points}, ac={self.armor_class}, "
                f"speed={self.speed}, cr={self.challenge_rating}, actions={self.actions}, traits={self.traits})")
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