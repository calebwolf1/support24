import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function FetchScreen() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const backendURL = 'http://192.168.1.71:5000';
    fetch(backendURL)
      .then((response) => response.text()) // Assuming Flask returns plain text
      .then((data) => {
        setMessage(data);
      })
      .catch((error) => {
        console.error('Error fetching from backend:', error);
      });
  }, []);
  

  return (
    <View style={styles.container}>
      <Text style={styles.text}>{message || 'Loading...'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    fontSize: 20,
  },
});
