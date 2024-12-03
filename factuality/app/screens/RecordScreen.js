// import { StatusBar } from 'expo-status-bar';
// import { Text, View, Button } from 'react-native';

// import styles from '../styles/RecordScreenStyles';

// export default function RecordScreen(props) {
//   return (
//     <View style={styles.container}>
//       <Text>Hello React Native</Text>
//       <Button 
//         title={"Click me"}
//         onPress={() => 
//           console.log("Pressed")
//         }
//       />
//       <StatusBar style="auto" />
//     </View>
//   );
// }

import React from 'react';
import { StyleSheet, Text, View, Button } from 'react-native';
import { Audio } from 'expo-av';
import { useAudioRecorder } from '@siteed/expo-audio-stream';

export default function RecordScreen() {
  const config = {
    onAudioStream: async (event) => {
      console.log('Audio data:', event);
      // Process the audio data here
    },
    interval: 500,
  };

  const {
    startRecording,
    stopRecording,
  } = useAudioRecorder({debug: true});

  const [recording, setRecording] = React.useState(false);
  // const [recordings, setRecordings] = React.useState([]);

  const handleStart = async () => {
    const { granted } = await Audio.requestPermissionsAsync();
    if (granted) {
      const result = await startRecording(config);
      console.log('Recording started with result:', result)
      setRecording(true);
    }
  };

  async function handleStop() {
    const result = await stopRecording();
    setRecording(false);
    console.log('Recording stopped with result:', result);
  }

  // async function startRecorder() {
  //   try {
  //     const perm = await Audio.requestPermissionsAsync();
  //     if (perm.status === "granted") {
  //       await Audio.setAudioModeAsync({
  //         allowsRecordingIOS: true,
  //         playsInSilentModeIOS: true
  //       });
  //       const { recording } = await Audio.Recording.createAsync(Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY);
  //       setRecording(recording);
  //     }
  //   } catch (err) {}
  // }

  // async function stopRecorder() {
  //   setRecording(undefined);

  //   await recording.stopAndUnloadAsync();
  //   let allRecordings = [...recordings];
  //   const { sound, status } = await recording.createNewLoadedSoundAsync();
  //   allRecordings.push({
  //     sound: sound,
  //     duration: getDurationFormatted(status.durationMillis),
  //     file: recording.getURI()
  //   });

  //   setRecordings(allRecordings);
  // }

  // function getDurationFormatted(milliseconds) {
  //   const minutes = milliseconds / 1000 / 60;
  //   const seconds = Math.round((minutes - Math.floor(minutes)) * 60);
  //   return seconds < 10 ? `${Math.floor(minutes)}:0${seconds}` : `${Math.floor(minutes)}:${seconds}`
  // }

  // function getRecordingLines() {
  //   return recordings.map((recordingLine, index) => {
  //     return (
  //       <View key={index} style={styles.row}>
  //         <Text style={styles.fill}>
  //           Recording #{index + 1} | {recordingLine.duration}
  //         </Text>
  //         <Button onPress={() => recordingLine.sound.replayAsync()} title="Play"></Button>
  //       </View>
  //     );
  //   });
  // }

  // function clearRecordings() {
  //   setRecordings([])
  // }

  return (
    <View style={styles.container}>
      <Button title={recording ? 'Stop Recording' : 'Start Recording'} onPress={recording ? handleStop : handleStart} />
      {/* {getRecordingLines()} */}
      {/* <Button title={recordings.length > 0 ? 'Clear Recordings' : ''} onPress={clearRecordings} /> */}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 10,
    marginRight: 40
  },
  fill: {
    flex: 1,
    margin: 15
  }
});