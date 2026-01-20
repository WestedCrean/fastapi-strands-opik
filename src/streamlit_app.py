import asyncio
import boto3
import nest_asyncio
import streamlit as st

from test_opik.agent.orchestrator import get_orchestrator_agent

# nest_asyncio.apply()

st.title("Strands agent")


async def stream_response(prompt):
    """Stream the agent response."""
    agent = await get_orchestrator_agent()
    async for chunk in agent.stream_response(user_query=prompt):
        yield chunk


def main():
    if prompt := st.chat_input():
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            st.write_stream(stream_response(prompt))


if __name__ == "__main__":
    main()
