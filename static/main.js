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

document.querySelectorAll(".rating-select").forEach(sel => {
  sel.addEventListener("change", async e => {
    const bookId = e.target.id.split("-")[1];
    const rating = e.target.value;
    const resp = await fetch(`/book/${bookId}/rate`, {
      method: "POST",
      headers: {"Content-Type":"application/x-www-form-urlencoded"},
      body: `rating=${rating}`
    });
    if (!resp.ok) alert("Fehler beim Speichern");
  });
});