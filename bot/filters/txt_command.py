from aiogram.filters import BaseFilter
from aiogram.types import Message

class TextCommand(BaseFilter):
    def __init__(self, commands: list):
        self.commands = [cmd.lower() for cmd in commands]
    
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        
        text = message.text.strip().lower()
        
        for cmd in self.commands:
            if text.startswith(cmd + " ") or text == cmd:
                return True
        
        return False
