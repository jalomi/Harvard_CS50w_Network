document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#edit-button').forEach(element => {
        element.addEventListener('click', event => edit_post(event.target));
    });
  });

function edit_post(button) {
    if (button.innerText == "Edit") {
        const content_obj = button.parentElement.querySelector('.post-content');
        const content = content_obj.innerText;

        content_obj.innerHTML = `<textarea id="post-textarea">${content}</textarea>`

        button.innerText = "Save"
    }
    else if (button.innerText == "Save") {
        const parent = button.parentElement;
        const content = parent.querySelector('#post-textarea').value;
        parent.querySelector('.post-content').innerHTML = content;
        button.innerText = "Edit";
        save_edit(parent.dataset.postid, content);
    }
}

function save_edit(id, content) {
    console.log("save_edit")
    console.log(id)

    fetch(`/edit/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            content: content,
        }),
        headers: { "X-CSRFToken": CSRF_TOKEN },
      })
}