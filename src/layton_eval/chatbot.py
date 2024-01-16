import typing as t
from functools import cached_property

from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.llms import Together
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


class LaytonRiddle(BaseModel):
    llm: bool = Field(description="the riddle description is sufficient to solve the riddle")
    vlm: bool = Field(
        description="""the riddle description is not sufficient to solve the riddles, but it contains a mention to a certain image or visual information that,\
                                if present, could make the riddle solvable"""
    )
    output: t.Literal["action", "text"] = Field(
        description="text if the riddle answer can be described with natural language, action otherwise"
    )


class LaytonAnswer(BaseModel):
    structured: t.List[str] = Field(
        description="A list containing different writings of the answers. Each writing should be as short as possible. It should\
                                            not contain any reasoning, just the raw answer. It should contain all imagineable correct answers to the riddle.\
                                            If there is no apparent solution in the answer, do not generate new ones.\
                                            Generate as much valid answers as possible from the extracted one."
    )


class ModelArgs(t.TypedDict):
    provider: t.Literal["openai", "together"]
    owner: t.Literal["mistralai", "togethercomputer"] | None
    string: t.Literal["gpt-3.5-turbo", "llama-2-7b-chat", "Mistral-7B-Instruct-v0.1"]
    task: t.Literal["input_structuration", "answer_structuration"]


class Chatbot:
    RIDDLE_TEMPLATE = """[INST]
    Here is a Professor Layton riddle, use it to answer the questions and format the answer but do not solve the riddle.

    Professor Layton Riddle: {riddle}
    {format_instructions}
    Questions:
    - Is this riddle llm_solvable ?
    - Is this riddle vlm_solvable ?
    - What is the output_type of this riddle ?
    [/INST]"""

    ANSWER_TEMPLATE = """[INST]
    Here is a Professor Layton riddle and its solution, use it to structure the answer but do not solve the riddle.

    Professor Layton Riddle: {riddle}

    Riddle answer: {answer}
    {format_instructions}
    Please format the riddle answer.
    [/INST]"""

    def __init__(self, **model_kwargs: t.Unpack[ModelArgs]) -> None:
        self.model_provider = model_kwargs.get("provider", "openai")
        self.model_owner = model_kwargs.get("owner", None)
        self.model_string = model_kwargs.get("string", "gpt-3.5-turbo")
        self.task = model_kwargs.get("task", None)

    @cached_property
    def llm(self) -> ChatOpenAI | Together:
        if self.model_provider == "openai":
            return ChatOpenAI(
                model=self.model_string,
                streaming=False,
                model_kwargs={},
            )
        elif self.model_provider == "together":
            return Together(
                model=f"{self.model_owner}/{self.model_string}",
                max_tokens=1024,
            )

    @cached_property
    def parser(self) -> JsonOutputParser:
        pydantic_object = LaytonRiddle if self.task == "input_structuration" else LaytonAnswer
        return JsonOutputParser(pydantic_object=pydantic_object)

    @cached_property
    def template(self) -> PromptTemplate:
        if self.task == "input_structuration":
            return PromptTemplate(
                template=self.RIDDLE_TEMPLATE,
                input_variables=["riddle"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()},
            )
        elif self.task == "answer_structuration":
            return PromptTemplate(
                template=self.ANSWER_TEMPLATE,
                input_variables=["riddle", "answer"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()},
            )
        return

    @cached_property
    def chain(self) -> Chain:
        return LLMChain(llm=self.llm, memory=None, verbose=True, prompt=self.template, output_parser=self.parser)

    def ask(
        self,
        riddle: str,
        answer: str = None,
    ) -> str:
        if self.task == "input_structuration":
            return self.chain.run(
                riddle=riddle,
            )
        elif self.task == "answer_structuration":
            return self.chain.run(riddle=riddle, answer=answer)
        return
