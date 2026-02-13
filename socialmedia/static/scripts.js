// ---------- SIGNUP ----------
document.getElementById("signupbtn")?.addEventListener("click", async () => {
    const addname = document.getElementById("addname").value.trim();
    const addpassword = document.getElementById("addpassword").value.trim();

    const res = await fetch("/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ addname, addpassword })
    });

    const data = await res.json();
    alert(data.message || data.error);
});

// ---------- LOGIN ----------
document.getElementById("loginBtn")?.addEventListener("click", async () => {
    const name = document.getElementById("name").value.trim();
    const password = document.getElementById("password").value.trim();

    const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, password })
    });

    const data = await res.json();

    if (data.message === "login successfull") {
        window.location.href = "/showposts";
    } else {
        alert("Invalid login");
    }
});

// ---------- POSTS ----------
document.getElementById("postBtn")?.addEventListener("click", async () => {
    const content = document.getElementById("post").value;
    if (!content) return alert("Write something!");

    const res = await fetch("/posts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content })
    });

    const data = await res.json();
    if (data.message) location.reload();
});
