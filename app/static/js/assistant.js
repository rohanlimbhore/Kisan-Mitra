const form = document.getElementById('chatForm');
const input = document.getElementById('chatInput');
const messages = document.getElementById('chatMessages');

function addMessage(text, role) {
  const bubble = document.createElement('div');
  bubble.className = `message ${role}`;
  bubble.textContent = text;
  messages.appendChild(bubble);
  messages.scrollTop = messages.scrollHeight;
}

form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const value = input.value.trim();
  if (!value) return;

  addMessage(value, 'user');
  input.value = '';

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: value }),
    });

    const data = await response.json();
    if (!response.ok) {
      addMessage(data.error || 'Unable to process request.', 'bot');
      return;
    }

    addMessage(data.reply, 'bot');
  } catch (error) {
    addMessage('Server connection failed. Please try again.', 'bot');
  }
});
