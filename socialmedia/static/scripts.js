//------signup
document.getElementById("signupbtn")?.addEventListener("click", async () => {
    const addname = document.getElementById("addname").value.trim();
    const addpassword = document.getElementById("addpassword").value.trim();

        const res = await fetch("/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ addname, addpassword })
        });

        const data = await res.json(); // ✅ IMPORTANT

        if (data.message === "saved successfully") {
            alert("saved successfully");
        } else {
            alert("Error. Try again later");
        }
});


// ---------- LOGIN ----------
document.getElementById("loginbtn")?.addEventListener("click", async (event) => {
    event.preventDefault(); // prevent default form submit

    const name = document.getElementById("name").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!name || !password) return alert("Enter both fields");

    try {
        const res = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, password })
        });

        const data = await res.json();

        if (data.message === "login successfull") {
            window.location.href = "/showposts";
        } else {
            alert(data.message || data.error || "Invalid login");
        }
    } catch (err) {
        alert("Error connecting to server");
        console.error(err);
    }
});


console.log("Sign-Log script loaded successfully!");

//---------- CREATE POST ----------

document.getElementById("postBtn")?.addEventListener("click", async () => {
    const content = document.getElementById("post").value;
    if (!content) return alert("Write something!");

    try {
        const res = await fetch("/posts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content })
        });

        const data = await res.json();
        if (data.error) return alert(data.error);
        if (data.message) location.reload();
    } catch (err) {
        console.error(err);
        alert("Error posting. See console.");
    }
});


// ---------- FRIEND REQUEST ----------
// Send Friend Request
document.getElementById("sendRequestBtn")?.addEventListener("click", async () => {
    const friendId = document.getElementById("friendId").value.trim();
    if (!friendId) return alert("Enter a valid friend ID!");

    const res = await fetch("/send_friend_request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ friendId })
    });

    const data = await res.json();
    alert(data.message || data.error);
});

// Accept Friend Request
document.getElementById("acceptRequestBtn")?.addEventListener("click", async () => {
    const requestId = document.getElementById("requestId").value.trim();
    if (!requestId) return alert("Enter a valid request ID!");

    const res = await fetch("/accept_friend_request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ requestId })
    });

    const data = await res.json();
    alert(data.message || data.error);
});

// ---------- SEARCH FRIEND ----------
document.getElementById("who")?.addEventListener("input", async (event) => {
    const query = event.target.value.trim();
    const resultsContainer = document.getElementById("searchResults");

    if (!query) {
        resultsContainer.innerHTML = ""; // Clear results
        return;
    }

    const res = await fetch(`/searchbar?who=${encodeURIComponent(query)}`);
    const data = await res.json();

    if (data && data.length > 0) {
        resultsContainer.innerHTML = data.map(user => `
            <div class="search-result">
                <img src="static/images/${user.imgpath}" alt="Profile">
                <p>${user.name}</p>
                <button onclick="sendFriendRequest(${user.user_id})">Add Friend</button>
            </div>
        `).join("");
    } else {
        resultsContainer.innerHTML = "<p>No users found</p>";
    }
});

// ---------- EDIT NAME ----------
document.getElementById("saveNameBtn")?.addEventListener("click", async () => {
    const newname = document.getElementById("newname").value.trim();

    if (!newname) {
        return alert("Enter a name!");
    }

    const res = await fetch("/editname", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ newname })
    });

    const data = await res.json();

    alert(data.message || data.error);

    if (data.message) {
        window.location.href = "/profile"; // go back after success
    }
});

//---------- EDIT DESCRIPTION ----------
document.getElementById("saveDescBtn")?.addEventListener("click", async () => {
    const desc = document.getElementById("desc").value.trim();
    if (!desc) return alert("Description cannot be empty!");

    const res = await fetch("/descupdate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ desc })
    });

    const data = await res.json();

    if (data.message) {
        alert(data.message);
    } else {
        alert(data.error || "Failed to update description.");
    }
});


