async function checkAuth() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/posts', {
            credentials: 'include'
        });
        if (!response.ok) {
            window.location.href = 'index.html';
        }
    } catch (error) {
        window.location.href = 'index.html';
    }
}

checkAuth();

async function logout() {
    try {
        await fetch('http://127.0.0.1:5000/api/logout', {
            method: 'POST',
            credentials: 'include'
        });
        localStorage.removeItem('currentUser');
        window.location.href = 'index.html';
    } catch (error) {
        alert('Error logging out');
    }
}

async function createPost() {
    const content = document.getElementById('postContent').value;
    if (!content.trim()) return;

    try {
        const response = await fetch('http://127.0.0.1:5000/api/posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ content })
        });

        if (response.ok) {
            document.getElementById('postContent').value = '';
            loadPosts();
        } else {
            const data = await response.json();
            alert(data.error);
        }
    } catch (error) {
        alert('Error creating post');
    }
}

async function loadPosts() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/posts', {
            credentials: 'include'
        });
        const data = await response.json();
        
        const postsContainer = document.getElementById('posts');
        postsContainer.innerHTML = '';
        
        data.posts.forEach(post => {
            const postElement = document.createElement('div');
            postElement.className = 'post';
            postElement.innerHTML = `
                <div class="post-header">
                    <span class="post-author">${post.author.fullname}</span>
                    <span class="post-time">${new Date(post.created_at).toLocaleString()}</span>
                </div>
                <div class="post-content">
                    ${post.content}
                </div>
            `;
            postsContainer.appendChild(postElement);
        });
    } catch (error) {
        alert('Error loading posts');
    }
}

// Load posts when page loads
loadPosts();

// Display username
document.getElementById('userName').textContent = localStorage.getItem('currentUser');