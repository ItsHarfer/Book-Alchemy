function openBookDetail(bookId) {
  fetch(`/book/${bookId}?modal=true`)
    .then(response => response.text())
    .then(html => {
      modalBody.innerHTML = html;
      editModal.classList.remove("hidden");
      document.body.classList.add("modal-open");
    });
}


function openAuthorDetail(authorId) {
  fetch(`/author/${authorId}?modal=true`)
    .then(response => response.text())
    .then(html => {
      modalBody.innerHTML = html;
      editModal.classList.remove("hidden");
      document.body.classList.add("modal-open");
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
    if (!resp.ok) alert("Error while rating book.");
  });
});

document.querySelectorAll(".read-toggle").forEach(cb => {
  cb.addEventListener("change", async e => {
    const id = e.target.dataset.bookId;
    const isRead = e.target.checked;
    await fetch(`/book/${id}/status`, {
      method: "POST",
      headers: {"Content-Type":"application/x-www-form-urlencoded"},
      body: `is_read=${isRead}&progress=${document.querySelector("#progress-"+id).value}`
    });
  });
});


document.querySelectorAll(".progress-slider").forEach(slider => {
  slider.addEventListener("input", e => {
    const id = e.target.dataset.bookId;
    const val = e.target.value;
    document.querySelector(`#progress-${id} + .progress-value`).textContent = val + " %";
  });
  slider.addEventListener("change", async e => {
    const id = e.target.dataset.bookId;
    const val = e.target.value;
    await fetch(`/book/${id}/status`, {
      method: "POST",
      headers: {"Content-Type":"application/x-www-form-urlencoded"},
      body: `is_read=${document.querySelector(".read-toggle[data-book-id='"+id+"']").checked}&progress=${val}`
    });
  });
});



// Helper: Modal-Elemente
const editModal    = document.getElementById("editModal");
const modalBody    = document.getElementById("modal-body");
const modalClose   = editModal.querySelector(".modal-close");
const modalOverlay = editModal.querySelector(".modal-overlay");

document.querySelectorAll(".edit-icon").forEach(btn => {
  btn.addEventListener("click", async () => {
    const id = btn.dataset.bookId;
    const resp = await fetch(`/book/${id}/edit?modal=true`);
    const html = await resp.text();
    modalBody.innerHTML = html;

    // *** Hier den Live-Slider-Listener hinzufügen ***
    const modalSlider = modalBody.querySelector("#progress-slider");
    const modalValue  = modalBody.querySelector("#progress-value");
    if (modalSlider && modalValue) {
      // Initialisieren
      modalValue.textContent = modalSlider.value + " %";
      // Bei jedem Verschieben updaten
      modalSlider.addEventListener("input", e => {
        modalValue.textContent = e.target.value + " %";
      });
    }

    // Formular-Submit
    document.getElementById("edit-book-form").addEventListener("submit", async e => {
      e.preventDefault();
      const form = e.target;
      const data = new URLSearchParams(new FormData(form));
      const post = await fetch(`/book/${id}/edit`, {
        method: "POST",
        headers: { "Content-Type":"application/x-www-form-urlencoded" },
        body: data
      });
      const result = await post.json();
      if (result.success) {
        location.reload();  // oder: DOM aktualisieren
      } else {
        alert("Fehler beim Speichern");
      }
    });

    // Abbrechen-Button
    modalBody.querySelector("#cancel-edit").addEventListener("click", () => {
      closeModal();
    });

    // Modal einblenden
    editModal.classList.remove("hidden");
    document.body.classList.add("modal-open");
  });
});

// Modal schließen
function closeModal() {
  editModal.classList.add("hidden");
  modalBody.innerHTML = "";
  document.body.classList.remove("modal-open");
}
[modalClose, modalOverlay].forEach(el =>
  el.addEventListener("click", closeModal)
);

// Open book detail when title is clicked
document.querySelectorAll('.book-title').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const bookId = link.dataset.bookId;
    openBookDetail(bookId);
  });
});