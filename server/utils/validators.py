def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if a file has an allowed extension
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
