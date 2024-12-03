import {useState, useEffect} from 'react';
import {io} from 'socket.io-client';

/**
 * On mount, connect to the socket.io server
 * @param {*} url 
 * @param {*} handleData 
 * @returns 
 */
export default function useWebSocket(url, handleData) {
  const [socket, setSocket] = useState(null);

  useEffect(() => {

    // Connect to the flask server
    const socketClient = io(url);

    socketClient.on('connect', () => {
      console.log('Connected to server');
    });

    socketClient.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    // To make the hook more generic, accept a handleData
    // function that is passed to the socket.
    socketClient.on('data', (data) => {
      handleData(data);
    });

    setSocket(socketClient);

    // On unmount, close the socket
    return () => {
      socketClient.close();
    }
  }, []);

  return socket
}