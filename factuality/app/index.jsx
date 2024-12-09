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
import useTranscribe from "../hooks/useTranscribe";

const MainScreen = () => {
  const [transcription, setTranscription] = useState(""); // Store what's currently being transcribed
  const [previousText, setPreviousText] = useState([]); // "Permanent" storage of text that's been fully fact checked
  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [selectedWordDetails, setSelectedWordDetails] = useState("");
  const [claims, setClaims] = useState({}); // All claims that have been made throughout the whole text
  const [currentClaims, setCurrentClaims] = useState({}); // Only the claims for the current parsing cycle
  const [verifyResults, setVerifyResults] = useState({});
  const [processingText, setProcessingText] = useState([]); // Intermediate storage of text that has been parsed but not fact checked
  const [highlightColors, setHighlightColors] = useState({}); // Stores each phrase and the color it should be highlighted (phrase:color pairs)
  const scrollViewRef = useRef(null);
  const [currentClaimsUpdatedByClaim, setCurrentClaimsUpdatedByClaim] =
    useState(false); // Flag to track update source

  const backendURL = "http://11.20.7.208:5000";
  const {
    startTranscribe,
    stopTranscribe,
    isRecording,
    durationMs,
    size,
    transcript,
    socket,
  } = useTranscribe(backendURL);

  // const handleHighlightPress = (phrase) => {
  //   const factResult =
  //     verifyResults[Object.keys(claims).find((key) => claims[key] === phrase)]; // fact result object for the given phrase
  //   print(factResult);
  //   if (factResult) {
  //     setSelectedWordDetails(factResult); // change this to better display the factuality, confidence, context, and sources
  //   } else {
  //     setSelectedWordDetails("Loading...");
  //   }
  //   setIsPopupVisible(true);
  // };

  const handleHighlightPress = (phrase) => {
    const claimKey = Object.keys(claims).find((key) => claims[key] === phrase);
    const factResult = claimKey ? verifyResults[claimKey] : null;

    console.log("Selected phrase:", phrase);
    console.log("Claim Key:", claimKey);
    console.log("Fact Result:", factResult);

    if (factResult) {
      // Properly format and update the selected details
      const details = `
        Factuality: ${factResult.factuality}\n
        Confidence: ${factResult.confidence}\n
        Context: ${factResult.context}\n
        Sources: ${factResult.sources.join(", ")}
      `;
      setSelectedWordDetails(details);
    } else {
      setSelectedWordDetails("Loading or no data available...");
    }

    // Show modal
    setIsPopupVisible(true);
  };

  const claim = async () => {
    socket.on("claim", (claims_obj) => {
      console.log("claims:", claims_obj);
      const newState = { ...currentClaims };
      // update claims state
      claims_obj.forEach((pair) => {
        newState[pair["claim"]] = pair["source_text"]; // stores claim:source_text pairs
      });

      setCurrentClaimsUpdatedByClaim(true);
      setCurrentClaims(newState);
    });
  };

  useEffect(() => {
    // Check if the update comes from the claim
    if (currentClaimsUpdatedByClaim) {
      parseTranscription(transcription);
      console.log("current claims:" + Object.keys(currentClaims));
      console.log("total claims:" + Object.keys(claims));
      const handleHighlightPress = (phrase) => {
        const claimKey = Object.keys(claims).find(
          (key) => claims[key] === phrase
        );
        const factResult = claimKey
          ? verifyResults[claimKey]
          : "nothing received?";

        // console.log("Selected phrase:", phrase);
        // console.log("Claim Key:", claimKey);
        // console.log("Fact Result:", factResult);

        // console.log("json is: " + JSON.stringify(factResult));

        // Accessing the values
        const claim = verify.claim; // "The earth is flat."
        const factCheckResult = verify.fact_check_result; // Object containing factuality, confidence, etc.
        const confidence = factCheckResult.confidence; // 100
        const context = factCheckResult.context; // Detailed context about the claim
        const factuality = factCheckResult.factuality; // "false"
        const sources = factCheckResult.sources; // Array of sources

        // Example Output
        console.log("Claim:", claim);
        console.log("Factuality:", factuality);
        console.log("Confidence:", confidence);
        console.log("Context:", context);
        console.log("Sources:", sources);

        if (factResult) {
          setSelectedWordDetails(
            `Factuality: ${factResult.factuality}\nConfidence: ${factResult.confidence}\nContext: ${factResult.context}\nSources: ${factResult.sources}`
          );
        } else {
          setSelectedWordDetails("Loading or no data available...");
        }
        setIsPopupVisible(true);
      };
      // Reset the flag after parsing
      setCurrentClaimsUpdatedByClaim(false);
    }
  }, [currentClaims, currentClaimsUpdatedByClaim, verifyResults]);

  // helper for verify, extracts the text within an element recursively to account for nested objects
  const extractText = (element) => {
    if (React.isValidElement(element)) {
      // If the element has children, check if the child is a <Text> component
      if (element.props.children) {
        if (Array.isArray(element.props.children)) {
          // If children is an array, recurse through it
          return element.props.children
            .map((child) => extractText(child))
            .join("");
        } else if (React.isValidElement(element.props.children)) {
          // If there's a single child element, recurse into it
          return extractText(element.props.children);
        } else {
          // If the child is raw text, return it
          return element.props.children;
        }
      }
    }
    return ""; // Default return for non-valid elements
  };

  const verify = async () => {
    socket.on("verify", (verify_obj) => {
      console.log("verify:", verify_obj);

      // Update highlight colors
      const colors = { ...highlightColors };
      const factuality = verify_obj["fact_check_result"]["factuality"];
      const color =
        factuality === "true"
          ? "green"
          : factuality === "false"
          ? "red"
          : "yellow";
      colors[claims[verify_obj["claim"]]] = color;
      setHighlightColors(colors);

      // Move fact-checked text to previousText
      const index = processingText.findIndex((element) => {
        const text = extractText(element);
        return text.includes(claims[verify_obj["claim"]]);
      });

      if (index !== -1) {
        const elementsToMove = processingText.slice(0, index + 1);
        const remainingElements = processingText.slice(index + 1);
        setPreviousText((prev) => [...prev, ...elementsToMove]);
        setProcessingText(remainingElements);
      }

      // Update verifyResults
      setVerifyResults((prev) => ({
        ...prev,
        [verify_obj["claim"]]: verify_obj["fact_check_result"],
      }));
    });
  };

  const test = async () => {
    console.log("starting test listening");
    socket.on("test", (test_obj) => {
      console.log(test_obj);
    });
  };

  useEffect(() => {
    if (socket != null) {
      console.log("SOCKET NOT NULL");
      test();
      claim();
      verify();
    }
  }, [socket]);

  useEffect(() => {
    setTranscription(transcription + " " + transcript);
  }, [transcript]);

  const parseTranscription = (text) => {
    const phrasesToHighlight = Object.values(currentClaims);
    console.log("phrases to highlight: " + phrasesToHighlight);
    let result = [];
    let remainingText = text;
    const tempClaims = claims;
    const tempCurrentClaims = currentClaims;

    phrasesToHighlight.forEach((phrase) => {
      const index = remainingText.toLowerCase().indexOf(phrase.toLowerCase());

      if (index !== -1) {
        // Only add a claim to the list of total claims if it has been parsed
        const key = Object.keys(currentClaims).find(
          (key) => currentClaims[key] === phrase
        );

        // Add to claims
        tempClaims[key] = phrase;

        // Delete from currentClaims
        delete tempCurrentClaims[key];

        // Split the text into three parts: before, match, and after
        const before = remainingText.slice(0, index);
        const match = remainingText.slice(index, index + phrase.length);
        const after = remainingText.slice(index + phrase.length);

        // Push the parts to the result array
        if (before)
          result.push(
            <Text key={`${before}-${Date.now() + 1}+${Math.random()}`}>
              {before}
            </Text>
          );
        result.push(
          <Pressable
            key={`${match}-${Date.now()}+${Math.random()}`}
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
      result.push(
        <Text key={`${remainingText}-${Date.now() - 1}+${Math.random()}`}>
          {remainingText}
        </Text>
      );

    setProcessingText((prevText) => [...prevText, ...result]); // add to processingText
    setTranscription(""); // resets transcription
    // Updates claim states
    setClaims(tempClaims);
    setCurrentClaims(tempCurrentClaims);
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
          <Text>
            {[
              ...previousText,
              <Text
                key={`${processingText}-${Date.now() + 1}+${Math.random()}`}
              >
                {processingText}
              </Text>,
              <Text key={`${transcription}-${Date.now() - 1}+${Math.random()}`}>
                {transcription}
              </Text>,
            ]}
          </Text>
        </ScrollView>
        {isRecording ? (
          <TouchableOpacity style={styles.button} onPress={stopTranscribe}>
            <Text>{"Stop"}</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={styles.button}
            onPress={() => {
              startTranscribe();
            }}
          >
            <Text>{"Start"}</Text>
          </TouchableOpacity>
        )}
        {/* <Modal visible={isPopupVisible} transparent={true}>
          <SafeAreaView style={styles.modalContainer}>
            <View style={styles.popup}>
              <Text>{selectedWordDetails}</Text>
              <TouchableOpacity onPress={() => setIsPopupVisible(false)}>
                <Text>Close</Text>
              </TouchableOpacity>
            </View>
          </SafeAreaView>
        </Modal> */}
        <Modal visible={isPopupVisible} transparent={true}>
          <SafeAreaView style={styles.modalContainer}>
            <View style={styles.popup}>
              <Text>{selectedWordDetails}</Text>
              <TouchableOpacity onPress={() => setIsPopupVisible(false)}>
                <Text>Close</Text>
              </TouchableOpacity>
            </View>
          </SafeAreaView>
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
  modalContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0, 0, 0, 0.5)",
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
