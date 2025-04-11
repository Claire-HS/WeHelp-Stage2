const dialog = document.getElementById("dialog")
const loginBtn = document.getElementById("loginBtn");
const logoutBtn = document.getElementById("logoutBtn");
const closeBtnLogin = document.getElementById("close-btn-login");
const closeBtnRegister = document.getElementById("close-btn-register");
const signIn = document.getElementById("login-container");
const signUp = document.getElementById("register-container");
const navList = document.getElementById("navList");
const bookingBtn = document.getElementById("bookingBtn");
  // navList.style.display = "none";

// 開啟/關閉 Dialog
const setDialogHeight = (height) => {
    dialog.style.height = `${height}px`;
};

loginBtn.addEventListener("click", () => {
    dialog.showModal();
    signUp.style.display = "none";
    signIn.style.display = "flex";
    setDialogHeight(275);
});

closeBtnLogin.addEventListener("click", () =>{
    dialog.close();         
});

closeBtnRegister.addEventListener("click", () => {
      dialog.close();         
});

bookingBtn.addEventListener("click", async () => {
  const isLoggedIn = await checkUserStatus();

  if (isLoggedIn) {
    window.location.href = "/booking";
  } else {
    dialog.showModal();
    signUp.style.display = "none";
    signIn.style.display = "flex";
    setDialogHeight(275);
  }
});

//切換Dialog signIn/Up
document.getElementById("switch-to-register").addEventListener("click", function(event){
    event.preventDefault();

    const signUpForm = signUp.querySelector("form");
    signUpForm.reset(); 
    registerMessage.innerHTML="";
    loginMessage.innerHTML="";
    registerMessage.style.display = "none";
    loginMessage.style.display = "none";

    signIn.style.display = "none";
    signUp.style.display = "flex";
    setDialogHeight(332);
});

document.getElementById("switch-to-login").addEventListener("click", function(event){
    event.preventDefault();

    const signInForm = signIn.querySelector("form");
    signInForm.reset();  
    registerMessage.innerHTML="";
    loginMessage.innerHTML="";
    registerMessage.style.display = "none";
    loginMessage.style.display = "none";

    signUp.style.display = "none";
    signIn.style.display = "flex";
    setDialogHeight(275);
})

// 註冊會員
document.getElementById("sign-up").addEventListener("submit", async function(event) {
    event.preventDefault();

    let form = event.target;
    let submitBtn = event.target.querySelector("button");
    submitBtn.disabled = true; 

    const signUpData = {
        name: form.name.value,
        email: form.email.value,
        password: form.password.value
    };

    try { 
        let response = await fetch("/api/user",{
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(signUpData)
        });
        let result = await response.json();

        setDialogHeight(360);
        registerMessage.innerHTML="";
        registerMessage.style.display = "flex";
        registerMessage.classList.remove("success", "error");

        if (response.ok && result.ok) {
        registerMessage.innerHTML="註冊成功，請登入系統";
        registerMessage.classList.add("success");

        } else {
        registerMessage.innerHTML = result.message || "發生未知錯誤";
        registerMessage.classList.add("error");
        }

    } catch (error) {
        console.error("錯誤:", error);
        registerMessage.innerHTML="伺服器連線失敗!";
        registerMessage.classList.add("error");
    } finally {
        submitBtn.disabled = false;
    }
});

// 登入系統
document.getElementById("sign-in").addEventListener("submit", async function(event) {
    event.preventDefault();

    let form = event.target;
    let submitBtn = event.target.querySelector("button");
    submitBtn.disabled = true;

    const signInData = {
      email: form.email.value,
      password: form.password.value
    };

    try {
      let response = await fetch("/api/user/auth",{
        method: "PUT",
        headers: {
          "Content-Type":"application/json"  
        },
        body: JSON.stringify(signInData)
      });
      let result = await response.json();
      console.log(result);


      setDialogHeight(300);
      loginMessage.innerHTML="";
      loginMessage.style.display = "flex";
      loginMessage.classList.remove("success", "error");

      if (response.ok && result.token) {
        localStorage.setItem("jwt_token", result.token); // 存 JWT token 到 localStorage
        loginMessage.innerHTML="登入成功!";
        loginMessage.classList.add("success");

        // 手動關閉
        closeBtnLogin.onclick = () => {
          dialog.close();
          window.location.reload();
          // window.location.href = "/";
        };

        // 自動關閉
        setTimeout(() => {
          dialog.close();
          window.location.reload();
          // window.location.href = "/";
        }, 3000);

      } else {
        loginMessage.innerHTML = result.message || "發生未知錯誤";
        loginMessage.classList.add("error");
      }
    } catch (error) {
      console.error("錯誤:", error);
      loginMessage.innerHTML="伺服器連線失敗!";
      loginMessage.classList.add("error");
    } finally {
      submitBtn.disabled = false;
    }  
});

// 登入狀態檢查
async function checkUserStatus() {
    const token = localStorage.getItem("jwt_token");

    try {
      let response = await fetch("/api/user/auth",{
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });

      let result = await response.json();

      if (result.data) {
        logoutBtn.style.display = "block";
        return true;
        // loginBtn.style.display = "none";
      } else {
        // Token 無效或已過期
        // logoutBtn.style.display = "none";
        loginBtn.style.display = "block";
        localStorage.removeItem("jwt_token");
        return false;
      }
    } catch (error) {
      console.error("錯誤:", error);
      return false;
    } finally {
      navList.style.display = "flex";
    }
}
  
// 登出系統
document.getElementById("logoutBtn").addEventListener("click",() => {
    localStorage.removeItem("jwt_token");
    window.location.reload();
})
