function toggleForm() {
    const loginForm = document.querySelector('.login-form');
    const signupForm = document.querySelector('.signup-form');
    
    if (loginForm.style.display === 'none') {
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('currentUser', data.user.username);
            window.location.href = 'home.html';
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert('Error connecting to server');
    }
}

async function handleSignup(event) {
    event.preventDefault();
    const fullname = document.getElementById('fullname').value;
    const username = document.getElementById('newUsername').value;
    const password = document.getElementById('newPassword').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, fullname })
        });

        const data = await response.json();
        if (response.ok) {
            alert('Registration successful! Please login.');
            toggleForm();
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert('Error connecting to server');
    }
}