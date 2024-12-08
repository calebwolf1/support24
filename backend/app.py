import time
from flask import Flask, request, Response, jsonify
from flask_socketio import SocketIO, emit
import asyncio
import threading
import base64
import wave
import os

from transcribe import process_audio_chunks
from claim_parser import parse_claim
from factcheck import fact_check

Q_POLLING_RATE = 0.1

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin requests


@app.route('/')
def hello_world():
    return 'Hello World'


def send(transcript):
    socketio.emit('transcription', {'text': transcript})
    transcript_queue.put_nowait(transcript)


async def claim():
    while True:
        # likely waits longer than 20 seconds because it adds the sleep time 
        # and parse_claim time rather than doing max(20, seconds(parse_claim))
        transcript: str = ""
        start_time = time.time()
        while time.time() - start_time < 20:
            await asyncio.sleep(Q_POLLING_RATE)
            if not transcript_queue.empty():
                transcript_chunk = transcript_queue.get_nowait()
                if transcript_chunk is None:
                    return 1
                transcript += transcript_chunk + " "
        
        if transcript:
            claims = parse_claim(transcript)
            print(claims)
            for claim_obj in claims['claims']:
                claim_queue.put_nowait(claim_obj)
            socketio.emit('claim', claims['claims'])
            print("sent claims")
        else:
            print("No transcript available.")

async def verify():
    while True:
        await asyncio.sleep(Q_POLLING_RATE)
        if claim_queue.empty():
            continue
        claim_obj = claim_queue.get_nowait()
        if claim_obj is None:
            return 1
        claim = claim_obj['claim']
        print('STARTING FACT CHECK')
        ftr = await fact_check(claim, 1244) # TODO: figure out UID
        print('ENDING FACT CHECK')
        socketio.emit('verify', {'claim': claim, 'fact_check_result': ftr})


async def pipeline():
    '''
    shared resources:
    - audio chunk queue
    - transcript queue
    - claims queue

    coroutines:
    - transcribe from audio queue and add to transcript queue/send to frontend
    - generate claims from transcript queue and add to claims queue
    - fact check claims from claims queue and send to frontend
    '''
    global audio_queue, transcript_queue, claim_queue
    audio_queue, transcript_queue, claim_queue = (asyncio.Queue() for _ in range(3))
    result = await asyncio.gather(process_audio_chunks(audio_queue, send),
                         claim(),
                         verify())
    print(f"Ended pipeline with results {result}.")


# Handle connections
@socketio.on("connect")
def connect():
    # The request.sid is a unique ID for the client connection.
    # It is added by SocketIO
    print(f'Client connected: {request.sid}')
    threading.Thread(target=lambda: asyncio.run(pipeline())).start()


# Handle the data event. This is a user defined event. In other words,
# it is not reserved like connect and disconnect.
@socketio.on("send_chunk")
def handle_chunk(data):
    # decode_and_append_audio(data['chunk'])
    emit('chunk_received', {'status': 'ok', 'message': 'Received audio chunk'})
    audio_chunk = base64.b64decode(data['chunk'])
    audio_queue.put_nowait(audio_chunk)


# Handle disconnections
@socketio.on("disconnect")
def disconnect():
    print(f'Client disconnected: {request.sid}')
    audio_queue.put_nowait(None)  # Signal Transcribe to stop processing
    transcript_queue.put_nowait(None)
    claim_queue.put_nowait(None)


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


import json

def parse_transcript_event(event_data):
    event_json = json.loads(event_data)
    results = event_json.get("Transcript", {}).get("Results", [])
    
    new_texts = []
    for result in results:
        if not result.get("IsPartial", True):  # Skip partial results if needed
            alternatives = result.get("Alternatives", [])
            if alternatives:
                new_texts.append(alternatives[0].get("Transcript", ""))
    
    return " ".join(new_texts)



# main driver function
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
