import pandas as pd

class KvkStats:
    def __init__(self, file_path):
        # Correct the method to read the Excel file
        self.data = pd.read_excel(file_path, engine='openpyxl')
