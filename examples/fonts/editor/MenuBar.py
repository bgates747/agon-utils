import tkinter as tk
from tkinter import Menu

class MenuBar:
    """Menu bar for the application, providing access to file operations, edit options, and help."""
    def __init__(self, parent, app_reference):
        self.parent = parent
        self.app_reference = app_reference

        # Create a Menu widget and attach it to the parent window
        self.menubar = Menu(self.parent)

        # File Menu
        file_menu = Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.get_open_filename)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        self.menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = Menu(self.menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo_action)
        edit_menu.add_command(label="Redo", command=self.redo_action)
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences", command=self.open_preferences)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)

        # Help Menu
        help_menu = Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
        self.menubar.add_cascade(label="Help", menu=help_menu)

        # Attach the menubar to the parent window
        self.parent.config(menu=self.menubar)

    def get_open_filename(self):
        """Handle the Open action by invoking the FileManager's get_open_filename method."""
        self.app_reference.file_manager.get_open_filename()

    def save_file(self):
        """Handle the Save action by invoking the FileManager's save_file method."""
        self.app_reference.file_manager.save_file()

    def exit_app(self):
        """Close the application."""
        self.parent.quit()

    # Placeholder methods for Edit Menu actions
    def undo_action(self):
        """Placeholder for undo functionality."""
        print("Undo action triggered")

    def redo_action(self):
        """Placeholder for redo functionality."""
        print("Redo action triggered")

    def open_preferences(self):
        """Open preferences dialog; placeholder for functionality."""
        print("Open preferences dialog")
        # Placeholder: Add logic to open a preferences dialog if needed

    # Placeholder methods for Help Menu actions
    def show_about(self):
        """Show about dialog; placeholder for functionality."""
        print("Show about dialog")
        # Placeholder: Add logic to open an About dialog if needed

    def show_help(self):
        """Show help dialog; placeholder for functionality."""
        print("Show help dialog")
        # Placeholder: Add logic to open a Help dialog if needed
