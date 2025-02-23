class Settings:
    def __init__(self):
        self.debug = True
        self.database_url = "sqlite:///./test.db"  # Example database URL
        self.secret_key = "your_secret_key"  # Example secret key

settings = Settings()
