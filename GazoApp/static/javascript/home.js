document.addEventListener('DOMContentLoaded', function () {
    const followButtons = document.querySelectorAll('.follow-btn, .unfollow-btn');

    followButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const user_id = this.getAttribute('data-user');
            const url = this.classList.contains('follow-btn') ? '/follow/' : '/unfollow/';
            const notification_url = '/notification';

            fetch(url + user_id, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }).then(function (response) {
                if (url == '/follow/') {
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-danger');
                    button.classList.remove('follow-btn');
                    button.classList.add('unfollow-btn');
                    button.textContent = 'Unfollow';

                    const notif_type = 'follow'
                    const user_to_be_notified_id = user_id;
                    const post_id = -1;
                    const notificationData = { notif_type, user_to_be_notified_id, post_id };

                    fetch(notification_url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify(notificationData)
                    }).then(function (response) {
                        if (response.ok) {
                            console.log('Notification sent successfully');
                        } else {
                            console.log('Failed to send notification');
                        }
                    }).catch(function (error) {
                        console.log(error);
                    });

                } else {
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-primary');
                    button.classList.remove('unfollow-btn');
                    button.classList.add('follow-btn');
                    button.textContent = 'Follow';
                }
            }).catch(function (error) {
                console.log(error);
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const starButtons = document.querySelectorAll('.star-btn');

    starButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const button = this;
            const post_id = this.getAttribute('data-post');
            const this_post_id = this.getAttribute('data-post-id');
            const post_user_id = this.getAttribute('post_user_id');
            const url = '/star/' + post_id;
            const notification_url = '/notification';

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }).then(function (response) {
                if (response.ok) {
                    const starCountElement = document.querySelector(`.star-count-${this_post_id}`);
                    const currentStarCount = parseInt(starCountElement.textContent);
                    const newStarCount = button.classList.contains('starred') ? currentStarCount - 1 : currentStarCount + 1;
                    starCountElement.textContent = newStarCount;

                    if (button.classList.contains('starred')) {
                        button.classList.remove('starred');
                        button.innerHTML = '<i class="fa-regular fa-star fa-lg"></i>';
                    } else {
                        const notif_type = 'star'
                        const user_to_be_notified_id = post_user_id;
                        const notificationData = { notif_type, user_to_be_notified_id, post_id };

                        fetch(notification_url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: JSON.stringify(notificationData)
                        }).then(function (response) {
                            if (response.ok) {
                                console.log('Notification sent successfully');
                            } else {
                                console.log('Failed to send notification');
                            }
                        }).catch(function (error) {
                            console.log(error);
                        });
                        button.classList.add('starred');
                        button.innerHTML = '<i class="fa-solid fa-star fa-lg" style="color: rgb(41, 156, 194);"></i>';
                    }
                } else {
                    console.log('Failed to update star status');
                }
            }).catch(function (error) {
                console.log(error);
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const reshareButtons = document.querySelectorAll('.reshare-btn');

    reshareButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const button = this;
            const post_id = this.getAttribute('data-post');
            const this_post_id = this.getAttribute('data-post-id');
            const post_user_id = this.getAttribute('post_user_id');
            const url = '/reshare/' + post_id;
            const notification_url = '/notification';

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }).then(function (response) {
                if (response.ok) {
                    const reshareCountElement = document.querySelector(`.reshare-count-${this_post_id}`);
                    const currentReshareCount = parseInt(reshareCountElement.textContent);
                    const newReshareCount = button.classList.contains('reshared') ? currentReshareCount - 1 : currentReshareCount + 1;
                    reshareCountElement.textContent = newReshareCount;

                    if (button.classList.contains('reshared')) {
                        button.classList.remove('reshared');
                        button.innerHTML = '<i class="fa-solid fa-retweet fa-lg"></i>';
                    } else {
                        const notif_type = 'reshare'
                        const user_to_be_notified_id = post_user_id;
                        const notificationData = { notif_type, user_to_be_notified_id, post_id };

                        fetch(notification_url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: JSON.stringify(notificationData)
                        }).then(function (response) {
                            if (response.ok) {
                                console.log('Notification sent successfully');
                            } else {
                                console.log('Failed to send notification');
                            }
                        }).catch(function (error) {
                            console.log(error);
                        });

                        button.classList.add('reshared');
                        button.innerHTML = '<i class="fa-solid fa-retweet fa-lg" style="color: rgb(41, 156, 194);"></i>';
                    }
                } else {
                    console.log('Failed to update reshare status');
                }
            }).catch(function (error) {
                console.log(error);
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const commentButtons = document.querySelectorAll('.cmt-btn');

    commentButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const button = this;
            const post_id = this.getAttribute('data-post-id');
            const post_user_id = this.getAttribute('post_user_id');
            const url = '/comment/' + post_id;
            const commentsList = document.querySelector('#commentsModal .comments-list');
            const addANote = document.querySelector('#addANote');
            const postCommentBtn = document.querySelector('#postCommentBtn');
            const notification_url = '/notification';

            fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }).then(function (response) {
                return response.json();
            }).then(function (data) {
                commentsList.innerHTML = '';
                data.forEach(function (comment) {
                    const newComment = document.createElement('div');
                    newComment.classList.add('card-4', 'mb-1', 'p-1');
                    newComment.style.border = '0.3px solid lightgray';
                    newComment.setAttribute('id', `comment-${comment.id}`);
                    newComment.innerHTML = `
                                <div class="card-body">
                                    <p>${comment.description}</p>
                                    <div class="d-flex justify-content-between">
                                        <div class="d-flex flex-row align-items-center">
                                            <button class="btn p-0 mr-1 "  onclick="window.location.href='/profile/${comment.user.id}'">
                                                <img src="${comment.user.profile_pic_url}" alt="avatar" width="25" height="25" />
                                            </button>
                                            <button class="btn p-0" onclick="window.location.href='/profile/${comment.user.id}'">
                                                <p class="small mb-0 ms-2">${comment.user.username}</p>
                                            </button>
                                        </div>
                                        <div class="d-flex flex-row align-items-center">
                                            <p class="small text-muted mb-0 mr-1">${comment.date_created}</p>
                                            ${comment.user.id == comment.current_user.id ?
                            '<button class="btn p-0" onclick="deleteComment(' + comment.id + ')"><i class="fas fa-trash" style="color: red;"></i></button>'
                            :
                            ''
                        }   
                                        </div>
                                    </div>
                                </div>
                            `;
                    commentsList.appendChild(newComment);
                });
            });

            function handlePostComment() {
                const commentBody = addANote.value.trim();
                if (commentBody) {
                    const notif_type = 'comment'
                    const user_to_be_notified_id = post_user_id;
                    const notificationData = { notif_type, user_to_be_notified_id, post_id };

                    fetch(notification_url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify(notificationData)
                    }).then(function (response) {
                        if (response.ok) {
                            console.log('Notification sent successfully');
                        } else {
                            console.log('Failed to send notification');
                        }
                    }).catch(function (error) {
                        console.log(error);
                    });
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({
                            commentBody: commentBody
                        })
                    }).then(function (response) {
                        return response.json();
                    }).then(function (data) {
                        data.forEach(function (comment) {
                            const newComment = document.createElement('div');
                            newComment.classList.add('card-4', 'mb-1', 'p-1');
                            newComment.style.border = '0.3px solid lightgray';
                            newComment.setAttribute('id', `comment-${comment.id}`);
                            console.log(comment.user.id)
                            console.log("hi")
                            console.log(comment.current_user.id)
                            newComment.innerHTML = `
                                        <div class="card-body">
                                            <p>${comment.description}</p>
                                            <div class="d-flex justify-content-between">
                                                <div class="d-flex flex-row align-items-center">
                                                    <button class="btn p-0 mr-1 "  onclick="window.location.href='/profile/${comment.user.id}'">
                                                        <img src="${comment.user.profile_pic_url}" alt="avatar" width="25" height="25" />
                                                    </button>
                                                    <button class="btn p-0" onclick="window.location.href='/profile/${comment.user.id}'">
                                                        <p class="small mb-0 ms-2">${comment.user.username}</p>
                                                    </button>
                                                </div>
                                                <div class="d-flex flex-row align-items-center">
                                                    <p class="small text-muted mb-0 mr-1">${comment.date_created}</p>
                                                    ${comment.user.id == comment.current_user.id ?
                                    '<button class="btn p-0" onclick="deleteComment(' + comment.id + ')"><i class="fas fa-trash" style="color: red;"></i></button>'
                                    :
                                    ''
                                }   
                                                </div>
                                            </div>
                                        </div>
                                    `;
                            commentsList.insertAdjacentElement('afterbegin', newComment);
                            addANote.value = '';
                        });
                    });
                }
            }

            postCommentBtn.addEventListener('click', handlePostComment);

            const closeModalBtn = document.querySelector('#closeModalBtn');

            closeModalBtn.addEventListener('click', function () {
                postCommentBtn.removeEventListener('click', handlePostComment);
            });
        });
    });
});

function deleteComment(commentId) {
    fetch(`/comment/${commentId}/delete`, {
        method: 'DELETE',
    })
        .then(response => {
            if (response.ok) {
                const commentElem = document.getElementById(`comment-${commentId}`);
                commentElem.remove();
            } else {
                console.error('Error deleting comment:', response);
            }
        })
        .catch(error => {
            console.error('Error deleting comment:', error);
        });
}

document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('.deletepost-btn');

    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const button = this;
            const post_id = this.getAttribute('data-post-id');
            const url = `/deletepost/${post_id}`;

            // show confirmation modal before deleting post
            $('#deletepostModal').modal('show');

            const deleteButton = document.querySelector('#deletePostBtn');
            const cancelButton = document.querySelector('#cancelButton');

            cancelButton.addEventListener('click', function (event) {
                event.preventDefault();
                // hide confirmation modal when cancel button is clicked
                $('#deletepostModal').modal('hide');
            });
            deleteButton.addEventListener('click', function (event) {
                event.preventDefault();
                fetch(url, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                }).then(function (response) {
                    if (response.ok) {
                        // remove post from the page
                        button.closest('.post').remove();
                        // hide confirmation modal after deleting post
                        $('#deletepostModal').modal('hide');
                    } else {
                        console.log('Failed to delete post');
                    }
                }).catch(function (error) {
                    console.log(error);
                });
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const aiButtons = document.querySelectorAll('.ai-analysis-btn');

    aiButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const modal = document.getElementById('analysisModal');
            const post_id = this.getAttribute('data-post-id');
            const notesList = modal.querySelector('.notes-list');
            notesList.innerHTML = '<div style="text-align: center; padding: 20px;"><i class="fa fa-spinner fa-spin fa-3x"></i></div>';

            fetch(`/ai/${post_id}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    notesList.innerHTML = '';
                    const labels = data.labels.join(', ');
                    notesList.insertAdjacentHTML('beforeend', `<p><strong>Labels:</strong><p>${labels}</p></p>`);
                    if (data.expressions != "No expressions found") {
                        const expressions = data.expressions.join(', ');
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Expressions:</strong><p>${expressions}</p></p>`);
                    }
                    else {
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Expressions: </strong>${data.expressions}</p>`);
                    }
                    if (data.landmarks != "No landmarks found") {
                        const landmarks = data.landmarks.join(', ');
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Landmarks:</strong><p>${landmarks}</p></p>`);
                    }
                    else {
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Landmarks: </strong>${data.landmarks}</p>`);
                    }

                    if (data.logos != "No logos found") {
                        const logos = data.logos.join(', ');
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Logos:</strong><p>${logos}</p></p>`);
                    }
                    else {
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Logos: </strong>${data.logos}</p>`);
                    }

                    const safeSearch = data.safeSearch.join(', ');
                    notesList.insertAdjacentHTML('beforeend', `<p><strong>Safe Search:</strong><p>${safeSearch}</p></p>`);

                    if (data.text != "No text found") {
                        const text = data.text.join(', ');
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Text:</strong><p>${text}</p></p>`);
                    }
                    else {
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Text: </strong>${data.text}</p>`);
                    }

                    if (data.localizedObject != "No objects found") {
                        const localizedObjects = data.localizedObject.join(', ');
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Localized Objects:</strong> ${localizedObjects}</p>`);
                    }
                    else {
                        notesList.insertAdjacentHTML('beforeend', `<p><strong>Localized Objects: </strong> ${data.localizedObject}</p>`);
                    }
                })
                .catch(error => {
                    console.error(error);
                    notesList.innerHTML = `<p>${error.message}</p>`;
                });
        });
    });
});
