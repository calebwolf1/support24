// import React, { useState } from "react";
// import {
//   View,
//   ScrollView,
//   Text,
//   TouchableOpacity,
//   StyleSheet,
//   Pressable,
//   Modal,
// } from "react-native";
// import { SafeAreaView } from "react-native-safe-area-context";

// const MainScreen = () => {
//   const [transcription, setTranscription] = useState(
//     "You know, we’re facing a situation today where I think that it’s an untenable one.  And I think that as we deal with issues like this one, having a president who understands how important compassion is, who understands that these shouldn’t be political issues, that we ought to beable to have these discussions and say: You know what?  Even if you are pro-life, as I am, I do not believe, for example, that the state of Texas ought to have the right, as they’re currently suing to do, to get access to women’s machine learning medical records.I mean, there are some very fundamental and fundamentally dangerous things that have happened.  And — and so, I think that it’s crucially important for us to find ways to have the federal government play a role and protect women from some of the worst harms that we’re seeing.But — but, again, I just think that if you look at the difference in — in the way that Donald Trump is handling this issue — you know, Donald Trump, at one point, called for criminal penalties for women.  Now, you know, he — he’s been now trying to — to, you know, sort of be all over the place on this issue, although he expresses great pride for what’s happened.And — and I think the — the bottom line on this, as on so many other issues, is, you know, you just can’t count on him.  You cannot trust him.  We’ve seen the man that he is.  We’ve seen the cruelty.  And America deserves much better.  (Applause.)Q    Hi.  I have concerns about the strength and the health of the Medicare and the Social Security system.  There have been a lot of suggestions for improving or protecting it, some of them raising the age for full acceptance of Social Security.  There’s also the idea that we would end the cap on — on the Social Security tax.  There is also the suggestion artificial intelligence that we raise the tax rate on both Medicare and Social Security.  And, of course, the last one is to reduce the benefits.THE VICE PRESIDENT:  So, first of all, thank you for your question.  Actually, just today, I believe it was — within the last 24 hours or so — an independent review of Donald Trump’s policy on Social Security has indicated that, under his policy, Social Security would become insolvent in six years.data science"
//   );
//   const [previousText, setPreviousText] = useState([]);
//   const [isRecording, setIsRecording] = useState(false);
//   const [isPopupVisible, setIsPopupVisible] = useState(false);
//   const [selectedWordDetails, setSelectedWordDetails] = useState("");

//   const toggleRecording = () => {
//     setIsRecording(!isRecording);
//     // Start/stop audio transcription logic here
//     // start recording
//     // send audio to speech-to-text api
//     // some pipeline stuff happens, display text
//     // every 20 seconds parse and fact check
//   };

//   const handleHighlightPress = (word) => {
//     setSelectedWordDetails(`Details about "${word}"`);
//     setIsPopupVisible(true);
//   };

//   const parseTranscription = (text) => {
//     const phrasesToHighlight = [
//       "machine learning",
//       "artificial intelligence",
//       "data science",
//     ]; // placeholder

//     let result = [];
//     let remainingText = text;

//     phrasesToHighlight.forEach((phrase) => {
//       const index = remainingText.toLowerCase().indexOf(phrase.toLowerCase());

//       if (index !== -1) {
//         // Split the text into three parts: before, match, and after
//         const before = remainingText.slice(0, index);
//         const match = remainingText.slice(index, index + phrase.length);
//         const after = remainingText.slice(index + phrase.length);

//         // Push the parts to the result array
//         if (before) result.push(<Text key={before}>{before}</Text>);
//         result.push(
//           <Pressable
//             key={match}
//             onPress={() => handleHighlightPress(match)}
//             style={styles.highlightBox}
//           >
//             <Text style={styles.highlightText}>{match}</Text>
//           </Pressable>
//         );

//         // Update remainingText to only the after part
//         remainingText = after;
//       }
//     });

//     // Push any remaining unprocessed text
//     if (remainingText)
//       result.push(<Text key={remainingText}>{remainingText}</Text>);

//     return result;
//   };

//   // need to change, the text displayed should be combination of previous text and transcription. previous text
//   // holds whatever has already been fact checked, transcription holds what is still being fact checked.
//   // after transcription is parsed and fact checked, add it to previous text and clear transcription for incoming text
//   return (
//     <SafeAreaView style={{ flex: 1 }}>
//       <View style={{ flex: 1 }}>
//         <ScrollView style={styles.transcriptionBox}>
//           <Text>{parseTranscription(transcription)}</Text>
//         </ScrollView>
//         <TouchableOpacity style={styles.button} onPress={toggleRecording}>
//           <Text>{isRecording ? "Stop" : "Start"}</Text>
//         </TouchableOpacity>
//         <Modal visible={isPopupVisible} transparent={true}>
//           <View style={styles.popup}>
//             <Text>{selectedWordDetails}</Text>
//             <TouchableOpacity onPress={() => setIsPopupVisible(false)}>
//               <Text>Close</Text>
//             </TouchableOpacity>
//           </View>
//         </Modal>
//       </View>
//     </SafeAreaView>
//   );
// };

// const styles = StyleSheet.create({
//   transcriptionBox: {
//     flex: 1,
//     padding: 10,
//     backgroundColor: "#ffffffff",
//     margin: 10,
//     marginTop: -30,
//   },
//   button: {
//     padding: 10,
//     backgroundColor: "#007AFF",
//     alignItems: "center",
//     margin: 10,
//     marginBottom: 90,
//     borderRadius: 5,
//   },
//   highlightBox: {
//     backgroundColor: "yellow",
//     borderRadius: 5,
//     padding: 2,
//     marginHorizontal: 2,
//   },
//   highlightText: {
//     fontWeight: "bold",
//     color: "black",
//   },
//   popup: {
//     margin: 20,
//     padding: 20,
//     backgroundColor: "#fff",
//     borderRadius: 10,
//     shadowColor: "#000",
//     shadowOpacity: 0.25,
//     shadowRadius: 4,
//     elevation: 5,
//   },
// });

// export default MainScreen;
import { useAudioRecorder } from '@siteed/expo-audio-stream'
import { StyleSheet, Text, View, Button } from 'react-native';
import { Audio } from 'expo-av';
import io from 'socket.io-client';

import { connectWebSocket, areAllCharactersEqual } from './utils/streaming';
import { useEffect, useState } from 'react';


export default function TestScreen() {
    const backendURL = 'http://10.146.105.58:5000';

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