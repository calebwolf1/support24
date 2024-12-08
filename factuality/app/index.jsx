import React, { useState, useRef, useEffect } from "react";
import {
  View,
  ScrollView,
  Text,
  TouchableOpacity,
  StyleSheet,
  Pressable,
  Modal,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import useTranscribe from './hooks/useTranscribe';

const MainScreen = () => {
  const [transcription, setTranscription] = useState(""); // Store what's currently being transcribed
  const [previousText, setPreviousText] = useState([]); // "Permanent" storage of text that's been fully fact checked
  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [selectedWordDetails, setSelectedWordDetails] = useState("");
  const [claims, setClaims] = useState([]); // All claims that have been made throughout the whole text
  const [currentClaims, setCurrentClaims] = useState([]); // Only the claims for the current parsing cycle
  const [verifyResults, setVerifyResults] = useState([]);
  const [processingText, setProcessingText] = []; // Intermediate storage of text that has been parsed but not fact checked
  const scrollViewRef = useRef(null);
  const backendURL = 'http://10.148.111.91:5000';
  const { startTranscribe, 
      stopTranscribe, 
      isRecording, 
      durationMs, 
      size,
      transcript,
      socket
    } = useTranscribe(backendURL);
  
  const handleHighlightPress = (word) => {
    setSelectedWordDetails(`Details about "${word}"`); // change this to access verify information for the given source text, should display the factuality, confidence, context, and sources
    setIsPopupVisible(true);
  };

  const claim = async () => {
    socket.on('claim', (claims_obj) => {
      console.log("claims:", claims_obj);
      // update claims state(s) (add to claims, replace currentClaims) and parse text (thinking of storing claims as dictionary with claim:source text pairs)
    })
  }

  const verify = async () => {
    socket.on('verify', (verify_obj) => {
      console.log("verify:", verify_obj);
      // update verifyResults state (thinking of storing as claim:fact_check_result pairs)
      // change highlight color of the claim's source text to reflect factuality (green for true, yellow for unkown, red for false)
      // move all the text until the claim's source text to previousText (it is now completely fact checked, so can be moved to the "permanent" storage)
    })
  }

  useEffect(() => {
    setTranscription(transcription + " " + transcript)
  }, [transcript]);

  const parseTranscription = (text) => {
    const phrasesToHighlight = currentClaims.values;

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
            style={styles.highlightBox} // change this to have dynamic highlight color, should be gray by default (check fact check doc for how)
          >
            <Text style={styles.highlightText}>{match}</Text>
          </Pressable>
        );

        // Update remainingText to only the after part
        remainingText = after;
      }
    });

    // Push any remaining unprocessed text
    if (remainingText)
      result.push(<Text key={remainingText}>{remainingText}</Text>);

    setProcessingText((prevText) => [...prevText, ...result]) // add to processingText
    setTranscription("") // resets transcription
  };

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <View style={{ flex: 1 }}>
        <ScrollView 
          ref={scrollViewRef}
          onContentSizeChange={() => 
            scrollViewRef.current?.scrollToEnd({ animated: true })
          }
          style={styles.transcriptionBox}
        >
          <Text>{[...previousText, <Text key={processingText}>{processingText}</Text>, <Text key={transcription}>{transcription}</Text>]}</Text>
        </ScrollView>
        {isRecording ? (
            <TouchableOpacity style={styles.button} onPress={stopTranscribe}>
              <Text>{"Stop"}</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity style={styles.button} onPress={startTranscribe}>
              <Text>{"Start"}</Text>
            </TouchableOpacity>
        )}
        <Modal visible={isPopupVisible} transparent={true}>
          <View style={styles.popup}>
            <Text>{selectedWordDetails}</Text>
            <TouchableOpacity onPress={() => setIsPopupVisible(false)}>
              <Text>Close</Text>
            </TouchableOpacity>
          </View>
        </Modal>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  transcriptionBox: {
    flex: 1,
    padding: 10,
    backgroundColor: "#ffffffff",
    margin: 10,
    marginTop: -30,
  },
  button: {
    padding: 10,
    backgroundColor: "#007AFF",
    alignItems: "center",
    margin: 10,
    marginBottom: 90,
    borderRadius: 5,
  },
  highlightBox: {
    backgroundColor: "yellow",
    borderRadius: 5,
    padding: 2,
    marginHorizontal: 2,
  },
  highlightText: {
    fontWeight: "bold",
    color: "black",
  },
  popup: {
    margin: 20,
    padding: 20,
    backgroundColor: "#fff",
    borderRadius: 10,
    shadowColor: "#000",
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
});

export default MainScreen;
