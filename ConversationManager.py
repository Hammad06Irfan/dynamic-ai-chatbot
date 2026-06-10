class ConversationManager:
    def __init__(self, system_prompt="You are a helpful assistant."):
        self.history = []

        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})
            
    def add_user_message(self, message):
        self.history.append({"role": "user", "content": message})

    def add_ai_message(self, message):
        self.history.append({"role": "assistant", "content": message})

    def get_history(self):
        return self.history
    
    def clear_history(self):
        system_prompt = self.history[0] if self.history and self.history[0]["role"] == "system" else None
        self.history = [system_prompt] if system_prompt else []

    def update_system_prompt(self, new_prompt):
        """Changes the AI's persona on the fly and clears old memory."""
        # 1. If history has items and the first item is a system prompt, update it
        if self.history and self.history[0]["role"] == "system":
            self.history[0]["content"] = new_prompt
        else:
            # 2. If it doesn't exist for some reason, insert it at the very beginning
            self.history.insert(0, {"role": "system", "content": new_prompt})
        
        # 3. CRITICAL: Clear out all the user/assistant chat history 
        # because the old chat was based on the old persona!
        self.clear_history()