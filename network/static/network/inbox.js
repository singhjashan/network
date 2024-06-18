// DOM
document.addEventListener("DOMContentLoaded", function () {
    var likedByWhomData = JSON.parse(document.getElementById('likedByWhomData').textContent);
    console.log("likedByWhomData:", likedByWhomData);
    var postElements = document.querySelectorAll(".like-count");

    postElements.forEach(function (postElement) {
        var postId = postElement.id.split("-")[2];
        console.log(postId)
        var like_Count = likedByWhomData[postId] ? likedByWhomData[postId].like_count : 0;
        postElement.textContent = ` ${like_Count}`;
    });
});

// function to get csrf token
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// submit function 

function submit(id) {
    console.log("hlo", id);
    const textarea_Value = document.getElementById(`textarea_${id}`).value;
    const content = document.getElementById(`content_${id}`);
    const modal = document.getElementById(`modal_edit_post${id}`);
    console.log(textarea_Value);
    fetch(`/edit/${id}`, {
        method: "POST",
        headers: { "Content-type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        body: JSON.stringify({
            content: textarea_Value
        })
    })
        .then(response => response.json())
        .then(result => {
            console.log(result);
            content.innerText = result.data;

            modal.classList.remove('show');
            modal.setAttribute('aria-hidden', 'true');
            modal.setAttribute('style', 'display: none');

            const modalBackdrops = document.getElementsByClassName('modal-backdrop');
            for (let i = 0; i < modalBackdrops.length; i++) {
                document.body.removeChild(modalBackdrops[i]);
            }
        });
}


// like function

function like(id) {
    const like_btn = document.getElementById(`${id}`);
    const like_count_element = document.getElementById(`like-count-${id}`); // assuming you have an element with id like this to display like count

    // Check if the post is already liked
    let liked = like_btn.classList.contains('fa-thumbs-down');

    if (liked) {
        // If the post is already liked, unlike it
        fetch(`/un_like/${id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        })
            .then(response => response.json())
            .then(result => {
                console.log(result.message)
                like_btn.classList.remove('fa-thumbs-down')
                like_btn.classList.add('fa-thumbs-up')
                like_count_element.textContent = parseInt(like_count_element.textContent) - 1; // decrement the like count
            })
    }
    else {
        // If the post isn't liked yet, like it
        fetch(`/add_like/${id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        })
            .then(response => response.json())
            .then(result => {
                console.log(result.message)
                like_btn.classList.remove('fa-thumbs-up')
                like_btn.classList.add('fa-thumbs-down')
                like_count_element.textContent = parseInt(like_count_element.textContent) + 1; // increment the like count
            })
    }
}
