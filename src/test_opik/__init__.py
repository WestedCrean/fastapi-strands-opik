import os
from openai import OpenAI
from fastapi import FastAPI

app = FastAPI()


@app.get("/test_llm")
async def hello() -> str:

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        # anthropic openai-compatible api
        base_url="https://api.anthropic.com/v1",
    )

    response = await client.responses.create(
        model="claude-3-haiku-20240307",
        instructions="You are a coding assistant that talks like a pirate.",
        input="How do I check if a Python object is an instance of a class?",
    )
    output = response.output_text
    # if output:
    #    return output

    return "dupa"


@app.get("/")
async def root() -> str:
    return "Hello wordld"
