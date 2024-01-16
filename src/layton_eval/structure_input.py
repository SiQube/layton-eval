import os

if __name__ == "__main__":
    os.environ["TOGETHER_API_KEY"] = "XXX"
    riddle = """
    A boy and his big sister are sitting around the kitchen table chatting.

"You know, Sis, if I took away two years from my age and gave them to you, you'd be twice my age, huh!"

"Well, why don't you just give me one more on top of that? Then I'll be three times your age."

So just how old is each sibling?
    """
    llm_solvables = []
    vlm_solvables = []
    output_types = []
    # chatbot = Chatbot(provider="together", owner="mistralai", string="Mixtral-8x7B-Instruct-v0.1", task="input_structuration")
    # for riddle, solution in list(zip(df["description"], df["solution"]))[:3]:
    #     output = chatbot.ask(riddle)
    #     llm_solvables.append(output.get("llm", False))
    #     vlm_solvables.append(output.get("vlm", False))
    #     output_types.append(output.get("output", "action"))
    # df["llm_solvable"] = llm_solvables
    # df["vlm_solvable"] = vlm_solvables
    # df["output_type"] = output_types
    # df.to_excel(f"{ROOT_DIR}/structured_answers.xlsx")
