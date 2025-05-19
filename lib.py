from pirc522 import RFID
import RPi.GPIO as GPIO
import asyncio
from classes import Entity

INPUT_PIN = 10

def Initialization_Mode(rfid):
    """Mode to write a name to an RFID tag using blocks 9, 10, 11."""
    print("=== Initialization Mode ===")
    print("Scan a tag to write a name to it (stored in blocks 9, 10, and 11).")
    print("Press Ctrl+C or type 'exit' when prompted to stop.\n")

    try:
        while True:
            print("Waiting for tag...")
            rfid.wait_for_tag()
            (error, tag_type) = rfid.request()
            if error:
                print("No tag detected.\n")
                continue

            print(f"Tag detected: {tag_type}")
            (error, uid) = rfid.anticoll()
            if error:
                print("Error reading UID.\n")
                continue

            print(f"UID: {uid}")
            if rfid.select_tag(uid):
                print("Tag selection failed.\n")
                continue

            # Try authentication with Key A first
            success = write_name_to_tag(rfid, uid, rfid.auth_a)
            if success is False:
                # If Key A failed or user exited, try Key B
                success = write_name_to_tag(rfid, uid, rfid.auth_b)

            if success is False:
                print("Failed to write to tag after trying both Key A and B.\n")
            # If success is True, loop continues automatically

    except KeyboardInterrupt:
        print("\nExiting Initialization Mode.")
        rfid.stop_crypto()

def write_name_to_tag(rfid, uid, auth_method):
    """Helper function to write a name to an RFID tag across 3 blocks (9, 10, 11)."""
    name = input("Enter name to write to tag (or type 'exit' to quit):\n>> ").strip()
    
    if name.lower() == 'exit':
        print("Exiting Initialization Mode.")
        return False  # Signal to exit the loop

    if len(name) > 48:
        print("Name too long. Maximum is 48 characters.")
        return True  # Continue loop to prompt again

    # Pad/truncate the name to exactly 48 bytes
    name = name.ljust(48)[:48]

    # Split into 3 blocks of 16 bytes each
    block_data = [ [ord(c) for c in name[i:i+16]] for i in range(0, 48, 16) ]
    blocks = [9, 10, 11]

    for block, data in zip(blocks, block_data):
        if rfid.card_auth(auth_method, block, [0xFF]*6, uid):
            print(f"Authentication failed for block {block}.")
            rfid.stop_crypto()
            return False
        rfid.write(block, data)
        rfid.stop_crypto()

    print(f"Successfully written '{name.strip()}' to blocks 9, 10, and 11.\n")
    return True  # Success


def Get_Tag_Input(rfid, entity_dict):
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
                # Authenticate with default Key A for block 9 (to read 9,10,11)
                if not rfid.card_auth(rfid.auth_a, 9, [0xFF]*6, uid):
                    try:
                        data9 = rfid.read(9)
                        data10 = rfid.read(10)
                        data11 = rfid.read(11)

                        full_data = data9 + data10 + data11
                        matched_creature = next(
                            (creature for creature in entity_dict["creatures"] if creature["name"] == full_data),
                            None
                        )

                        if matched_creature:
                            print(f"Matched creature: {matched_creature}")
                            scanned_entity = Entity(
                                name=matched_creature["name"],
                                type=matched_creature["type"],
                                alignment=matched_creature["alignment"],
                                hit_points=matched_creature["hit_points"],
                                speed=matched_creature["speed"],
                                challenge_rating=matched_creature["challenge_rating"],
                                actions=matched_creature.get("actions", []),
                                traits=matched_creature.get("traits", []),
                            )
                        else:
                            print("No matching creature found.")
                            scanned_entity = None

                        return scanned_entity
                    finally:
                        rfid.stop_crypto()
                else:
                    print("Authentication failed.")
            else:
                print("Tag selection failed.")
        else:
            print("Error reading UID.")
    else:
        print("No tag detected.")

    return None

                
async def detect_button_press(pin):
    while GPIO.input(pin) == GPIO.LOW:
        await asyncio.sleep(0.1)
    return True

async def initialize_combat(rfid, entity_dict, combat_order):
    creature_list = []
    print("Starting Combat, scan minis using the RFID reader...")
    print("Place your RFID card near the reader...")

    while True:
        if GPIO.input(INPUT_PIN) == GPIO.HIGH:
            entity = Get_Tag_Input(rfid, entity_dict)
            if entity:
                creature_list.append(entity)
                print(f"Added {entity.name} to the combat order.")
        else:
            print("Combat order completed. Are you sure? (y/n)")
            confirmation = input(">> ").strip().lower()
            if confirmation == 'y':
                for entity in creature_list:
                    combat_order.append(entity)
                break
            else:
                print("Resuming entity scanning...")

async def run_combat(combat_order):
    print("Combat started!")
    combat_in_progress = True
    entity_iterator = combat_order.traverse()

    while combat_in_progress:
        entity = next(entity_iterator)
        print(f"It's {entity.name}'s turn!")
        print("Press the button to end the turn...")
        await detect_button_press(INPUT_PIN)

        print("Press the button again to exit combat or wait for the next turn...")
        if GPIO.input(INPUT_PIN) == GPIO.HIGH:
            combat_in_progress = False
            print("Exiting combat...")
            break