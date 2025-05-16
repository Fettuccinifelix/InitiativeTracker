from pirc522 import RFID
import RPi.GPIO as GPIO
import asyncio
from classes import Entity

INPUT_PIN = 10

def Initialization_Mode(rfid): # to be changed
    print("=== Initialization Mode ===")
    print("Scan a tag to write a name to block 10.")
    print("Press Ctrl+C or type 'exit' when prompted to stop.\n")

    try:
        while True:
            print("Waiting for tag...")
            rfid.wait_for_tag()
            (error, tag_type) = rfid.request()
            if not error:
                print(f"Tag detected: {tag_type}")
                (error, uid) = rfid.anticoll()
                if not error:
                    print(f"UID: {uid}")
                    if not rfid.select_tag(uid):
                        # Authenticate with default Key A
                        if not rfid.card_auth(rfid.auth_a, 10, [0xFF]*6, uid):
                            name = input("Enter name to write to tag (or type 'exit' to quit):\n>> ").strip()
                            if name.lower() == 'exit':
                                rfid.stop_crypto()
                                print("Exiting Initialization Mode.")
                                break

                            data = [ord(c) for c in name.ljust(16)[:16]]  # pad/truncate to 16 bytes
                            rfid.write(10, data)
                            rfid.stop_crypto()
                            print(f"✅ Written '{name}' to block 10 of tag.\n")
                        else:
                            print("❌ Authentication failed.\n")
                    else:
                        print("❌ Tag selection failed.\n")
                else:
                    print("❌ Error reading UID.\n")
            else:
                print("❌ No tag detected.\n")

    except KeyboardInterrupt:
        print("\nExiting Initialization Mode.")
        rfid.stop_crypto()


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
                # Auth for block 10 (block 2 of sector 2) using default shipping key A
                if not rfid.card_auth(rfid.auth_a, 10, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid): # this is good
                    block_data= rfid.read(10)

                    matched_name = ""

                    for key, tag in entity_dict.items():
                        if tag == block_data:
                            matched_name = key
                            break  

                    scanned_entity = Entity(name=matched_name, entity_tag=block_data)
                    
                    print(f"Scanned entity: {scanned_entity.name}")
                    rfid.stop_crypto()
                    return scanned_entity
                
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