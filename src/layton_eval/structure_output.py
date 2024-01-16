import os

import pandas as pd
from constants import ROOT_DIR

if __name__ == "__main__":
    os.environ["TOGETHER_API_KEY"] = "XXX"
    structured_solutions = []
    df = pd.read_excel(f"{ROOT_DIR}/layton-annotations.xlsx").iloc[:3, :]
    print(df)
    # chatbot = Chatbot(provider="together", owner="mistralai", string="Mixtral-8x7B-Instruct-v0.1", task="answer_structuration")
    # for riddle, solution in list(zip(df["description"], df["solution"]))[:3]:
    #     output = chatbot.ask(riddle, solution)
    #     structured_solutions.append(output.get("structured", []))
    # df["structured_solution"] = structured_solutions
    # df.to_excel(f"{ROOT_DIR}/structured_answers.xlsx")
