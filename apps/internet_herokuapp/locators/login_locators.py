"""Locator descriptors for the internet_herokuapp Login page.

Named here (rather than scattered inline in the Page Object) so they stay
easy to find and update if the target application's markup changes
(Constitution IV).
"""

USERNAME_FIELD_LABEL = "Username"
PASSWORD_FIELD_LABEL = "Password"

LOGIN_BUTTON_ROLE = "button"
LOGIN_BUTTON_NAME = "Login"

# CSS id selector used as a last resort here: this demo application exposes
# no ARIA role/test-id/label for its flash banner element, so no more
# resilient locator strategy is available (FR-008 last-resort exception).
FLASH_MESSAGE_SELECTOR = "#flash"
