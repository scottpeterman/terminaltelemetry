# key_handler.py

class KeyHandler:
    @staticmethod
    def send(string, ssh_connection):

        if "\n" in string:
            lines = string.splitlines()
            for line in lines:
                ssh_connection.send_command(line)
                ssh_connection.send_command("\n")
        else:
            ssh_connection.send_command(string)

    @staticmethod
    def handle_key(event, ssh_connection):
        """
        Handle the key press event and send appropriate command to SSH.

        :param event: Key press event.
        :param ssh_connection: SSHConnection object to send commands to.
        """
        keysym = event.keysym
        char = event.char

        # Mapping of special keys to their corresponding escape sequences
        special_keys = {
            "Return": "\r",
            "BackSpace": "\b",
            "Escape": "\x1b",
            "Up": "\x1b[A",
            "Down": "\x1b[B",
            "Right": "\x1b[C",
            "Left": "\x1b[D",
            "F1": "\x1bOP",
            "F2": "\x1bOQ",
            "F3": "\x1bOR",
            "F4": "\x1bOS",
            "F5": "\x1b[15~",
            "F6": "\x1b[17~",
            "F7": "\x1b[18~",
            "F8": "\x1b[19~",
            "F9": "\x1b[20~",
            "F10": "\x1b[21~",
            "F11": "\x1b[23~",
            "F12": "\x1b[24~",
            "Insert": "\x1b[2~",
            "Delete": "\x1b[3~",
            "Home": "\x1b[H",
            "End": "\x1b[F",
            "PageUp": "\x1b[5~",
            "PageDown": "\x1b[6~",
            # Additional mappings can be added here
        }

        # Check if the key is a special key
        if keysym in special_keys:
            ssh_connection.send_command(special_keys[keysym])
        elif char:
            # Send the character if it's a regular key
            ssh_connection.send_command(char)

        return "break"
