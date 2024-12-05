import {
  AntDesign,
  MaterialIcons,
  MaterialCommunityIcons,
} from "@expo/vector-icons";

export const icons = {
  index: (props) => <AntDesign name="home" size={26} {...props} />,
  history: (props) => (
    <MaterialCommunityIcons name="history" size={26} {...props} />
  ),
  livestream: (props) => <MaterialIcons name="live-tv" size={26} {...props} />,
  profile: (props) => <AntDesign name="user" size={26} {...props} />,
};
