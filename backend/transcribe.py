import asyncio
import time
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.exceptions import BadRequestException
import asyncio

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

    while True:
        try:
            # Start a new transcription session
            stream = await client.start_stream_transcription(
                language_code="en-US",
                media_sample_rate_hz=44100,
                media_encoding="pcm",
            )

            handler = MyEventHandler(stream.output_stream, send)
            
            async def send_audio():
                while True:
                    try:
                        audio_chunk = audio_queue.get_nowait()
                        if audio_chunk is None:  # Stop signal
                            print("Ending transcription stream.")
                            await stream.input_stream.end_stream()
                            break
                        await stream.input_stream.send_audio_event(audio_chunk=audio_chunk)
                        print("Sent audio event as input to Transcribe stream")
                    except asyncio.QueueEmpty:
                        await asyncio.sleep(0.1)

            # Gather the sending audio and handler
            await asyncio.gather(send_audio(), handler.handle_events())

        except BadRequestException as e:
            if 'timed out' in str(e):  # Check for timeout error
                print("No new audio for 15 seconds, restarting transcription.")
                continue  # Restart the transcription process

        except Exception as e:
            print(f"Error during transcription: {e}")
            break

    return 1
