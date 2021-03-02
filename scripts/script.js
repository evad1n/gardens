let title = document.querySelector("#title");
let author = document.querySelector("#author");
let gardenList = document.querySelector("#gardens-list");
let commentList = document.querySelector("#comments-list");
let saveAlert = document.querySelector("#saving-container");

/** The current garden object */
let currentGarden = null;

/** Local object to store serve data in for the session */
gardens = [];

// Get initial data and setup
function init() {
    goToGardens();
}

init();

/**
 * Refreshes local gardens with server data
 * @param {function} callback Optional callback when done
 */
function getGardens(callback) {
    selectGarden(currentGarden == null ? -1 : currentGarden.id);
    getData("/gardens", (gardensInfo) => {
        gardens = gardensInfo;
        // Wait for user data before updaitng UI
        getUserData(callback);

    });
}

/**
 * Select a garden based on id and update page info with new garden info
 * @param {Integer} id The id of the garden to select
 */
function selectGarden(gardenId) {
    // Go to no selection screen
    if (gardenId == -1) {
        currentGarden = null;
        refreshComments();
        refreshFlowers();
        showControls(false, false);
        allowEditing(false);
    }
    else {
        getData(`/gardens/${gardenId}`, data => {
            currentGarden = data;
            oldFlowers = [...data.flowers];
            refreshGarden();
            showControls(true, $user != null);
            allowEditing($user && $user.id == currentGarden.author_id);
            // Turn erasing off
            if (erasing) {
                toggleErasing();
                document.getElementById("erasing").checked = false;
            }
        });
    }
}

function refreshGarden() {
    title.childNodes[0].nodeValue = currentGarden.name;
    author.innerHTML = currentGarden.author;

    refreshComments();
    refreshFlowers();

    // Remove saving alert
    saveAlert.children[0].style.display = "none";
    saveAlert.children[1].style.display = "none";
}

/** Create user gardens list based on server data */
function refreshGardens() {
    // Clear previous gardens
    gardenList.innerHTML = "";

    if ($user != null) {
        // If there are no gardens
        if ($user.gardens.length == 0) {
            let item = document.createElement("li");
            item.innerHTML = 'You have no gardens yet!';
            item.style.fontWeight = "bold";
            item.style.fontSize = "1.2rem";
            item.style.marginTop = "10px";
            item.style.textAlign = "center";
            gardenList.appendChild(item);
        } else {
            // Get new gardens
            $user.gardens.forEach(garden => {
                let item = document.createElement("li");
                item.innerHTML = `<strong>${garden.name}</strong> by ${garden.author}`;
                item.classList.add("garden-list-item");
                item.classList.add("list-item");
                item.onclick = () => { selectGarden(garden.id); };

                gardenList.appendChild(item);
            });
        }
    } else {
        let item = document.createElement("li");
        item.innerHTML = 'Please login to see your gardens';
        item.style.fontWeight = "bold";
        item.style.fontSize = "1.2rem";
        item.style.marginTop = "10px";
        item.style.textAlign = "center";
        gardenList.appendChild(item);
    }
}

/** Create comments list based on server data */
function refreshComments() {
    // Clear previous comments
    commentList.innerHTML = "";
    // if no comments
    if (currentGarden == null || currentGarden.comments.length == 0) {
        let item = document.createElement("li");
        item.innerHTML = 'There are no comments yet!';
        item.style.fontWeight = "bold";
        item.style.fontSize = "1.2rem";
        item.style.marginTop = "10px";
        item.style.textAlign = "center";
        item.style.hove;
        commentList.appendChild(item);
    }
    else {
        // Get new comments
        currentGarden.comments.forEach(comment => {
            let item = document.createElement("li");
            item.innerHTML = `<strong>${comment.author}</strong>: ${comment.content}`;
            item.classList.add('list-item');
            item.classList.add('comment-list-item');
            item.onclick = () => { showCommentModal(comment, $user && $user.id == comment.author_id); };

            commentList.appendChild(item);
        });
    }
}

/** Make sure the comment body isn't empty */
function validateComment() {
    let input = document.querySelector("#input-comment");

    if ($user != null) {
        if (currentGarden == null) {
            alert("Please select a garden to add comments");
        }
        else {
            if (input.value != "") {
                addComment(input.value);
                input.value = "";
            }
            else {
                alert("Please enter a comment!");
            }
        }
    }
    else {
        alert("Please login to comment on gardens!");
    }
}

/**
 * Shows the garden editing controls and hides "no-garden" disclaimer
 * @param {bool} show Whether to show controls or not
 */
function showControls(show, auth) {
    let noGardenElements = document.querySelectorAll(".no-garden");

    noGardenElements.forEach(el => {
        el.style.display = show ? "none" : "";
    });

    let haveGardenElements = document.querySelectorAll(".have-garden");

    haveGardenElements.forEach(el => {
        el.style.display = show ? "" : "none";
    });


    let noAuthGardenElements = document.querySelectorAll(".no-auth-garden");

    noAuthGardenElements.forEach(el => {
        el.style.display = !auth && show ? "" : "none";
    });

    let yourGardenElements = document.querySelectorAll(".have-auth-and-your-garden");

    yourGardenElements.forEach(el => {
        el.style.display = show && auth && $user.id == currentGarden.author_id ? "" : "none";
    });

    let notYourGardenElements = document.querySelectorAll(".not-your-garden");

    notYourGardenElements.forEach(el => {
        el.style.display = show && auth && $user.id != currentGarden.author_id ? "" : "none";
    });
}

/**
 * Allows editing controls
 * @param {bool} allow Whether to allow editing or not
 */
function allowEditing(allow) {
    let editControls = document.querySelectorAll(".edit");

    editControls.forEach(control => {
        control.style.display = allow ? "" : "none";
    });
}
