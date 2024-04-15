import React from 'react';


const ChatMessages = ({ messages }) => {
    return (
      <div className="chat-messages-container">
        {messages.map((msg, index) => (
          <div key={index} className="message">
            {msg["human"]!==undefined?msg["human"]: 'Response: '+ msg["ai"]}
          </div>
        ))}
      </div>
    );
  };  

export default ChatMessages;