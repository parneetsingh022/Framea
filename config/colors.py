class Colors:
    """Contains color palettes for different themes."""
    LIGHT = {
        "primary": "#007BFF",
        "secondary": "#6C757D",
        "background": "#F8F9FA",
        "surface": "#FFFFFF",
        "text": "#212529",
        "success": "#28A745",
        "danger": "#DC3545",
    }
    DARK = {
        "primary": "#007BFF",
        "secondary": "#6C757D",
        "background": "#121212",
        "surface": "#1E1E1E",
        "text": "#EAEAEA",
        "success": "#28A745",
        "danger": "#DC3545",
    }


class Theme:
    """Manages the application's current theme and provides corresponding colors."""
    def __init__(self):
        self._theme = "light"
        self._colors = Colors()

    @property
    def theme(self):
        """Gets the current theme name ('light' or 'dark')."""
        return self._theme
    
    @theme.setter
    def theme(self, value):
        """Sets the theme name and validates it."""
        if value in ["light", "dark"]:
            self._theme = value
        else:
            raise ValueError("Theme must be 'light' or 'dark'")
    
    @property
    def colors(self):
        """A property that returns the correct color palette for the current theme."""
        if self.theme == "light":
            return self._colors.LIGHT
        else:
            return self._colors.DARK
            
    def toggle_theme(self):
        """Switches the theme from light to dark or vice-versa."""
        self.theme = "dark" if self.theme == "light" else "light"


theme = Theme()  # Singleton instance