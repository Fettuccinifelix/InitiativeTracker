from pirc522 import RFID

def main():
    entity_dict = {
        "entity1": [72, 101, 108, 108, 111, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "entity2": [72, 101, 108, 108, 111, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "entity3": [72, 101, 108, 108, 111, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    } # stick this in a json somewhere

    # Initialize RFID reader
    rfid = RFID()

    combatOrder = CircularLinkedList()
    startCombat = False
    creatureList = []
    firstLoop = True    

    while True:
        if startCombat and firstLoop: # Replace with actual button press detection logic
                print("Starting Combat, scan minis using the RFID reader...")
                print("Place your RFID card near the reader...")
                orderingDone = False
                ## orderingDone button logic placeholder
                button_pressed = False  # Replace with actual button press detection logic
                if button_pressed:
                    orderingDone = True
                    print("Combat order completed.") # add "are you sure?" prompt
                    for entity in creatureList:
                        combatOrder.append(entity)
                        print(entity.name)
                    firstLoop = False
                    rfid.cleanup()

                while not orderingDone:
                    # Wait for a card to be detected
                    rfid.wait_for_tag()

                    # Request the tag
                    (error, tag_type) = rfid.request()
                    if not error:
                        print(f"Tag detected: {tag_type}")

                        # Get the UID of the tag
                        (error, uid) = rfid.anticoll()
                        if not error:
                            print(f"UID: {uid}")
                            # Select Tag is required before Auth
                            if not rfid.select_tag(uid):
                                # Auth for block 10 (block 2 of sector 2) using default shipping key A
                                if not rfid.card_auth(rfid.auth_a, 10, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid): # this is good
                                    block_data= rfid.read(10)

                                    # Assume we haven't found a matching entity yet
                                    matched_name = ""

                                    # Loop through the entity_dict
                                    for key, tag in entity_dict.items():
                                        if tag == block_data:
                                            matched_name = key
                                            break  # Found a match, no need to keep looking

                                    # Now create the new Entity
                                    scanned_entity = Entity(name=matched_name, entity_tag=block_data)
                                    creatureList.append(scanned_entity)
                                    
                                    print(f"Scanned entity: {scanned_entity.name}")
                                    # Always stop crypto1 when done working
                                    rfid.stop_crypto()
        elif startCombat and not firstLoop: # Replace with actual button press detection logic
            combatInProgress = True
            while combatInProgress:
                #press button to exit combat
                button_pressed1 = False  # Replace with actual button press detection logic
                if button_pressed1:
                    combatInProgress = False
                    print("Exiting combat...")
                    # play victory music
                    break

                entity = combatOrder.traverse()
                print(entity.name)
                button_pressed2 = False  # Replace with actual button press detection logic
                # pause until button pressed
                # when button pressed, move to next entity
            
                

if __name__ == "__main__":
    main()

class Entity: 
    def __init__(self, name, entity_tag):
        self.name = name
        self.entity_tag = entity_tag

    def __str__(self):
        return f"Entity(name={self.name}, uid={self.uid})"
    
# Python Program of Traversal of Circular Linked List
class Node:
    def __init__(self, data):
        # Initialize a node with data and next pointer
        self.data = data
        self.next = None

# Circular Linked List class
class CircularLinkedList:
    def __init__(self):
        # Initialize an empty circular linked list with head pointer pointing to None
        self.head = None

    def append(self, data):
        # Append a new node with data to the end of the circular linked list
        new_node = Node(data)
        if not self.head:
            # If the list is empty, make the new node point to itself
            new_node.next = new_node
            self.head = new_node
        else:
            current = self.head
            while current.next != self.head:
                # Traverse the list until the last node
                current = current.next
            # Make the last node point to the new node
            current.next = new_node
            # Make the new node point back to the head
            new_node.next = self.head

    def traverse(self):
        # Traverse and display the elements of the circular linked list
        if not self.head:
            print("Circular Linked List is empty")
            return
        current = self.head
        while True:
            print(current.data, end=" -> ")
            current = current.next
            if current == self.head:
                # Break the loop when we reach the head again
                break