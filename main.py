import logging
import rumps
import threading
import time
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flag to indicate if the Quartz framework is available for mouse events
try:
    from Quartz.CoreGraphics import (
        CGEventCreateMouseEvent,
        CGEventPost,
        kCGEventMouseMoved,
        kCGHIDEventTap
    )
    quartz_available = True
    logging.info("Quartz framework is available.")
except ImportError:
    quartz_available = False
    logging.warning("Quartz framework not found. Mouse movement will be disabled.")

# Global flag to control the mouse movement thread
running = False

def move_mouse():
    """
    Moves the mouse cursor slightly at a fixed interval to prevent the system from going idle.
    This function runs in a separate thread.
    """
    logging.info("Mouse movement thread started.")
    while running:
        if quartz_available:
            try:
                # Create a mouse move event
                event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (100, 100), 0)
                # Post the event to the system event queue
                CGEventPost(kCGHIDEventTap, event)
                logging.info("Mouse moved.")
            except Exception as e:
                logging.error(f"Error moving mouse: {e}")
        time.sleep(30) # Wait for 30 seconds before moving the mouse again
        logging.info("Mouse movement thread stopped.")

class StayActiveApp(rumps.App):
    """
    A rumps application that prevents the system from going idle by periodically moving the mouse.
    """
    def __init__(self):
        """
        Initializes the StayActiveApp. Sets up the menu items, icon, and the initial state.
        """
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        super(StayActiveApp, self).__init__("StayActive", icon=icon_path)
        logging.info(f"Application initialized with icon: {icon_path}")

        # Create menu items for starting and stopping the activity
        self.start_item = rumps.MenuItem("Start", callback=self.start_clicked)
        self.stop_item = rumps.MenuItem("Stop", callback=self.stop_clicked)
        self.license_item = rumps.MenuItem("About StayActiveApp", callback=self.show_license)
        # Define the application menu
        self.menu = [self.start_item, self.stop_item, None, self.license_item]

        # Use a timer to ensure the 'Stop' item is disabled after the menu is built.
        # This addresses a potential race condition or initialization order issue.
        self.disable_timer = rumps.Timer(self._disable_stop_item, 0.1)
        self.disable_timer.start()

        self.running_thread = None
        logging.info("Menu items created and timer for disabling 'Stop' started.")

    def _disable_stop_item(self, sender):
        """
        Callback function for the timer to disable the 'Stop' menu item after a short delay.
        Args:
            sender: The rumps.Timer object.
        """
        logging.debug("Disabling stop item")
        self.stop_item.set_callback(None)
        self.disable_timer.stop()
        logging.info("'Stop' menu item disabled.")

    @rumps.notifications
    def notify_user(self, message):
        """
        Displays a rumps notification to the user.
        Args:
            message (str): The message to display in the notification.
        """
        rumps.notification("StayActive", "", message)
        logging.info(f"Notification sent: {message}")
    
    @rumps.clicked("Start")
    def start_clicked(self, _):
        """
        Callback function when the 'Start' menu item is clicked.
        Starts the mouse movement thread and updates the menu items.
        Args:
            _: Not used.
        """
        global running
        if not running:
            running = True
            logging.info("Starting mouse movement.")
            self.running_thread = threading.Thread(target=move_mouse, daemon=True)
            self.running_thread.start()
            self.notify_user("Started successfully.")
            self.start_item.title = "Running..."
            self.start_item.set_callback(None) # Disable the 'Start' button
            self.stop_item.set_callback(self.stop_clicked) # Enable the 'Stop' button
            logging.info("Mouse movement started and menu updated.")
        else:
            logging.warning("Attempted to start when already running.")

    @rumps.clicked("Stop")
    def stop_clicked(self, _):
        """
        Callback function when the 'Stop' menu item is clicked.
        Stops the mouse movement thread and resets the menu items.
        Args:
            _: Not used.
        """
        global running
        if running:
            running = False
            logging.info("Stopping mouse movement.")
            self.notify_user("Stopped.")

            # Update the menu items: change back to Start, disable Stop
            self.start_item.title = "Start"  # Change back to Start
            self.start_item.set_callback(self.start_clicked) # Enable Start button
            self.stop_item.set_callback(None)
            logging.info("Mouse movement stopped and menu updated.")
        else:
            logging.warning("Attempted to stop when already stopped.")

    @rumps.clicked("About StayActiveApp")
    def show_license(self, _):
        import subprocess
        subprocess.Popen(["python3", os.path.join(os.path.dirname(__file__), "license_viewer.py")])


if __name__ == "__main__":
    """
    Main entry point of the application. Checks for Quartz availability and runs the rumps app.
    """
    logging.info("Application starting.")
    if not quartz_available:
        logging.warning("Quartz module not found.\nMouse movement won't work.")
        rumps.alert("Quartz module not found.\nMouse movement won't work.")
    StayActiveApp().run()
    logging.info("Application finished.")
