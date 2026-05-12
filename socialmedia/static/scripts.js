//------signup
document.getElementById("signupbtn")?.addEventListener("click", async () => {
  const addname = document.getElementById("addname").value.trim();
  const addpassword = document.getElementById("addpassword").value.trim();

  if (!addname || !addpassword) return alert("Enter both fields");

  try {
    const res = await fetch("/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ addname, addpassword }),
    });

    const data = await res.json(); // ✅ IMPORTANT

    if (data.message === "saved successfully") {
      document.getElementById("login").click();
      alert("saved successfully");
    } else {
      alert("Username already taken");
    }
  } catch (err) {
    console.error(err);
    alert("Error connecting to server");
  }
});

document.getElementById("addname")?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    document.getElementById("addpassword").focus();
  }
});

// enter key for sign up
document
  .getElementById("addpassword")
  ?.addEventListener("keydown", async (event) => {
    const addname = document.getElementById("addname").value.trim();
    const addpassword = document.getElementById("addpassword").value.trim();

    if (event.key === "Enter") {
      if (!addname || !addpassword) return alert("Enter both fields");
      try {
        const res = await fetch("/add", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ addname, addpassword }),
        });

        const data = await res.json(); // ✅ IMPORTANT

        if (data.message === "saved successfully") {
          document.getElementById("login").click();
          alert("saved successfully");
        } else {
          alert("Username already taken");
        }
      } catch (err) {
        console.error(err);
        alert("Error connecting to server");
      }
    }
  });

// ---------- LOGIN ----------
document
  .getElementById("loginbtn")
  ?.addEventListener("click", async (event) => {
    event.preventDefault(); // prevent default form submit

    const name = document.getElementById("name").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!name || !password) return alert("Enter both fields");

    try {
      const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, password }),
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

document.getElementById("name")?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    document.getElementById("password").focus();
  }
});

//enter key for login
document
  .getElementById("password")
  ?.addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
      event.preventDefault(); // prevent default form submit
      const name = document.getElementById("name").value.trim();
      const password = document.getElementById("password").value.trim();

      if (!name || !password) return alert("Enter both fields");

      try {
        const res = await fetch("/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, password }),
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
      body: JSON.stringify({ content }),
    });

    const data = await res.json();

    if (data.error) return alert(data.error);
    savedText = "";
    inputText.value = savedText;
    localStorage.setItem("savedText", savedText);
    if (data.message) location.reload();
  } catch (err) {
    console.error(err);
    alert("Error posting. See console.");
  }
});

//enter key for posting
document
  .querySelector(".postInput")
  ?.addEventListener("keydown", async (event) => {
    const content = document.querySelector(".postInput").value;

    if (event.key === "Enter") {
      if (!content) return alert("Write something!");
      try {
        const res = await fetch("/posts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content }),
        });

        const data = await res.json();
        if (data.error) return alert(data.error);
        savedText = "";
        inputText.value = savedText;
        localStorage.setItem("savedText", savedText);
        if (data.message) location.reload();
      } catch (err) {
        console.error(err);
        alert("Error posting. See console.");
      }
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
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ newname }),
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
    body: JSON.stringify({ desc }),
  });

  const data = await res.json();

  if (data.message) {
    alert(data.message);
  } else {
    alert(data.error || "Failed to update description.");
  }
});

// enter key for desc editing
document.getElementById("desc")?.addEventListener("keydown", async (event) => {
  if (event.key === "Enter") {
    const desc = document.getElementById("desc").value.trim();
    if (!desc) return alert("Description cannot be empty!");

    const res = await fetch("/descupdate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ desc }),
    });

    const data = await res.json();

    if (data.message) {
      alert(data.message);
    } else {
      alert(data.error || "Failed to update description.");
    }
  }
});

// reloading the homepage for live messaging

setInterval(async () => {
  if (window.location.pathname === "/showposts") {
    await location.reload();
  }
}, 18000);
