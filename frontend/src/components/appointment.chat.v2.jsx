import React, { useState } from 'react';
import ChatMessages from './chat.messages';
import {sendMessage} from '../services/appointment.v2.service';


function AppointmentChat(props) {
    const [messages, setMessages] = useState([]);
    const [wppNumber, setWppNumber] = useState('');
    const [message, setMessage] = useState('');

    const handleChange = (e) => {
        setMessage(e.target.value);
      };
    
    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() !== '') {
        send(message);
        setMessage('');
        }
    };
    const send = (message)=>{
        sendMessage(wppNumber, message).then(result=>{if (result) setMessages(result)})
    }
    const handleWppChange = (e) => {
      setWppNumber(e.target.value);
    };


    return (
      <div className="chat">
        Appointment v2
        <br/><input
            value={wppNumber}
            onChange={handleWppChange}
        />
        <form onSubmit={handleSubmit}>
            <input
            type="text"
            value={message}
            onChange={handleChange}
            placeholder="Type your message..."
            className="chat-input"
            />
            <button type="submit" className="send-button">
            Send
            </button>
        </form>
        <ChatMessages messages={messages}/>
      </div>
    );
  }

export default AppointmentChat;
