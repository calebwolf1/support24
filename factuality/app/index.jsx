import React, { useState, useRef, useEffect } from "react";
import {
  View,
  ScrollView,
  Text,
  TouchableOpacity,
  StyleSheet,
  Pressable,
  Modal,
  Linking,
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

  const handleHighlightPress = (phrase) => {
    const claimKey = Object.keys(claims).find((key) => claims[key] === phrase);
    const factResult = claimKey ? verifyResults[claimKey] : null;

    console.log("Selected phrase:", phrase);
    console.log("Claim Key:", claimKey);
    console.log("Fact Result:", factResult);

    if (factResult) {
      // Properly format and update the selected details
      // const details = `
      //   Factuality: ${factResult.factuality}\n
      //   Confidence: ${factResult.confidence}\n
      //   Context: ${factResult.context}\n
      //   Sources: ${factResult.sources.join(", ")}
      // `;
      const details = {
        factuality: factResult.factuality || "Unknown",
        confidence: factResult.confidence || "Unknown",
        context: factResult.context || "No context available",
        sources: Array.isArray(factResult.sources)
          ? factResult.sources
          : ["No sources available"],
      };
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
      // Reset the flag after parsing
      setCurrentClaimsUpdatedByClaim(false);
    }
  }, [currentClaims, currentClaimsUpdatedByClaim]);

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

  useEffect(() => {
    for (const key in highlightColors) {
      console.log(key + ": " + highlightColors[key]);
    }
    // Regenerate processingText to reflect new highlight colors
    setProcessingText((prevText) =>
      prevText.map((element) => {
        if (React.isValidElement(element) && element.props.onPress) {
          const phrase = extractText(element);
          console.log(phrase);
          console.log(highlightColors[phrase]);
          return (
            <Pressable
              key={phrase + Math.random()}
              onPress={() => handleHighlightPress(phrase)}
              style={[
                styles.highlightBox,
                { backgroundColor: highlightColors[phrase] || "gray" },
              ]}
            >
              <Text style={styles.highlightText}>{phrase}</Text>
            </Pressable>
          );
        }
        return element; // Non-Pressable elements remain unchanged
      })
    );
  }, [highlightColors]); // Run this effect when highlightColors updates

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
      // Update the highlightColors by merging with the existing state
      const claimText = claims[verify_obj["claim"]];
      setHighlightColors((prevColors) => ({
        ...prevColors, // Retain existing colors
        [claimText]: color, // Add or update the color for the current claim
      }));

      // Find the index of the element
      const index = processingText.findIndex((element) => {
        const text = extractText(element);
        return text.includes(claims[verify_obj["claim"]]);
      });

      if (index !== -1) {
        // Schedule the movement to happen after the re-render
        setTimeout(() => {
          setProcessingText((prevText) => {
            const elementsToMove = prevText.slice(0, index + 1);
            const remainingElements = prevText.slice(index + 1);

            // Move fact-checked text to previousText
            setPreviousText((prev) => [...prev, ...elementsToMove]);

            return remainingElements; // Update processingText
          });
        }, 0); // Allow one render cycle for highlight color to update
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
          <Text style={{ fontSize: 20 }}>
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
        <Modal visible={isPopupVisible} transparent={true}>
          <SafeAreaView style={styles.modalContainer}>
            <View style={styles.popup}>
              {selectedWordDetails ? (
                <View>
                  <Text style={{ fontSize: 17 }}>
                    <Text style={{ fontWeight: "bold" }}>Factuality:</Text>{" "}
                    {selectedWordDetails.factuality}
                    {"\n"}
                  </Text>
                  <Text style={{ fontSize: 17 }}>
                    <Text style={{ fontWeight: "bold" }}>Confidence:</Text>{" "}
                    {selectedWordDetails.confidence}
                    {"\n"}
                  </Text>
                  <Text style={{ fontSize: 17 }}>
                    <Text style={{ fontWeight: "bold" }}>Context:</Text>{" "}
                    {selectedWordDetails.context}
                    {"\n"}
                  </Text>
                  <Text
                    style={{ fontWeight: "bold", marginTop: 10, fontSize: 16 }}
                  >
                    Sources:
                  </Text>
                  {selectedWordDetails.sources.map((source, index) => (
                    <View
                      key={index}
                      style={{
                        flexDirection: "row",
                        alignItems: "flex-start",
                        marginVertical: 2,
                      }}
                    >
                      <Text style={{ marginRight: 5 }}>•</Text>
                      <Text
                        style={{
                          color: "blue",
                          textDecorationLine: "underline",
                          fontSize: 16,
                        }}
                        onPress={() => Linking.openURL(source)}
                      >
                        {source}
                      </Text>
                    </View>
                  ))}
                </View>
              ) : (
                <Text>Loading or no data available...</Text>
              )}
              <TouchableOpacity
                onPress={() => setIsPopupVisible(false)}
                style={{
                  padding: 10,
                  paddingTop: 10,
                  backgroundColor: "#007BFF", // Button color
                  borderRadius: 5, // Rounded corners
                  alignItems: "center", // Center text horizontally
                  justifyContent: "center", // Center text vertically
                  marginTop: 20, // Optional, adds space above the button
                }}
              >
                <Text
                  style={{
                    color: "white", // Text color
                    fontWeight: "bold", // Make text bold
                    fontSize: 16, // Adjust font size
                  }}
                >
                  Close
                </Text>
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
    padding: 15,
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
  },
  highlightText: {
    fontWeight: "bold",
    color: "black",
    fontSize: 18, // Match this with the font size of regular transcript text
    lineHeight: 20,
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
