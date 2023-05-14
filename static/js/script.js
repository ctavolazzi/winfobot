document.getElementById('message-form').addEventListener('submit', function(event) {
  event.preventDefault();  // Prevents the form from submitting normally

  var input = document.getElementById('input');
  var message = input.value;
  input.value = '';

  var messages = document.getElementById('messages');

  // Add the user's message to the chat
  messages.innerHTML += '<p>You: ' + message + '</p>';

  // Add a loading message for the AI
  messages.innerHTML += '<p>AI: Loading...</p>';

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/chat');
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
      if (xhr.status === 200) {
          var response = JSON.parse(xhr.responseText);

          // Remove the loading message
          messages.removeChild(messages.lastChild);

          // Add the AI's response to the chat
          messages.innerHTML += '<p>' + response.message + '</p>';
          messages.scrollTop = messages.scrollHeight;
      }
  };
  xhr.send(encodeURI('message=' + message));
});

document.getElementById('send').addEventListener('click', function(event) {
  event.preventDefault();  // Prevents the button's click event from dispatching the form's submit event
  document.getElementById('message-form').dispatchEvent(new Event('submit'));
});
