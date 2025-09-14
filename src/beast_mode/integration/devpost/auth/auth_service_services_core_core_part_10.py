
def clear_credentials(self) -> None:
    """Clear stored credentials"""
    self.credentials = AuthCredentials()
    if self.credentials_file.exists():
        self.credentials_file.unlink()
