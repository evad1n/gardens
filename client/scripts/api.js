const URL = "http://localhost:8080";

/**
 * Gets data from server
 * @param {string} route The route to GET from
 * @param {function} callback Optional callback when done
 */
function getData(route, callback) {
    fetch(`${URL}${route}`, {
        credentials: "include",
    })
        .then(response => {
            if (response.ok) {
                response.json()
                    .then(data => {
                        console.log("getData -> data", data);
                        if (callback)
                            callback(data);
                    });
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert(`Server Error: ${error}`);
        });
}

/**
 * Posts data to server with specified route and data
 * @param {string} route The route to POST to
 * @param {object} data The data to post
 * @param {function} callback Optional callback when done
 */
function postData(route, data, callback) {
    // Convert data to x-www-form-urlencoded format
    data = new URLSearchParams(data);

    fetch(`${URL}${route}`, {
        method: 'POST',
        credentials: "include",
        body: data,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => {
            console.log('Response:', response);
            if (callback)
                callback(response);
        })
        .catch((error) => {
            console.error('Error:', error);
            alert(`Server Error: ${error}`);
        });
}

/**
 * Updates a member of a collection
 * @param {string} route The route to specifying the collection and member to update
 * @param {object} data The new data to update to
 * @param {function} callback Optional callback when done
 */
function updateMember(route, data, callback) {
    // Convert data to x-www-form-urlencoded format
    data = new URLSearchParams(data);

    fetch(`${URL}${route}`, {
        method: 'PUT',
        credentials: "include",
        body: data,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => {
            console.log('Response:', response);
            if (callback)
                callback();
        })
        .catch((error) => {
            console.error('Error:', error);
            alert(`Server Error: ${error}`);
        });
}

/**
 * Deletes a member of a collection
 * @param {string} route The route to specifying the collection and member to delete
 * @param {function} callback Optional callback when done
 */
function deleteMember(route, callback) {
    fetch(`${URL}${route}`, {
        method: 'DELETE',
        credentials: "include",
    })
        .then(response => {
            console.log('Response:', response);
            if (callback)
                callback();
        })
        .catch((error) => {
            console.error('Error:', error);
            alert(`Server Error: ${error}`);
        });
}

function getUserData() {
    getData("/me", (response) => {
        if (response.status == 200) {
            response.json().then(data => {
                setGreeting(data);
            });
        } else {
            // Not logged in

        }
    });
}

/**
 * Adds a new garden and switches to the newly created garden
 * @param {string} name The name of the new garden
 * @param {string} author The author of the new garden
 */
function addGarden(name, author) {
    postData("/gardens", {
        name: name,
        author: author
    }, (response) => {
        response.json().then(data => {
            getGardens(() => {
                selectGarden(data.id);
            });
        });
    });
}

/**
 * Changes the name of an existing garden
 * @param {string} name The new name of the garden
 */
function updateGarden(name) {
    updateMember(`/gardens/${currentGarden.id}`, {
        name: name,
    }, () => {
        getGardens(() => {
            selectGarden(currentGarden.id);
        });
    });
}

function deleteGarden() {
    deleteMember(`/gardens/${currentGarden.id}`, () => {
        getGardens(() => {
            selectGarden(-1);
        });
    });
}

function getComments() {
    getData(`/gardens/${currentGarden.id}`, (data) => {
        currentGarden.comments = data.comments;
        refreshComments();
    });
}

/**
 * Adds a comment to the current garden
 * @param {string} comment The text content of the comment
 */
function addComment(comment) {
    postData("/comments", {
        gardenId: currentGarden.id,
        content: comment
    }, () => {
        getComments();
    });
}

function deleteComment(commentId) {
    deleteMember(`/comments/${commentId}`, () => {
        getComments();
    });
}

function getFlowers() {
    getData(`/gardens/${currentGarden.id}`, (data) => {
        currentGarden.flowers = data.flowers;
        oldFlowers = [...data.flowers];
        refreshFlowers();
    });
}

/** Update server flowers with the currentGarden flowers */
function saveFlowers() {
    // Keep track of saving progress
    let changeCounter = 0;
    let numChanges = 0;
    // Show saving icon animation
    saveAlert.children[0].style.display = "block";
    saveAlert.children[1].innerHTML = "Saving..";

    // function to check if a flower exists in a list
    function exists(list, el) {
        for (const l of list) {
            if (l.id == el.id)
                return true;
        }
        return false;
    }

    // Get server flowers
    console.log(oldFlowers);
    console.log(currentGarden.flowers);
    // If it has been deleted
    oldFlowers.forEach(flower => {
        if (!exists(currentGarden.flowers, flower)) {
            numChanges++;
            deleteMember(`/flowers/${flower.id}`, () => {
                changeCounter++;
                doneSaving(changeCounter, numChanges);
            });
        }
    });

    // If it has been added
    currentGarden.flowers.forEach(flower => {
        if (!exists(oldFlowers, flower)) {
            numChanges++;
            postData("/flowers", {
                gardenId: currentGarden.id,
                color: flower.color,
                x: flower.x,
                y: flower.y
            }, () => {
                changeCounter++;
                doneSaving(changeCounter, numChanges);
            });
        }
    });

    doneSaving(changeCounter, numChanges);
}

function doneSaving(current, needed) {
    console.log(`counter: ${current}`);
    if (current == needed) {
        console.log("refreshing flowers");
        getFlowers();
        saveAlert.children[0].style.display = "none";
        saveAlert.children[1].innerHTML = "Saved!";
    }
}