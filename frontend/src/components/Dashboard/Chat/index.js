"use client";

import { useState } from "react";
import {
  Card,
  Form,
  Button,
  Dropdown,
  OverlayTrigger,
  Tooltip,
} from "react-bootstrap";
import ReactMarkdown from "react-markdown";


const DocumentChat = ({ documentId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (input.trim() === "") return;

    // Add user's message to the chat
    const userMessage = {
      text: input,
      sender: "user",
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}docs/${documentId}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: input }),
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();
      const botMessage = {
        text: data.response,
        sender: "bot",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        { text: "Error: Could not get response", sender: "bot", timestamp: new Date().toISOString() },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    let hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    const minutesStr = minutes < 10 ? `0${minutes}` : minutes;
    return `${hours}:${minutesStr} ${ampm}`;
  };

  return (
    <Card className="bg-white border-0 rounded-3 h-100">
      <Card.Body className="p-4 d-flex flex-column h-100">
        {/* Chat Messages */}
        <ul className="mb-0 list-unstyled chat-details flex-grow-1 overflow-auto pe-2">
          {messages.length > 0 ? (
            messages.map((msg, index) => (
              <li key={index} className={`mb-4 ${msg.sender === "user" ? "ms-auto own-chat" : ""}`}>
                <div className={`d-sm-flex ${msg.sender === "user" ? "text-end" : ""}`}>
                  {msg.sender !== "user" && (
                    <div className="flex-shrink-0">
                      {/* Placeholder for bot avatar if desired */}
                    </div>
                  )}
                  <div className="flex-grow-1 ms-sm-3 mt-3 mt-sm-0">
                    <div
                      className={`d-flex align-items-center ${
                        msg.sender === "user" ? "justify-content-end" : ""
                      }`}
                    >
                      {msg.sender === "user" && (
                        <Dropdown className="action-opt me-2">
                          <Dropdown.Toggle
                            variant="secondary"
                            id={`dropdown-${index}`}
                            className="bg-transparent p-0"
                          >
                            <i className="ri-more-2-fill text-secondary"></i>
                          </Dropdown.Toggle>
                          <Dropdown.Menu className="bg-white border box-shadow">
                            <Dropdown.Item href="#">Reply</Dropdown.Item>
                            <Dropdown.Item href="#">Delete You</Dropdown.Item>
                          </Dropdown.Menu>
                        </Dropdown>
                      )}
                      {msg.sender === "bot" ? (
                        <div className="bot-msg">
                          <ReactMarkdown>{msg.text}</ReactMarkdown>
                        </div>
                      ) : (
                        <p>{msg.text}</p>
                      )}
                      {msg.sender !== "user" && (
                        <Dropdown className="action-opt ms-2">
                          <Dropdown.Toggle
                            variant="secondary"
                            id={`dropdown-${index}`}
                            className="bg-transparent p-0"
                          >
                            <i className="ri-more-2-fill text-secondary"></i>
                          </Dropdown.Toggle>
                          <Dropdown.Menu className="bg-white border box-shadow">
                            <Dropdown.Item href="#">Reply</Dropdown.Item>
                            <Dropdown.Item href="#">Delete You</Dropdown.Item>
                          </Dropdown.Menu>
                        </Dropdown>
                      )}
                    </div>
                    <span className="fs-12 d-block">{formatTimestamp(msg.timestamp)}</span>
                  </div>
                </div>
              </li>
            ))
          ) : (
            <li className="text-center text-muted">Start chatting about Document {documentId}</li>
          )}
          {isLoading && (
            <li className="mb-4">
              <div className="d-sm-flex">
                <div className="flex-grow-1 ms-sm-3 mt-3 mt-sm-0">
                  <p className="text-muted mb-0">Thinking...</p>
                </div>
              </div>
            </li>
          )}
        </ul>

        {/* Message Input */}
        <div className="d-sm-flex justify-content-between align-items-center bg-gary-light for-dark rounded-3 p-4">
          <div className="d-flex gap-3 justify-content-center justify-content-sm-start">
            <OverlayTrigger placement="top" overlay={<Tooltip>Emoji</Tooltip>}>
              <button className="p-0 border-0 bg-transparent">
                <i className="ri-emotion-laugh-line fs-18 text-body"></i>
              </button>
            </OverlayTrigger>
            <OverlayTrigger placement="top" overlay={<Tooltip>Link</Tooltip>}>
              <button className="p-0 border-0 bg-transparent">
                <i className="ri-link-m fs-18 text-body"></i>
              </button>
            </OverlayTrigger>
          </div>
          <Form
            className="w-100 ps-sm-4 ps-xxl-4 ms-xxl-3 mt-3 mt-sm-0 position-relative"
            onSubmit={sendMessage}
          >
            <Form.Control
              type="text"
              className="rounded-1 border-2 text-dark h-55"
              placeholder="Type your message"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <Button
              variant="primary"
              className="p-0 border-0 bg-transparent position-absolute top-50 end-0 translate-middle-y pe-3 d-sm-none"
              type="submit"
              disabled={isLoading}
            >
              <span className="material-symbols-outlined fs-24 text-primary">send</span>
            </Button>
          </Form>
          <Button
            variant="primary"
            className="p-0 border-0 bg-primary d-none d-sm-block rounded-1 ms-3"
            type="submit"
            disabled={isLoading}
          >
            <span className="material-symbols-outlined text-white wh-55 lh-55 d-inline-block">
              send
            </span>
          </Button>
        </div>
      </Card.Body>
    </Card>
  );
};

export default DocumentChat;