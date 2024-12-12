// Placeholder for future functionality
// Function to show the login popup
function showLoginPopup() {
    document.getElementById('loginPopup').style.display = 'block';
}

// Function to hide the login popup
function hideLoginPopup() {
    document.getElementById('loginPopup').style.display = 'none';
}

// // Function to handle login (you'll need to implement this)
// function login() {
//     const username = document.getElementById('username').value;
//     const password = document.getElementById('password').value;
//     // Implement your login logic here
//     console.log('Login attempted with:', username, password);
//     // After successful login, you might want to redirect or update the UI
// }

// Function to navigate to signup pages
function navigateTo(url) {
    window.location.href = url;
}

// Close the popup if the user clicks outside of it
window.onclick = function (event) {
    const popup = document.getElementById('loginPopup');
    if (event.target == popup) {
        hideLoginPopup();
    }
}

function closePopup() {
    document.getElementById("loginPopup").style.display = "none";
}

// Function to open the login popup
document.getElementById("loginSignupButton").addEventListener("click", function () {
    document.getElementById("loginPopup").style.display = "block";
});

// Function to close the popup
function closePopup() {
    document.getElementById("loginPopup").style.display = "none";
}

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const userType = document.getElementById('user_type').value;

    if (!username || !password) {
        alert('Please enter both username and password.');
        return;
    }

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password,
            user_type: userType
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Navigate to the correct dashboard based on user type
                window.location.href = "/dashboard";
            } else {
                alert(data.message || 'Invalid login credentials.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error processing login. Please try again.');
        });
}



// Open login/signup popup
document.getElementById('loginSignupButton').onclick = function () {
    document.getElementById('loginPopup').style.display = 'block';
}

// Close the popup
function closePopup() {
    document.getElementById('loginPopup').style.display = 'none';
}


// Function to navigate to different pages
function navigateTo(url) {
    window.location.href = url;
}

const room = "{{ session['user'] }}";
socket.emit('join_room', { room: room, username: "{{ session['user'] }}" });

socket.on('receive_message', (data) => {
    const messageContainer = document.getElementById('message-container');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.innerText = `${data.username}: ${data.message}`;
    messageContainer.append(messageElement);
    messageContainer.scrollTop = messageContainer.scrollHeight;
});


// Add event listener to the login/signup button
document.addEventListener('DOMContentLoaded', function () {
    const loginButton = document.getElementById('loginSignupButton');
    if (loginButton) {
        loginButton.addEventListener('click', showLoginPopup);
    }
});