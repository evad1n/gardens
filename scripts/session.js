let gardensPage = document.querySelector("main");
let authPage = document.getElementById("auth");
let userGreeting = document.getElementById("user");
let loginButton = document.getElementById("login-button");

let loginEmail = document.getElementById("email");
let loginPassword = document.getElementById("password");
let invalidLogin = document.getElementById("bad-login");

let firstNameInput = document.getElementById("register-first-name");
let lastNameInput = document.getElementById("register-first-name");
let emailInput = document.getElementById("register-email");
let passwordInput = document.getElementById("register-password");
let invalidRegister = document.getElementById("bad-register");


function goToLogin() {
    history.pushState({ page: "login" }, null);
    gardensPage.style.display = "none";
    authPage.style.display = "";

    for (const el of document.querySelectorAll(".register")) {
        el.style.display = "none";
    }
    for (const el of document.querySelectorAll(".login")) {
        el.style.display = "";
    }
}

function login() {
    let email = loginEmail.value;
    let password = loginPassword.value;

    if (email == "" || password == "") {
        invalidLogin.style.display = "block";
        invalidLogin.children[0].innerHTML = "Please fill out all the fields";
    }
    else {
        verifyUser(email, password);
        // Clear fields
        loginEmail.value = "";
        loginPassword.value = "";
    }
}

function goToRegister() {
    history.pushState({ page: "register" }, null);
    gardensPage.style.display = "none";
    authPage.style.display = "";

    for (const el of document.querySelectorAll(".login")) {
        el.style.display = "none";
    }
    for (const el of document.querySelectorAll(".register")) {
        el.style.display = "";
    }
}

function register() {
    let firstName = firstNameInput.value;
    let lastName = lastNameInput.value;
    let email = emailInput.value;
    let password = passwordInput.value;

    if (firstName == "" || lastName == "" || email == "" || password == "") {
        invalidRegister.style.display = "block";
        invalidRegister.children[0].innerHTML = "Please fill out all the fields";
    }
    else {
        addUser(firstName, lastName, email, password);
        // Clear fields
        firstNameInput.value = "";
        lastNameInput.value = "";
        emailInput.value = "";
        passwordInput.value = "";
    }
}

function goToGardens() {
    history.pushState({ page: "gardens" }, null);
    gardensPage.style.display = "";
    authPage.style.display = "none";
    getGardens();
}

/**
 * Creates a new user on the server
 * @param {string} firstName The first name of the new user
 * @param {string} lastName The last name of the new user
 * @param {string} email The email of the new user
 * @param {password} password The password of the new user
 */
function addUser(firstName, lastName, email, password) {
    postData("/users", {
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password,
    }, (response) => {
        // Successful register
        if (response.status == 201) {
            verifyUser(email, password);
        } else {
            invalidRegister.style.display = "block";
            invalidRegister.children[0].innerHTML = "That email has already been used. Kinda cringe that you don't remember your password bro..";
        }
    });
}

// Session user data
let $user = null;

/**
 * Attempt to login with the following credentials
 * @param {sring} email The email to verify against
 * @param {string} password The password to verify against
 */
function verifyUser(email, password) {
    postData("/sessions", {
        email: email,
        password: password,
    }, (response) => {
        // Successful login
        if (response.status == 201) {
            goToGardens();
        } else {
            invalidLogin.style.display = "block";
            invalidLogin.children[0].innerHTML = "Incorrect username or password";
        }
    });
}

function setGreeting(isAuth) {
    if (isAuth) {
        loginButton.style.display = "none";
        userGreeting.style.display = "block";
        userGreeting.children[0].innerHTML = `Hello, <strong>${$user.first_name}</strong>`;
    } else {
        loginButton.style.display = "";
        userGreeting.style.display = "none";
    }
}

function getUserData(callback) {
    getData("/me", (data) => {
        if (data.message) {
            // Not authenticated
            $user = null;
            setGreeting(false);
        } else {
            $user = data;
            setGreeting(true);
        }
        refreshGardens();
        if (callback) {
            callback();
        }
    });
}

function confirmLogout() {
    if (confirm("Do you wish to logout?")) {
        logout();
    }
}

function logout() {
    deleteMember("/sessions", () => {
        getUserData(() => {
            selectGarden(-1);
        });
    });
}