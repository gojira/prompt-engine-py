from prompt_refresher.interaction import Interaction
from prompt_refresher.modelConfig import ModelConfig

class PromptEngineConfig: 
    """
    This class provides the configuration for the Prompt Engine
    """
    def __init__(self, modelConfig: ModelConfig = None, commentOperator: str = "#", commentCloseOperator: str = "", newlineOperator: str = "\n", startSequence: str = "##", stopSequence: str = ""):
        self.modelConfig = modelConfig
        self.commentOperator = commentOperator
        self.commentCloseOperator = commentCloseOperator
        self.newlineOperator = newlineOperator
        self.startSequence = startSequence
        self.stopSequence = stopSequence


class PromptEngine(object):
    """
    Prompt Engine provides a reusable interface for the developer to construct prompts for large scale language model inference
    """
    def __init__(self, config: PromptEngineConfig, description: str, examples: list = [], dialog: list = []):
        self.config = config
        self.description = description
        self.examples = examples
        self.dialog = dialog

    def buildContext(self):
        """
        Builds the context from the description, examples, and dialog.
        """
        self.context: str = ""

        # Add the model config parameters to the context
        self._insert_model_config()

        # Add the description to the context
        self._insert_description()
        
        # Add the examples to the context
        self._insert_examples()
        
        # Checks if the number of tokens after adding the examples in the context is greater than the max_tokens
        if (self.config.modelConfig != None and self.__assert_token_limit(self.context, self.config.modelConfig.max_tokens)):
            raise Exception("Token limit exceeded, reduce the number of examples or size of description. Alternatively, you may increase the max_tokens in ModelConfig")
        
        # Add the dialog to the context
        self._insert_dialog()
        
        # Checks if the number of tokens after adding the dialog in the context is greater than the max_tokens, and if so, starts removing the most historical interactions
        if (self.config.modelConfig != None and self.__assert_token_limit(self.context, self.config.modelConfig.max_tokens)):
            self.removeFirstInteraction()
            self.buildContext()

        return self.context

    def buildPrompt(self, naturalLanguage: str, newlineEnd: bool = True):
        """
        Builds the prompt from the parameters given to the Prompt Engine 
        """
        prompt: str = self.context + self.config.startSequence + " " + naturalLanguage + self.config.stopSequence

        if (newlineEnd):
            prompt += self.config.newlineOperator

        return prompt

    def truncatePrompt(self, prompt: str):
        """
        Truncates the prompt to the max_tokens in the modelConfig
        """
        if (self.config.modelConfig != None and self.__assert_token_limit(prompt, self.config.modelConfig.max_tokens)):
            prompt = prompt.split()[:self.config.modelConfig.max_tokens]
            prompt = " ".join(prompt)
            return prompt
        else:
            return prompt
    
    def addExample(self, example: Interaction):
        """
        Adds an interaction to the example
        """
        self.examples.append(example)
    
    def addInteraction(self, interaction: Interaction):
        """
        Adds an interaction to the dialog
        """
        self.dialog.append(interaction)

    def removeLastInteraction(self):
        """
        Removes the last interaction from the dialog
        """
        if (len(self.dialog) > 0):
            self.dialog.pop()
        else:
            raise Exception("No interactions to remove")

    def removeFirstInteraction(self):
        """
        Removes the first interaction from the dialog
        """
        if (len(self.dialog) > 0):
            self.dialog.pop(0)
        else:
            raise Exception("No interactions to remove")

    def _insert_model_config(self):
        """
        Inserts the model config into the context
        """
        if (self.config.modelConfig != None):
            promptEngineConfigMembers = [attr for attr in dir(self.config.modelConfig) if not callable(getattr(self.config.modelConfig, attr)) and not attr.startswith("__")]
            for member in promptEngineConfigMembers:
                self.context += self.config.commentOperator + " " + member + ": " + str(getattr(self.config.modelConfig, member)) + self.config.commentCloseOperator + self.config.newlineOperator
                self.context += self.config.newlineOperator

    def _insert_description(self):
        """
        Inserts the description into the context
        """
        if (self.description != ""):
            self.context += self.config.commentOperator + " " + self.description + self.config.newlineOperator + self.config.commentCloseOperator
            self.context += self.config.newlineOperator

    def _insert_examples(self):
        """
        Inserts the examples into the context
        """
        if (self.examples != []):
            for example in self.examples:
                self.context += self.config.startSequence + " " + example.naturalLanguage + self.config.stopSequence + self.config.newlineOperator
                self.context += example.code + self.config.newlineOperator

    def _insert_dialog(self):
        """
        Inserts the dialog into the context
        """
        if (self.dialog != []):
            for dialog in self.dialog:
                self.context += self.config.startSequence + " " + dialog.naturalLanguage + self.config.stopSequence + self.config.newlineOperator
                self.context += dialog.code + self.config.newlineOperator
    
    def __assert_token_limit(self, context: str, max_tokens: int):
        """
        Asserts that the number of tokens in the context is less than the max_tokens
        """
        if context != None:
            if context != "":
                numTokens = len(context.split())
                if numTokens > max_tokens:
                    return True
                else:
                    return False
            else:
                return False
        else:
            raise Exception("The string to assert is None")
