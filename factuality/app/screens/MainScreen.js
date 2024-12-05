import React, { useState } from 'react';
import { View, ScrollView, Text, TouchableOpacity, StyleSheet, Pressable, Modal } from 'react-native';

const MainScreen = () => {
  const [transcription, setTranscription] = useState('Hello world');
  const [previousText, setPreviousText] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [selectedWordDetails, setSelectedWordDetails] = useState('');

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Start/stop audio transcription logic here
    // start recording
    // send audio to speech-to-text api
    // some pipeline stuff happens, display text
    // every 20 seconds parse and fact check
  };

  const handleHighlightPress = (word) => {
    setSelectedWordDetails(`Details about "${word}"`);
    setIsPopupVisible(true);
  };

  const parseTranscription = (text) => {
    const phrasesToHighlight = ['machine learning', 'artificial intelligence', 'data science']; // placeholder
  
    let result = [];
    let remainingText = text;
  
    phrasesToHighlight.forEach((phrase) => {
      const index = remainingText.toLowerCase().indexOf(phrase.toLowerCase());
  
      if (index !== -1) {
        // Split the text into three parts: before, match, and after
        const before = remainingText.slice(0, index);
        const match = remainingText.slice(index, index + phrase.length);
        const after = remainingText.slice(index + phrase.length);
  
        // Push the parts to the result array
        if (before) result.push(<Text key={before}>{before}</Text>);
        result.push(
          <Pressable
            key={match}
            onPress={() => handleHighlightPress(match)}
            style={styles.highlightBox}
          >
            <Text style={styles.highlightText}>{match}</Text>
          </Pressable>
        );
  
        // Update remainingText to only the after part
        remainingText = after;
      }
    });
  
    // Push any remaining unprocessed text
    if (remainingText) result.push(<Text key={remainingText}>{remainingText}</Text>);
  
    return result;
  };
  
  // need to change, the text displayed should be combination of previous text and transcription. previous text
  // holds whatever has already been fact checked, transcription holds what is still being fact checked.
  // after transcription is parsed and fact checked, add it to previous text and clear transcription for incoming text
  return (
    <View style={{ flex: 1 }}>
      <ScrollView style={styles.transcriptionBox}>
        <Text>{parseTranscription(transcription)}</Text>
      </ScrollView>
      <TouchableOpacity style={styles.button} onPress={toggleRecording}>
        <Text>{isRecording ? 'Stop' : 'Start'}</Text>
      </TouchableOpacity>
      <Modal visible={isPopupVisible} transparent={true}>
        <View style={styles.popup}>
          <Text>{selectedWordDetails}</Text>
          <TouchableOpacity onPress={() => setIsPopupVisible(false)}>
            <Text>Close</Text>
          </TouchableOpacity>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  transcriptionBox: {
    flex: 1,
    padding: 10,
    backgroundColor: '#f8f8f8',
  },
  button: {
    padding: 10,
    backgroundColor: '#007AFF',
    alignItems: 'center',
    margin: 10,
    borderRadius: 5,
  },
  highlightBox: {
    backgroundColor: 'yellow',
    borderRadius: 5,
    padding: 2,
    marginHorizontal: 2,
  },
  highlightText: {
    fontWeight: 'bold',
    color: 'black',
  },
  popup: {
    margin: 20,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
});

export default MainScreen;