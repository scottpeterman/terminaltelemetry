class KeyHandler:
    @staticmethod
    def send(string, serial_connection):
        # Convert the string to bytes and send it to the serial port
        if serial_connection:
            serial_connection.write(string.encode())

    @staticmethod
    def handle_key(event, serial_connection):
        """
        Handle the key press event and send appropriate command to the serial port.

        :param event: Key press event.
        :param serial_connection: serial.Serial object to send data to.
        """
        keysym = event.keysym
        char = event.char

        # Mapping of special keys to their corresponding control characters
        special_keys = {
            "Return": "\r",
            "BackSpace": "\b",
            "Escape": "\x1b",
            "Up": "\x1b[A",
            "Down": "\x1b[B",
            "Right": "\x1b[C",
            "Left": "\x1b[D",
            # Add more if needed for your application
            # "F1": "\x1bOP",  # Example for F1 key
            # ... other function keys ...
        }

        # Check if the key is a special key
        if keysym in special_keys:
            KeyHandler.send(special_keys[keysym], serial_connection)
        elif char:
            # Send the character if it's a regular key
            KeyHandler.send(char, serial_connection)

        return "break"
