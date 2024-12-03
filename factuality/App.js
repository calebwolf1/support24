import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import RecordScreen from './app/screens/RecordScreen'
import TestScreen from './app/screens/TestScreen'
import FetchScreen from './app/screens/FetchScreen'


const Stack = createStackNavigator();

export default function App() {
  console.log("hello world")
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName='Record'>
        <Stack.Screen name='Record' component={TestScreen} />
      </Stack.Navigator>
    </NavigationContainer>
    // <RecordScreen />
  );
}


