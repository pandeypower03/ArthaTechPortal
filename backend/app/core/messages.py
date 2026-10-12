MESSAGES = {
    "INVALID_CREDENTIALS": "Email, username or password is wrong.",
    "ACCOUNT_LOCKED": "Too many failed tries. Please try again later.",
    "NOT_AUTHENTICATED": "Please log in to continue.",
    "TOKEN_INVALID": "Your session is not valid. Please log in again.",
    "PERMISSION_DENIED": "You are not allowed to do this.",
    "NOT_FOUND": "We could not find what you asked for.",
    "VALIDATION_ERROR": "Some fields are not correct.",
    "SERVER_ERROR": "Something went wrong. Please try again.",
    "LOGOUT_OK": "You are logged out.",
    "USER_EXISTS": "A user with this email or username already exists.",
    "USER_NOT_FOUND": "This user was not found.",
    "USER_CREATED": "User created.",
    "USER_ACTIVATED": "User activated.",
    "USER_DEACTIVATED": "User deactivated.",
    "PASSWORD_RESET_OK": "Password changed. The user must log in again.",
}

def get_message(code):
    return MESSAGES.get(code, MESSAGES["SERVER_ERROR"])