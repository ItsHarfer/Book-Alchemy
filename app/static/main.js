/**
 * Book Alchemy – UI Interaction Module
 * ------------------------------------
 * Handles modal dialogs, toast messages, ratings, progress updates,
 * book editing/deletion, and adding recommended books.
 *
 * Main Features:
 * - Dynamic modal loading via fetch()
 * - Toast notifications for user feedback
 * - Book rating and progress tracking
 * - Form handling with spinners
 * - Add-to-library functionality
 *
 * Initializes all event listeners on DOMContentLoaded.
 * Depends on modals (#editModal), toast (#toast), and spinner (#spinner).
 *
 * Author: Martin Haferanke
 * Date: 09.07.2025
 */


const editModal = document.getElementById("editModal");
const modalBody = document.getElementById("modal-body");
const modalClose = editModal.querySelector(".modal-close");
const modalOverlay = editModal.querySelector(".modal-overlay");


/**
 * Handles an error by logging the error to the console and displaying a user-friendly message.
 *
 * @param {Error|string} err - The error object or error message to be logged.
 * @param {string} [userMsg='An unexpected error occurred.'] - The message to be shown to the user as a toast notification.
 * @return {void} This method does not return a value.
 */
function handleError(err, userMsg = 'An unexpected error occurred.') {
  console.error(err);
  showToast(userMsg);
}


/**
 * Opens a modal by fetching and loading content from a specified URL.
 *
 * @param {string} url - The URL to fetch the modal content from.
 * @return {Promise<void>} A promise that resolves when the modal is successfully displayed or logs an error if the fetch fails.
 */
async function openModal(url) {
  try {
    const resp = await fetch(url);
    const html = await resp.text();
    modalBody.innerHTML = html;

    // Rebind close buttons for dynamically loaded content
    editModal.querySelectorAll('.modal-close').forEach(btn =>
      btn.addEventListener('click', closeModal)
    );

    // Setup book form validation if present
    const bookForm = modalBody.querySelector('#add-book-form');
    if (bookForm) {
      const submitBtn    = bookForm.querySelector('#add-book-submit');
      const isbnInput    = bookForm.querySelector('#book-isbn');
      const titleInput   = bookForm.querySelector('#book-title');
      const descInput    = bookForm.querySelector('#book-description');
      const descCount    = bookForm.querySelector('#desc-count');
      const yearInput    = bookForm.querySelector('#book-year');
      const authorInput  = bookForm.querySelector('#book-author');
      const isbnFeedback = bookForm.querySelector('#isbn-feedback');
      const yearFeedback = bookForm.querySelector('#year-feedback');

      // For ISBN-10 and ISBN-13 format validation
      const isbnRegex = /^(?:\d{10}|\d{13})$/;

      // Validates the form fields and enables/disables the submit button
      function validateBook() {
        const hasTitle   = titleInput.value.trim().length > 0;
        const hasYear    = yearInput.value.trim().length > 0 && +yearInput.value <= 2030;
        const hasAuthor  = authorInput.value.trim().length > 0;
        const descOk     = descInput.value.length <= 250;
        const isbnVal    = isbnInput.value.trim();
        const isbnOk     = isbnVal === '' || isbnRegex.test(isbnVal);
        submitBtn.disabled = !(hasTitle && hasYear && hasAuthor && descOk && isbnOk);
      }

      // Live ISBN validation with inline feedback
      isbnInput.addEventListener('input', () => {
        const val = isbnInput.value.trim();
        if (val === '' || isbnRegex.test(val)) {
          isbnInput.classList.remove('is-invalid');
          isbnInput.classList.add('is-valid');
          isbnFeedback.textContent = '';
        } else {
          isbnInput.classList.add('is-invalid');
          isbnInput.classList.remove('is-valid');
          isbnFeedback.textContent = 'ISBN must be exactly 10 or 13 digits';
        }
        validateBook();
      });

      // Live year validation with feedback
      yearInput.addEventListener('input', () => {
        const val = +yearInput.value;
        if (yearInput.value.trim() && val <= 2030) {
          yearInput.classList.remove('is-invalid');
          yearInput.classList.add('is-valid');
          yearFeedback.textContent = '';
        } else {
          yearInput.classList.add('is-invalid');
          yearInput.classList.remove('is-valid');
          yearFeedback.textContent = 'Year must be 2030 or earlier';
        }
        validateBook();
      });

      // Live description character count with truncation at 250
      descInput.addEventListener('input', e => {
        if (e.target.value.length > 250) {
          e.target.value = e.target.value.slice(0, 250);
        }
        descCount.textContent = `${e.target.value.length}/250`;
        validateBook();
      });

      // Validate on title and author changes
      [titleInput, authorInput].forEach(el =>
        el.addEventListener('input', validateBook)
      );

      validateBook(); // Initial validation
    }

    // Setup author form validation if present
    const form = modalBody.querySelector('#add-author-form');
    if (form) {
      const submitBtn = form.querySelector('#add-author-submit');
      const nameInput = form.querySelector('#author-name');
      const birthInput = form.querySelector('#author-birth-date');

      const validate = () => {
        const nameOk = nameInput.value.trim().length > 0;
        const birthOk = birthInput.value.trim().length > 0;
        submitBtn.disabled = !(nameOk && birthOk);
      };

      validate(); // Initial check
      nameInput.addEventListener('input', validate);
      birthInput.addEventListener('input', validate);
    }

    // Show the modal
    editModal.classList.remove("hidden");
    document.body.classList.add("modal-open");
  } catch (err) {
    handleError(err, "Failed to load content.");
  }
}

/**
 * Closes the modal dialog by adding the "hidden" class to the modal element,
 * removing the "modal-open" class from the body, and clearing the modal content.
 *
 * @return {void} This function does not return a value.
 */
function closeModal() {
  editModal.classList.add("hidden");
  document.body.classList.remove("modal-open");
  modalBody.innerHTML = "";
}

/**
 * Displays a transient toast message at bottom-right.
 * @param {string} msg - The text to show.
 * @param {number} [duration=3000] - Duration in ms before hiding.
 */
function showToast(msg, duration = 3000) {
  if (!msg) return;
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}

/**
 * Initializes event listeners after DOM is ready.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Show flash message from server if present
    const flash = document.body.dataset.message;
    if (flash && flash !== 'None' && flash.trim() !== '') {
        showToast(flash);
    }

    // Modal close triggers
    [modalClose, modalOverlay].forEach(el =>
        el.addEventListener('click', closeModal)
    );

    // Open book details on title click
    document.querySelectorAll('.book-title').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const id = link.dataset.bookId;
            openModal(`/books/${id}?modal=true`);
        });

        document.querySelectorAll('.author-link, .book-author-line a').forEach(link => {
            link.addEventListener('click', e => {
                e.preventDefault();
                const id = link.dataset.authorId;
                openModal(`/authors/${id}?modal=true`);
            });
        });
    });

    // Open the Add-Author modal
    document.querySelectorAll('.js-open-add-author').forEach(btn => {
      btn.addEventListener('click', e => {
        openModal(btn.dataset.url);
      });
    });

    // Open the Add-Book modal
    document.querySelectorAll('.js-open-add-book').forEach(btn => {
      btn.addEventListener('click', e => {
        openModal(btn.dataset.url);
      });
    });

    // Rating change
    document.querySelectorAll('.rating-select').forEach(sel => {
        sel.addEventListener('change', async e => {
            const bookId = e.target.id.split("-")[1];
            const rating = e.target.value;
            const resp = await fetch(`/books/${bookId}/rate`, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `rating=${rating}`
            });
            showToast(resp.ok ? 'Rating saved' : 'Error while saving rating');
        });
    });

    // Progress slider live update
    document.querySelectorAll('.progress-slider').forEach(slider => {
        slider.addEventListener('input', e => {
            const id = e.target.dataset.bookId;
            document.querySelector(`#progress-${id} + .progress-value`).textContent = e.target.value + '%';
        });
        slider.addEventListener('change', async e => {
            const id = e.target.dataset.bookId;
            const val = e.target.value;
            const isRead = document.querySelector(`.read-toggle[data-book-id='${id}']`).checked;
            await fetch(`/books/${id}/status`, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `is_read=${isRead}&progress=${val}`
            });
            showToast('Progress updated');
        });
    });

    // Delete book with confirmation
    document.querySelectorAll('.delete-button').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.bookId;
            if (!confirm('Are you sure you want to delete this book?')) return;
            try {
                const resp = await fetch(`/books/${id}/delete`, {method: 'POST'});
                if (resp.ok) {
                    showToast('Book deleted successfully');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('Error while deleting the book');
                }
            } catch (err) {
                console.error('Deletion error:', err);
                showToast('An error occurred while deleting');
            }
        });
    });

    // Edit book modal
    document.querySelectorAll('.edit-icon').forEach(btn => {
        btn.addEventListener('click', async e => {
            const id = btn.dataset.bookId;

            // Warte, bis Modal geladen ist
            await openModal(`/books/${id}/edit?modal=true`);

            // Jetzt ist der Inhalt im DOM → Selektieren & Listener binden
            const form = document.getElementById('edit-book-form');
            if (!form) {
                console.error("Edit form not found in modal.");
                return;
            }

            const slider = form.querySelector('#progress-slider');
            const valDisplay = form.querySelector('#progress-value');

            if (slider && valDisplay) {
                valDisplay.textContent = slider.value + '%';
                slider.addEventListener('input', e => {
                    valDisplay.textContent = e.target.value + '%';
                });
            }

            form.addEventListener('submit', async e => {
                e.preventDefault();
                const data = new URLSearchParams(new FormData(form));
                const res = await fetch(`/books/${id}/edit`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: data
                });

                try {
                    const result = await res.json();
                    if (result.success) {
                        showToast('Changes saved successfully');
                        setTimeout(() => location.reload(), 500);
                    } else {
                        showToast('Error saving changes');
                    }
                } catch (err) {
                    console.error('Invalid JSON response', err);
                    showToast('Unexpected error');
                }
            });

            // Cancel button
            form.querySelector('#cancel-edit')?.addEventListener('click', closeModal);
        });
    });
});

// Hijack the Add-Author form submission when in a modal
document.addEventListener('submit', async e => {
  const form = e.target;
  if (form.id === 'add-author-form') {
    e.preventDefault();

    // Build POST to /authors/add?modal=true
    const url  = form.action + '?modal=true';
    const body = new URLSearchParams(new FormData(form));

    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
      });

      const result = await resp.json();

      if (result.success) {
        // 1) Close the modal
        closeModal();
        // 2) Show the toast with the success message
        showToast(result.message);
      } else {
        // Show inline error in the form
        let err = form.querySelector('.alert-danger');
        if (!err) {
          err = document.createElement('div');
          err.className = 'alert alert-danger';
          form.prepend(err);
        }
        err.textContent = result.message;
      }

    } catch (err) {
      console.error('Add-author AJAX error', err);
      showToast('An unexpected error occurred.');
    }
  }
});



/**
 * Displays a spinner by changing its CSS `display` property to "flex".
 *
 * @return {void} This method does not return a value.
 */
function showSpinner() {
  const sp = document.querySelector('.modal-content .spinner');
  if (sp) sp.style.display = 'flex';
}

/**
 * Hides the spinner element by setting its display style to "none".
 *
 * @return {void} This method does not return a value.
 */
function hideSpinner() {
  const sp = document.querySelector('.modal-content .spinner');
  if (sp) sp.style.display = 'none';
}

// Show spinner at form submit
document.querySelectorAll("form[method='POST']").forEach(form => {
    form.addEventListener("submit", function () {
        showSpinner(); // Spinner anzeigen
    });
});

// Add to Library Functionality
document.querySelectorAll('.add-to-library').forEach(button => {
    button.addEventListener('click', async function () {
        const title = this.dataset.title;
        const author = this.dataset.author;
        const isbn = this.dataset.isbn;
        const description = this.dataset.description;
        const year = this.dataset.year;
        const birthDate = this.dataset.birthDate;
        const dateOfDeath = this.dataset.dateOfDeath;

        // Disable button during request
        this.disabled = true;
        this.textContent = 'Adding...';

        try {
            const response = await fetch('/recommend/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    title: title,
                    author: author,
                    isbn: isbn,
                    description: description,
                    publication_year: year,
                    birth_date: birthDate,
                    date_of_death: dateOfDeath,
                })
            });

            const result = await response.json();

            if (result.success) {
                // Show success message
                const successMessage = document.getElementById('success-message');
                const successText = document.getElementById('success-text');
                successText.textContent = result.message;
                successMessage.classList.remove('hidden');

                // Update button
                this.textContent = '✓ Added to Library';
                this.classList.remove('btn-primary');
                this.classList.add('btn-success');

                // Hide success message after 5 seconds
                setTimeout(() => {
                    successMessage.classList.add('hidden');
                }, 5000);

            } else {
                // Show error
                alert('Error: ' + result.error);
                this.disabled = false;
                this.textContent = '➕ Add to My Library';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while adding the book.');
            this.disabled = false;
            this.textContent = '➕ Add to My Library';
        }
    });
});