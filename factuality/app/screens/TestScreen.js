import { StyleSheet, Text, View, Button } from 'react-native';
import { Audio } from 'expo-av';

import { useEffect, useState } from 'react';
import useTranscribe from '../hooks/useTranscribe';


export default function TestScreen() {
    const backendURL = 'http://192.168.1.71:5000';

    const { startTranscribe, 
        stopTranscribe, 
        isRecording, 
        durationMs, 
        size,
        transcript
    } = useTranscribe(backendURL);

    return (
        <View>
            <Button title="Request Permission" onPress={() => Audio.requestPermissionsAsync()} />
            {isRecording ? (
                <View>
                    <Text>Duration: {durationMs} ms</Text>
                    <Text>Size: {size} bytes</Text>
                    <Button title="Stop Recording" onPress={stopTranscribe} />
                </View> 
            ) : (
                <View>
                    <Button title="Start Recording" onPress={startTranscribe} />
                </View>
            )}
            <Text>Transcript: {transcript}</Text>
        </View>
    )
}