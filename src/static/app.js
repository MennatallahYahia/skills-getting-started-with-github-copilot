document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and reset select dropdown
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Current Participants (${details.participants.length}/${details.max_participants}):</strong>
            <ul class="participants-list" data-activity="${name}">
              ${details.participants.length > 0 
                ? details.participants.map(p => `<li draggable="true" data-email="${p}"><span class="participant-email">${p}</span><button class="delete-btn" data-activity="${name}" data-email="${p}" title="Unregister">🗑️</button></li>`).join('')
                : '<li class="no-participants">No participants yet</li>'}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add delete button listeners
        const deleteButtons = activityCard.querySelectorAll(".delete-btn");
        deleteButtons.forEach(btn => {
          btn.addEventListener("click", handleDeleteParticipant);
        });

        // Add drag-and-drop listeners to participant list items
        const participantsList = activityCard.querySelector(".participants-list");
        if (participantsList) {
          const listItems = participantsList.querySelectorAll("li[draggable='true']");
          listItems.forEach(item => {
            item.addEventListener("dragstart", handleDragStart);
            item.addEventListener("dragend", handleDragEnd);
            item.addEventListener("dragover", handleDragOver);
            item.addEventListener("drop", handleDrop);
            item.addEventListener("dragenter", handleDragEnter);
            item.addEventListener("dragleave", handleDragLeave);
          });
        }

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  let draggedItem = null;

  function handleDragStart(e) {
    draggedItem = this;
    this.classList.add("dragging");
    e.dataTransfer.effectAllowed = "move";
  }

  function handleDragEnd(e) {
    this.classList.remove("dragging");
    const allItems = document.querySelectorAll(".participants-list li[draggable='true']");
    allItems.forEach(item => item.classList.remove("drag-over"));
  }

  function handleDragOver(e) {
    if (e.preventDefault) {
      e.preventDefault();
    }
    e.dataTransfer.dropEffect = "move";
    return false;
  }

  function handleDragEnter(e) {
    if (this !== draggedItem && this.hasAttribute("data-email")) {
      this.classList.add("drag-over");
    }
  }

  function handleDragLeave(e) {
    this.classList.remove("drag-over");
  }

  function handleDrop(e) {
    if (e.stopPropagation) {
      e.stopPropagation();
    }

    if (draggedItem !== this && this.hasAttribute("data-email")) {
      const parentList = this.parentNode;
      
      // Swap the items in the DOM
      if (draggedItem.nextSibling === this) {
        this.parentNode.insertBefore(this, draggedItem);
      } else {
        draggedItem.parentNode.insertBefore(draggedItem, this);
      }
    }

    return false;
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh activities to update participant counts
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle participant deletion
  async function handleDeleteParticipant(event) {
    event.preventDefault();
    const btn = event.target.closest(".delete-btn");
    const listItem = btn.closest("li");
    const activity = btn.getAttribute("data-activity");
    const email = btn.getAttribute("data-email");

    if (!confirm(`Are you sure you want to unregister ${email}?`)) {
      return;
    }

    // Add deletion animation to the list item
    listItem.classList.add("deleting");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");
        
        // Wait for animation to complete, then refresh
        await new Promise(resolve => setTimeout(resolve, 300));
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "Failed to unregister";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
        listItem.classList.remove("deleting");
      }

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      listItem.classList.remove("deleting");
      console.error("Error unregistering:", error);
    }
  }

  // Initialize app
  fetchActivities();
});
