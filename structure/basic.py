from enum import Enum



class LanguageEnum(str, Enum):
    english = "english"
    chinese = "chinese"

class ModelEnum(str, Enum):
    openai = "openai"
    vosk = "vosk"
