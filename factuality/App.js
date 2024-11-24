import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import RecordScreen from './app/screens/RecordScreen'


const Stack = createStackNavigator();

export default function App() {
  console.log("hello world")
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName='Record'>
        <Stack.Screen name='Record' component={RecordScreen} />
      </Stack.Navigator>
    </NavigationContainer>
    // <RecordScreen />
  );
}


