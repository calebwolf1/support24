from flask import Flask, request, Response, jsonify
from flask_socketio import SocketIO, emit
import asyncio
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
import threading
import base64
import wave
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin requests


@app.route('/')
def hello_world():
    return 'Hello World'


# Define the Transcribe Event Handler
class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream):
        super().__init__(output_stream)
        self.transcripts = []

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                transcript_text = alt.transcript
                self.transcripts.append(transcript_text)
                socketio.emit('transcription', {'text': transcript_text})
                print(f"Transcript: {transcript_text}")


# Function to handle audio chunks and feed them to Amazon Transcribe
async def process_audio_chunks(audio_queue: asyncio.Queue):
    client = TranscribeStreamingClient(region="us-east-1")
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )
    
    handler = MyEventHandler(stream.output_stream)
    async def send_audio():
        while True:
            try:
                audio_chunk = audio_queue.get_nowait()
                if audio_chunk is None:  # Stop signal
                    print("Ending transcription stream.")
                    await stream.input_stream.end_stream()
                    break
                await stream.input_stream.send_audio_event(audio_chunk=audio_chunk)
                # print("sent audio event as input to Transcribe stream")
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.1)

    await asyncio.gather(send_audio(), handler.handle_events())


# Handle connections
@socketio.on("connect")
def connect():
    # The request.sid is a unique ID for the client connection.
    # It is added by SocketIO
    print(f'Client connected: {request.sid}')
    global audio_queue
    audio_queue = asyncio.Queue()
    # socketio.start_background_task(process_audio_chunks, audio_queue)
    threading.Thread(target=lambda: asyncio.run(process_audio_chunks(audio_queue))).start()


# Handle the data event. This is a user defined event. In other words,
# it is not reserved like connect and disconnect.
@socketio.on("send_chunk")
def handle_chunk(data):
    # print("valid audio" if valid_audio(data['chunk']) else "invalid audio")
    # print(f"queue size before adding chunk: {audio_queue.qsize()}")
    # decode_and_append_audio(data['chunk'])
    emit('chunk_received', {'status': 'ok', 'message': 'Received audio chunk'})
    audio_chunk = base64.b64decode(data['chunk'])
    audio_queue.put_nowait(audio_chunk)


# Handle disconnections
@socketio.on("disconnect")
def disconnect():
    print(f'Client disconnected: {request.sid}')
    audio_queue.put_nowait(None)  # Signal Transcribe to stop processing


def valid_audio(chunk):
    for c in chunk:
        if c != 'A' or c != '=':
            return True
    return False


def decode_and_append_audio(audio_chunk_base64, output_file="output_audio.wav", sample_rate=16000, channels=1, sample_width=2):
    """
    Decodes base64-encoded PCM audio data and appends it to a WAV file.

    :param audio_chunk_base64: The base64-encoded audio chunk (PCM data).
    :param output_file: The path to the output WAV file.
    :param sample_rate: The sample rate of the audio (default: 16000 Hz).
    :param channels: The number of audio channels (default: 1).
    :param sample_width: The sample width in bytes (default: 2 bytes for 16-bit PCM).
    """
    try:
        # Decode the base64-encoded audio chunk
        audio_chunk = base64.b64decode(audio_chunk_base64)

        # Check if the file exists
        file_exists = os.path.isfile(output_file)

        # Open the WAV file in write mode if new, append mode if exists
        with wave.open(output_file, 'wb' if not file_exists else 'rb') as wav_file:
            if not file_exists:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_chunk)
            else:
                existing_data = wav_file.readframes(wav_file.getnframes())
                wav_file.close()

                # Open again in write mode to append new data
                with wave.open(output_file, 'wb') as wav_file_append:
                    wav_file_append.setnchannels(channels)
                    wav_file_append.setsampwidth(sample_width)
                    wav_file_append.setframerate(sample_rate)
                    wav_file_append.writeframes(existing_data + audio_chunk)

        print(f"Audio chunk successfully appended to {output_file}")
    except Exception as e:
        print(f"Error decoding or appending audio chunk: {e}")


# main driver function
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
