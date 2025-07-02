function openBookDetail(bookId) {
  fetch(`/book/${bookId}?modal=true`)
    .then(response => response.text())
    .then(html => {
      const modalBody = document.getElementById("modal-body");
      const overlay = document.getElementById("modal-overlay");
      modalBody.innerHTML = html;
      overlay.style.display = "flex";
    });
}

function closeModal() {
  const overlay = document.getElementById("modal-overlay");
  const modalBody = document.getElementById("modal-body");
  overlay.style.display = "none";
  modalBody.innerHTML = "";
}

function openAuthorDetail(authorId) {
  fetch(`/author/${authorId}?modal=true`)
    .then(response => response.text())
    .then(html => {
      const modalBody = document.getElementById("modal-body");
      const overlay = document.getElementById("modal-overlay");
      modalBody.innerHTML = html;
      overlay.style.display = "flex";
    });
}