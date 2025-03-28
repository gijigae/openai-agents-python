import asyncio
import random

from agents import Agent, function_tool
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    SingleAgentWorkflowCallbacks,
    VoicePipeline,
)

from .util import AudioPlayer, record_audio

"""
This is a simple example that uses a voice toggle interface. Run it via:
`python -m examples.voice.static.main`

1. Press spacebar to START talking, press spacebar again to STOP.
2. The pipeline automatically transcribes the audio.
3. The agent workflow starts at the Assistant agent.
4. The output of the agent is streamed to the audio player.
5. Press return/enter to exit the conversation.

Try examples like:
- Tell me a joke (will respond with a joke)
- What's the weather in Tokyo? (will call the `get_weather` tool and then speak)
- Hola, como estas? (will handoff to the spanish agent)
"""


@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."


japanese_agent = Agent(
    name="Japanese",
    handoff_description="A Japanese speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "あなたは労働災害を減らすためのAIエージェントです。",
    ),
    model="gpt-4o-mini",
)

agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. If the user speaks in Japanese, handoff to the japanese agent. Maintain conversation context across multiple exchanges.",
    ),
    model="gpt-4o-mini",
    handoffs=[japanese_agent],
    tools=[get_weather],
)


class WorkflowCallbacks(SingleAgentWorkflowCallbacks):
    def on_run(self, workflow: SingleAgentVoiceWorkflow, transcription: str) -> None:
        print(f"[debug] on_run called with transcription: {transcription}")


async def main():
    pipeline = VoicePipeline(
        workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks())
    )
    
    # Create an audio player that will be reused for the entire conversation
    with AudioPlayer() as player:
        print("Starting conversation. Press SPACEBAR to start talking, press again to stop. Press RETURN to exit.")
        
        # Conversation history will be maintained by the agent automatically
        while True:
            # Get audio input from user (returns None if return key is pressed to exit)
            audio_buffer = record_audio()
            if audio_buffer is None:
                print("Conversation ended.")
                break
                
            audio_input = AudioInput(buffer=audio_buffer)
            
            # Process the audio input and get the response
            result = await pipeline.run(audio_input)
            
            # Stream the response to the audio player
            async for event in result.stream():
                if event.type == "voice_stream_event_audio":
                    player.add_audio(event.data)
                    print("Received audio")
                elif event.type == "voice_stream_event_lifecycle":
                    print(f"Received lifecycle event: {event.event}")
            
            print("Ready for next input. Press SPACEBAR to start talking.")


if __name__ == "__main__":
    asyncio.run(main())
