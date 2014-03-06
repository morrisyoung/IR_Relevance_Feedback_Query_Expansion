class CoreInput:
    """
    Interface class between Main and Core,
    Carry processed words to Core
    """
    def __init__(self):
        self.title = []  # array of string, title of returned file
        self.summary = []  # array of string, summary of returned file
        self.text = []  # array of string, text of returned file, may be empty
        self.url = ""  # string, URL of returned file
        self.relevant = True  # this search research is relevant or not
