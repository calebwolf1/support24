import { useAudioRecorder } from "@siteed/expo-audio-stream";
import { useState, useEffect } from "react";
import { Audio } from 'expo-av';
import { connectWebSocket, areAllCharactersEqual } from "../utils/streaming";


export default function useTranscribe(url) {
  const [socket, setSocket] = useState(null);
  const {
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    isRecording,
    isPaused,
    durationMs,
    size,
    analysisData,
  } = useAudioRecorder({
      debug: false,
  });
  const [transcript, setTranscript] = useState("");

  const startTranscribe = async () => {
    const { granted } = await Audio.requestPermissionsAsync();
    if(granted) {
      sock = await connectWebSocket(url);
      sock.on('transcription', (transcript_event) => {
        console.log("new transcript event:", transcript_event);
        setTranscript(transcript + String(transcript_event["text"]))
      })
      setSocket(sock);
    }
  }

  const onAudioEvent = async (event) => {
    console.log("event received:", event.position);
    if(!areAllCharactersEqual(event.data)) {
      console.log("valid audio");
    } else {
      console.log("audio invalid");
    }
    socket.emit('send_chunk', {chunk: event.data})
  }

  useEffect(() => {
    async function f() {
      console.log("Socket null ?", socket == null);
      await startRecording({ 
        interval: 500,
        sampleRate: 48000,
        channels: 1,
        // encoding: 'pcm_16bit',
        onAudioStream: onAudioEvent
      });
      console.log("here 2");
    }
    if(socket) {
        f();
    }
  }, [socket]);

  const stopTranscribe = async () => {
    await stopRecording();
    socket.close()
    setSocket(null);
  }

  return { startTranscribe, stopTranscribe, isRecording, durationMs, size, transcript, socket };

}