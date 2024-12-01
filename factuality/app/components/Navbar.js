import React, { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons"; // Install expo/vector-icons or use any icon library

const Navbar = ({ transcription }) => {
  // Extract the first 10 characters of the transcription
  const title = transcription.substring(0, 10);

  return (
    <View style={styles.navbar}>
      {/* Home Button */}
      <TouchableOpacity style={styles.homeButton}>
        <Ionicons name="home" size={24} color="black" />
      </TouchableOpacity>

      {/* Title */}
      <Text style={styles.title}>{title.length > 0 ? title : "App Title"}</Text>

      {/* Hamburger Menu */}
      <TouchableOpacity style={styles.menuButton}>
        <Ionicons name="menu" size={24} color="black" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  navbar: {
    position: "absolute", // Ensures the navbar is positioned relative to the screen
    top: 0, // Places the navbar at the top
    left: 0, // Aligns the navbar to the left
    right: 0, // Ensures it spans the entire width
    height: 60, // Set a fixed height for the navbar
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 10,
    backgroundColor: "#f8f9fa",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
    zIndex: 10, // Ensures it stays on top of other elements
  },
  homeButton: {
    padding: 10,
  },
  title: {
    fontSize: 18,
    fontWeight: "bold",
    textAlign: "center",
    flex: 1, // Ensures the title takes the remaining space
    marginHorizontal: 10, // Space between buttons and title
  },
  menuButton: {
    padding: 10,
  },
});

export default Navbar;
