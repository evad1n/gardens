// Create garden modal
let createGardenModal = document.querySelector("#create-garden-modal");
let createGardenBtn = document.querySelector("#create");
let createGardenClose = document.querySelector("#create-garden-close");

createGardenBtn.onclick = function () {
    if ($user != null) {
        createGardenModal.style.display = "block";
    } else {
        alert("Please login to start creating gardens");
    }
};

createGardenClose.onclick = function () {
    createGardenModal.style.display = "none";
};

/**
 * Make sure the name and author field aren't empty.
 */
function validateCreateGarden() {
    let gardenName = document.querySelector("#create-garden-name").value;

    if (gardenName != "") {
        // Close modal
        createGardenModal.style.display = "none";
        addGarden(gardenName, $user.first_name);
    }
    else {
        alert("Please enter a name for your garden!");
    }
}



// Edit garden modal
let editGardenModal = document.querySelector("#edit-garden-modal");
let editGardenClose = document.querySelector("#edit-garden-close");
let editGardenBtn = document.querySelector("#edit-garden");

let editGardenName = document.querySelector("#edit-garden-name");

editGardenBtn.onclick = function () {
    editGardenName.value = currentGarden.name;
    editGardenModal.style.display = "block";
};

function validateEditGarden() {
    let gardenName = document.querySelector("#edit-garden-name").value;

    if (gardenName != "") {
        editGardenModal.style.display = "none";
        updateGarden(gardenName);
    }
    else {
        alert("Please enter a name!");
    }
}

function confirmDeleteGarden() {
    if (confirm(`Are you sure you want to delete this garden?`)) {
        editGardenModal.style.display = "none";
        deleteGarden();
    }
}

editGardenClose.onclick = function () {
    editGardenModal.style.display = "none";
};



// Comment modal
let commentModal = document.querySelector("#comment-modal");
let commentClose = document.querySelector("#comment-close");

let commentAuthor = document.querySelector("#comment-author");
let commentContent = document.querySelector("#comment-content");

let currentComment = null;

/**
 * Activates the comment info modal
 * @param {Object} comment comment to display in the modal 
 */
function showCommentModal(comment, owner) {
    let delButton = document.getElementById("delete-comment");
    delButton.style.display = owner ? "" : "none";
    commentModal.style.display = "block";
    commentAuthor.innerHTML = comment.author;
    commentContent.innerHTML = comment.content;
    currentComment = comment;
}

function confirmDeleteComment() {
    if (confirm(`Are you sure you want to remove the comment:\n${currentComment.content}`)) {
        commentModal.style.display = "none";
        deleteComment(currentComment.id);
        currentComment = null;
    }
}

commentClose.onclick = function () {
    commentModal.style.display = "none";
};



// Clicking outside modal will close it
window.onclick = function (event) {
    if (event.target == createGardenModal) {
        createGardenModal.style.display = "none";
        // Clear fields
        document.querySelector("#create-garden-name").value = "";
    }
    if (event.target == editGardenModal) {
        editGardenModal.style.display = "none";
        // Clear fields
        document.querySelector("#edit-garden-name").value;
    }
    if (event.target == commentModal) {
        commentModal.style.display = "none";
    }
};