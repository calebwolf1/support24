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
  const [claims, setClaims] = useState({}); // All claims that have been made throughout the whole text
  const [currentClaims, setCurrentClaims] = useState({}); // Only the claims for the current parsing cycle
  const [verifyResults, setVerifyResults] = useState([]);
  const [processingText, setProcessingText] = useState([]); // Intermediate storage of text that has been parsed but not fact checked
  const [highlightColors, setHighlightColors] = useState({}); // Stores each phrase and the color it should be highlighted (phrase:color pairs)
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
      const before = currentClaims;
      // update claims state
      claims_obj.forEach((pair) => {
        console.log("current claim: " + pair['claim'] + ":" + pair['source_text']);
        setCurrentClaims(prevCurrentClaims => {
          const newState = {
            ...prevCurrentClaims,
            [pair['claim']]: pair['source_text'],
          };
          console.log(newState); // This will log the updated state
          return newState;
        });
      });

      while (Object.keys(before) == Object.keys(currentClaims)) {
        console.log("waiting");
      }
      console.log(currentClaims);
      parseTranscription(transcription);
    });
  }

  const verify = async () => {
    socket.on('verify', (verify_obj) => {
      console.log("verify:", verify_obj);
      // update verifyResults state (thinking of storing as claim:fact_check_result pairs)
      // change highlight color of the claim's source text to reflect factuality (green for true, yellow for unkown, red for false, check fact check doc for how)
      // move all the text until the claim's source text to previousText (it is now completely fact checked, so can be moved to the "permanent" storage)
    })
  }

  const test = async () => {
    console.log('starting test listening');
    socket.on('test', (test_obj) => {
      console.log(test_obj)
    });
  }

  useEffect(() => {
    if(socket != null) {
      console.log("SOCKET NOT NULL");
      test();
      claim();
      verify();
    }
  }, [socket]);

  useEffect(() => {
    setTranscription(transcription + " " + transcript)
  }, [transcript]);

  const parseTranscription = (text) => {
    const phrasesToHighlight = Object.values(currentClaims);

    let result = [];
    let remainingText = text;

    phrasesToHighlight.forEach((phrase) => {
      const index = remainingText.toLowerCase().indexOf(phrase.toLowerCase());

      if (index !== -1) {
        // Only add a claim to the list of total claims if it has been parsed
        const key = Object.keys(currentClaims).find(key => currentClaims[key] === phrase);
        // Add to cliams
        setClaims((prevClaims) => ({
          ...prevClaims,
          [key]: phrase,
        }));
        // Delete from currentClaims
        setCurrentClaims((prevCurrentClaims) => {
          const newClaims = {...prevCurrentClaims};
          delete newClaims[key];
          return newClaims;
        });      

        // Split the text into three parts: before, match, and after
        const before = remainingText.slice(0, index);
        const match = remainingText.slice(index, index + phrase.length);
        const after = remainingText.slice(index + phrase.length);

        // Push the parts to the result array
        if (before) result.push(<Text key={`${before}-${Date.now()}`}>{before}</Text>);
        result.push(
          <Pressable
            key={`${match}-${Date.now()}`}
            onPress={() => handleHighlightPress(match)}
            style={[
              styles.highlightBox,
              { backgroundColor: highlightColors[phrase] || "gray" }, // Dynamic color
            ]}
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
      result.push(<Text key={`${remainingText}-${Date.now()}`}>{remainingText}</Text>);

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
          <Text>{[...previousText, <Text key={`${processingText}-${Date.now()+1}`}>{processingText}</Text>, <Text key={`${transcription}-${Date.now()-1}`}>{transcription}</Text>]}</Text>
        </ScrollView>
        {isRecording ? (
            <TouchableOpacity style={styles.button} onPress={stopTranscribe}>
              <Text>{"Stop"}</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity style={styles.button} onPress={() => {startTranscribe();}}>
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
    backgroundColor: "gray",
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
