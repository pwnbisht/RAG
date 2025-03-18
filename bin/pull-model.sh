#!/bin/bash

# Wait for Ollama to be responsive
until curl -s http://ollama:11434/api/tags; do
  echo "Waiting for Ollama..."
  sleep 1
done

# Check if the model is already pulled
if ! curl -s http://ollama:11434/api/tags | grep -q "llama3.2:1b"; then
  echo "Pulling llama3.2:1b model..."
  curl -X POST http://ollama:11434/api/pull -d '{"name": "llama3.2:1b"}'
  
  # Wait until the model is fully pulled
  while ! curl -s http://ollama:11434/api/tags | grep -q "llama3.2:1b"; do
    echo "Waiting for model to be pulled..."
    sleep 5
  done
  echo "Model pulled successfully."
else
  echo "Model llama3.2:1b is already available."
fi