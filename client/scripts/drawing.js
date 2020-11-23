const canvas = document.querySelector("canvas");
const ctx = canvas.getContext("2d");

// Flower sprites are sized for 40
let flowerSize = 40;

// resize canvas while preserving quality
// let heightRatio = 0.6;
// canvas.height = canvas.width * heightRatio;

function createPetal(length, width) {

    const path = new Path2D();
    path.moveTo(0, 0);
    path.lineTo(length * 0.3, -width);
    path.lineTo(length * 0.8, -width);
    path.lineTo(length, 0);
    path.lineTo(length * 0.8, width);
    path.lineTo(length * 0.3, width);
    path.closePath();
    path.moveTo(0, 0);
    path.lineTo(length, 0);

    return path;
}


/**
 * Draws flower petals
 * @param {int} x X coordinate
 * @param {int} y Y coordinate
 * @param {int} count Number of petals
 * @param {int} startAt Angle to start at
 * @param {Path2D} petal Petal to trace
 */
function drawPetals(x, y, count, startAt, petal) {
    const step = (Math.PI * 2) / count;
    ctx.setTransform(1, 0, 0, 1, x, y);
    ctx.rotate(startAt);
    for (let i = 0; i < count; i += 1) {
        ctx.stroke(petal);
        ctx.rotate(step);
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);  // restore default
}


function drawFlower(x, y, size, color, petalCount) {
    // Draw stem
    let radius = size * 15;
    ctx.strokeStyle = "green";
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.arc(x - radius, y, radius, 0, 0.2);
    ctx.stroke();

    // Draw petals
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    drawPetals(x, y, petalCount, 0, createPetal(size, size * 0.2));

    // Draw center
    ctx.beginPath();
    ctx.arc(x, y, size * 0.15, 0, Math.PI * 2);
    ctx.fillStyle = "black";
    ctx.fill();

}

function blueFlower(x, y) {
    drawFlower(x, y, flowerSize, "blue", 6);
}

function redFlower(x, y) {
    drawFlower(x, y, flowerSize, "red", 5);
}

function yellowFlower(x, y) {
    drawFlower(x, y, flowerSize, "yellow", 10);
}

function whiteFlower(x, y) {
    drawFlower(x, y, flowerSize, "white", 7);
}

function purpleFlower(x, y) {
    drawFlower(x, y, flowerSize, "purple", 8);
}


// Dragging and dropping flowers
function getMousePos(canvas, evt) {
    let rect = canvas.getBoundingClientRect(), // abs. size of element
        scaleX = canvas.width / rect.width,    // relationship bitmap vs. element for X
        scaleY = canvas.height / rect.height;  // relationship bitmap vs. element for Y

    return {
        x: (evt.clientX - rect.left) * scaleX,   // scale mouse coordinates after they have
        y: (evt.clientY - rect.top) * scaleY     // been adjusted to be relative to element
    };
}

function addFlower(x, y, id) {
    switch (id) {
        case "blue":
            blueFlower(x, y);
            break;
        case "purple":
            purpleFlower(x, y);
            break;
        case "red":
            redFlower(x, y);
            break;
        case "white":
            whiteFlower(x, y);
            break;
        case "yellow":
            yellowFlower(x, y);
            break;

        default:
            break;
    }
}

function allowDrop(evt) {
    evt.preventDefault();
}

function drag(evt) {
    evt.dataTransfer.setData("id", evt.target.id);
}

function drop(evt) {
    evt.preventDefault();
    console.log("drop event");

    // Get flower type
    let id = evt.dataTransfer.getData("id");

    // If this is the canvas
    if (evt.target.id == "canvas") {
        let pos = getMousePos(canvas, evt);
        // push locally
        currentGarden.flowers.push({
            color: id,
            x: pos.x,
            y: pos.y
        });
        addFlower(pos.x, pos.y, id);
        console.log("adding flower");

        // Set alert status to changes not saved
        saveAlert.children[1].style.display = "block";
        saveAlert.children[1].innerHTML = "Changes not saved";
    }
}

let sizeSlider = document.querySelector("#flower-size");

sizeSlider.oninput = () => {
    flowerSize = sizeSlider.value;
    refreshFlowers(true);
};

// Reference to compare changes to
let oldFlowers = [];

/**
 * Draw flowers from current garden flowers list
 */
function refreshFlowers() {
    // clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (currentGarden != null) {
        currentGarden.flowers.forEach(flower => {
            addFlower(flower.x, flower.y, flower.color);
        });
    }
}

// Deleting flowers
let erasing = false;

canvas.onclick = function (evt) {
    if (erasing) {
        let pos = getMousePos(canvas, evt);

        // Determine if a flower was clicked and delete it if it was
        currentGarden.flowers.forEach(flower => {
            if (flowerClicked(pos, flower)) {
                currentGarden.flowers.splice(currentGarden.flowers.indexOf(flower), 1);
                // Set alert status to changes not saved
                saveAlert.children[1].style.display = "block";
                saveAlert.children[1].innerHTML = "Changes not saved";
            }
        });
    }

    refreshFlowers(true);
};

/**
 * Determines if a flower was clicked
 * @param {object} clickPos The mouse click position
 * @param {object} flower The flower to check against
 */
function flowerClicked(clickPos, flower) {
    let width = 2 * flowerSize;
    let height = 2 * flowerSize;

    if (clickPos.x > flower.x - (width / 2) && clickPos.x < flower.x + (width / 2)) {
        if (clickPos.y > flower.y - (height / 2) && clickPos.y < flower.y + (height / 2)) {
            return true;
        }
    }
    return false;
}

/* Adds erasing cursor. */
function toggleErasing() {
    erasing = !erasing;
    if (erasing) {
        canvas.classList.add("erasing");
    } else {
        canvas.classList.remove("erasing");
    }
}

// https://stackoverflow.com/questions/34075113/what-is-the-default-cursor-icon-for-delete