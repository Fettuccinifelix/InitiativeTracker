from pirc522 import RFID
import RPi.GPIO as GPIO
import json
from lib import Initialization_Mode, detect_button_press, initialize_combat, run_combat
from classes import CircularLinkedList
import asyncio

INPUT_PIN = 10
              
async def main_loop():
    """Main program loop."""
    rfid = RFID()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        mode = input("Select mode: [1] Normal  [2] Initialization\n>> ").strip()

        if mode == "2":
            Initialization_Mode(rfid)
            return

        entity_dict = json.load(open("entities.json"))
        combat_order = CircularLinkedList()

        while True:
            print("Press the button to start combat...")
            await detect_button_press(INPUT_PIN)

            await initialize_combat(rfid, entity_dict, combat_order)
            await run_combat(combat_order)

    finally:
        rfid.cleanup()
        GPIO.cleanup()

if __name__ == "__main__":
    asyncio.run(main_loop())