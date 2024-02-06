from langchain_community.chat_models import ChatOllama
from langchain_community.llms.gpt4all import GPT4All
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain


class DnDGameMaster:
    def __init__(self):
        self.state = "world_selection"  # initial state
        self.world_setting = None
        self.world_settings = {
            1: "The Shattered Isles: A realm of floating islands and sky pirates.",
            2: "The Verdant Expanse: A dense jungle world teeming with life and peril.",
            3: "The Frozen Wastes: A land of ice, snow, and forgotten magic.",
        }

        self.llm = ChatOllama(model="llama2")
        # self.llm = GPT4All(
        #     model="/Users/kohjunkai/Library/Application Support/nomic.ai/GPT4All/"
        # )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="You are a Game Master of a Dungeons and Dragons Quest. You create beautiful and immersive worlds for your players to explore."
                ),  # The persistent system prompt
                MessagesPlaceholder(
                    variable_name="chat_history"
                ),  # Where the memory will be stored.
                HumanMessagePromptTemplate.from_template(
                    "{user_input}"
                ),  # Where the human input will injected
            ]
        )
        self.chain = LLMChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True,
            prompt=self.prompt_template,
        )
        self.output_parser = StrOutputParser()

    def process_message(self, message):
        response = self.chain.predict(user_input=message)
        return response

    def process_input(self, message):
        """
        Main entry point for processing user input based on the current game state.

        """
        # return self.process_message(message)
        if self.state == "world_selection":
            return self.handle_world_selection(message)
        elif self.state == "scenario_narration":
            return self.process_message(message)
        else:
            return "Unknown game state. Please restart."

    def handle_world_selection(self, message):
        """
        Handle the selection of the game world.
        """
        try:
            user_choice = int(message)
            print(user_choice, self.world_settings)
            if user_choice not in self.world_settings:
                return "Invalid choice. Please select 1, 2, or 3."

            selected_world = self.world_settings[user_choice]
            self.world_setting = selected_world
            self.prompt_template = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content="You are a Game Master of a Dungeons and Dragons Quest. You create beautiful and immersive worlds for your players to explore."
                    ),
                    AIMessagePromptTemplate.from_template(
                        "Welcome to AI Dungeons & Dragons! Please choose a world setting for your DnD quest: 1. The Shattered Isles 2. Jungle World 3. The Frozen Wastes"
                    ),
                    HumanMessagePromptTemplate.from_template(
                        "Your choice: {user_input} - " + selected_world
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    SystemMessage(
                        content="Please generate 3 character options for the player to choose from. keep the details breif and short."
                    ),
                ]
            )
            self.chain = LLMChain(
                llm=self.llm,
                memory=self.memory,
                verbose=True,
                prompt=self.prompt_template,
            )
            response = self.chain.predict(user_input=message)

            # update game state
            self.prompt_template = self.prompt_template = (
                ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(
                            content="You are a Game Master of a Dungeons and Dragons Quest."
                        ),
                        AIMessagePromptTemplate.from_template(
                            "Welcome to AI Dungeons & Dragons! Please choose a world setting for your DnD quest: 1. The Shattered Isles 2. Jungle World 3. The Frozen Wastes"
                        ),
                        HumanMessagePromptTemplate.from_template(
                            "Your choice: {user_input} - " + selected_world
                        ),
                        MessagesPlaceholder(variable_name="chat_history"),
                        SystemMessage(
                            content="Please continue to narrate the DnD story based on the chosen settings, player character choice and the subsequent action choices."
                        ),
                    ]
                )
            )
            self.chain = LLMChain(
                llm=self.llm,
                memory=self.memory,
                verbose=True,
                prompt=self.prompt_template,
            )
            self.state = "scenario_narration"  # update game state
            return response
        except ValueError:
            return "Invalid choice. Please select 1, 2, or 3."

        except Exception as e:
            return f"An unexpected error occurred: {e}. Please try again."