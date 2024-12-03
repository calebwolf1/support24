import { useAudioRecorder } from '@siteed/expo-audio-stream'
import { StyleSheet, Text, View, Button } from 'react-native';
import { Audio } from 'expo-av';
import io from 'socket.io-client';

import { connectWebSocket, areAllCharactersEqual } from '../utils/streaming';
import { useEffect, useState } from 'react';


export default function TestScreen() {
    const backendURL = 'http://192.168.1.39:5000';

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
        debug: true,
    });

    

    async function processAudioDataEvent(event) {
      console.log("event received:", event.position);
      if(!areAllCharactersEqual(event.data)) {
        // console.log(event.data);
        console.log("valid audio");
      }
      // send to backend
      
    }

    const handleStart = async () => {
        const { granted } = await Audio.requestPermissionsAsync()
        if (granted) {
            // establish socket
            sock = await connectWebSocket(backendURL)
            
            // ws = await connectWebSocket(backendURL, 
            //     (event) => {console.log('Received from server:', event.data);});
            setSocket(sock);
            await startRecording({ 
                interval: 500,
                onAudioStream: async (event) => {
                    console.log("event received:", event.position);
                    if(!areAllCharactersEqual(event.data)) {
                        // console.log(event.data);
                        console.log("valid audio");
                        // console.log(event.data);
                    } else {
                        console.log("audio invalid");
                    }
                    sock.emit('send_chunk', {chunk: event.data})
                }
            });
            console.log("here");
        }
    }


    const handleStop = async () => {
        await stopRecording();
        socket.close()
        setSocket(null);
    }

    return (
        <View>
            <Button title="Request Permission" onPress={() => Audio.requestPermissionsAsync()} />
            {isRecording ? (
                <View>
                    <Text>Duration: {durationMs} ms</Text>
                    <Text>Size: {size} bytes</Text>
                    <Button title="Stop Recording" onPress={handleStop} />
                </View>
            ) : (
                <View>
                    <Button title="Start Recording" onPress={handleStart} />
                </View>
            )}
        </View>
    )
}