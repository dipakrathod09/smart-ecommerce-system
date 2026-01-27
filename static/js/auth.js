function validateRegister() {
    const pwd = document.getElementById("password").value;
    const email = document.getElementById("email").value;
  
    if (!email.includes("@")) {
      alert("Invalid email");
      return false;
    }
  
    if (pwd.length < 6) {
      alert("Password must be at least 6 characters");
      return false;
    }
    return true;
  }
  