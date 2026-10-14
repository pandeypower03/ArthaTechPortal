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
    "FILE_BAD": "Please attach an .xlsx file in the field named 'file'.",
    "UPLOAD_HAS_ERRORS": "The file has errors. Nothing was saved.",
    "UPLOAD_SAVED": "The file was uploaded and saved.",
    "HOUSE_CREATED": "The production house was saved.",
    "HOUSE_INVALID": "Some details are wrong. Nothing was saved.",
    "HOUSE_UPDATED": "The production house was updated.",
    "ITEM_REMOVED": "Removed.",
    "REMOVE_BLOCKED": "This cannot be removed.",
    "MEMBER_SWITCHED_OFF": "The person was switched off. Their history is kept.",
}

def get_message(code):
    return MESSAGES.get(code, MESSAGES["SERVER_ERROR"])