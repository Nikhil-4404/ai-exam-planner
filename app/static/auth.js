const registerForm = document.querySelector("#register-form");
const loginForm = document.querySelector("#login-form");
const authStatus = document.querySelector("#auth-status");
const authTabs = document.querySelectorAll(".auth-tab");

if (authTabs.length > 0) {
  authTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      authTabs.forEach(t => t.classList.remove("active-tab"));
      tab.classList.add("active-tab");
      
      if (tab.dataset.target === "login-form") {
        loginForm.classList.remove("hidden");
        registerForm.classList.add("hidden");
      } else {
        registerForm.classList.remove("hidden");
        loginForm.classList.add("hidden");
      }
    });
  });
}

const postJson = async (url, payload) => {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed." }));
    throw new Error(error.detail || "Request failed.");
  }

  return response.status === 204 ? null : response.json();
};

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(registerForm);

  try {
    authStatus.textContent = "Creating account...";
    authStatus.dataset.variant = "loading";
    await postJson("/api/auth/register", {
      name: formData.get("name"),
      email: formData.get("email"),
      password: formData.get("password"),
    });
    window.location.href = "/planner";
  } catch (error) {
    authStatus.textContent = error.message;
    authStatus.dataset.variant = "error";
  }
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);

  try {
    authStatus.textContent = "Logging you in...";
    authStatus.dataset.variant = "loading";
    await postJson("/api/auth/login", {
      email: formData.get("email"),
      password: formData.get("password"),
    });
    window.location.href = "/planner";
  } catch (error) {
    authStatus.textContent = error.message;
    authStatus.dataset.variant = "error";
  }
});
