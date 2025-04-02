import uuid

from PyQt6.QtCore import Qt

from termtel.termtel import logger
from termtel.widgets.terminal_app_wrapper import GenericTabContainer


class GameWrapper:
    """Wrapper class to standardize game interface"""

    def __init__(self, game_widget):
        self.game = game_widget

    def cleanup(self):
        """Handle cleanup when tab is closed"""
        if hasattr(self.game, 'cleanup'):
            self.game.cleanup()
        # Make sure to stop any running game loops
        if hasattr(self.game, 'gameView'):
            if hasattr(self.game.gameView, 'timer'):
                self.game.gameView.timer.stop()


def create_game_tab(self, title: str = "Asteroids") -> str:
    """Create a new game tab"""
    try:
        # Generate unique ID for the tab
        tab_id = str(uuid.uuid4())

        # Create game widget with appropriate theme color
        from termtel.widgets.space_debris import AsteroidsWidget
        theme_colors = self.parent.theme_manager.get_colors(self.parent.theme)
        game_color = theme_colors.get('text', Qt.GlobalColor.white)
        game = AsteroidsWidget(color=game_color,parent=self.parent)

        # Create wrapper and container
        wrapper = GameWrapper(game)
        container = GenericTabContainer(game, wrapper, self)

        # Add to tab widget
        index = self.addTab(container, title)
        self.setCurrentIndex(index)

        # Store in sessions
        self.sessions[tab_id] = container
        return tab_id

    except Exception as e:
        logger.error(f"Failed to create game tab: {e}")
        raise