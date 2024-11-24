import { StatusBar } from 'expo-status-bar';
import { Text, View, Button } from 'react-native';

import styles from '../styles/RecordScreenStyles';

export default function RecordScreen(props) {
  return (
    <View style={styles.container}>
      <Text>Hello React Native</Text>
      <Button 
        title={"Click me"}
        onPress={() => 
          console.log("Pressed")
        }
      />
      <StatusBar style="auto" />
    </View>
  );
}