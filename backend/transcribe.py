import asyncio
import time
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.exceptions import BadRequestException

# Define the Transcribe Event Handler
class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream, send):
        super().__init__(output_stream)
        self.transcripts = []
        self.send = send

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            if not result.is_partial:
                for alt in result.alternatives:
                    transcript_text = alt.transcript
                    self.transcripts.append(transcript_text)
                    self.send(transcript_text)
                    print(f"Transcript: {transcript_text}")

# Function to handle audio chunks and feed them to Amazon Transcribe
async def process_audio_chunks(audio_queue: asyncio.Queue, send):
    client = TranscribeStreamingClient(region="us-east-1")

    async def start_new_stream():
        stream = await client.start_stream_transcription(
            language_code="en-US",
            media_sample_rate_hz=48000,
            media_encoding="pcm",
        )
        return stream

    # Start a new transcription stream initially
    stream = await start_new_stream()
    handler = MyEventHandler(stream.output_stream, send)

    last_audio_time = time.time()  # Track the last time audio was sent

    async def send_audio():
        nonlocal last_audio_time
        while True:
            try:
                audio_chunk = await audio_queue.get()
                if audio_chunk is None:  # Stop signal
                    print("Ending transcription stream.")
                    await stream.input_stream.end_stream()
                    break

                # Send audio chunk to the transcription service
                await stream.input_stream.send_audio_event(audio_chunk=audio_chunk)
                last_audio_time = time.time()  # Reset the timer after sending audio
                print("Sent audio event as input to Transcribe stream")

            except asyncio.QueueEmpty:
                await asyncio.sleep(0.1)

            # Check for timeout (15 seconds of inactivity)
            if time.time() - last_audio_time > 15:
                print("No audio sent in the last 15 seconds. Restarting transcription stream.")
                await stream.input_stream.end_stream()  # Close the current stream
                # Start a new transcription stream
                stream = await start_new_stream()
                handler = MyEventHandler(stream.output_stream, send)
                last_audio_time = time.time()  # Reset the timer for the new stream

    try:
        await asyncio.gather(send_audio(), handler.handle_events())
    except BadRequestException as e:
        print(f"Error during transcription (timeout or disconnection): {e}")
        # Handle timeout/disconnection by restarting the stream
        await stream.input_stream.end_stream()
        stream = await start_new_stream()
        handler = MyEventHandler(stream.output_stream, send)
        # Retry the transcription
        await asyncio.gather(send_audio(), handler.handle_events())
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle any unexpected errors, possibly restarting the stream
        await stream.input_stream.end_stream()
        stream = await start_new_stream()
        handler = MyEventHandler(stream.output_stream, send)
        await asyncio.gather(send_audio(), handler.handle_events())
    return 1
