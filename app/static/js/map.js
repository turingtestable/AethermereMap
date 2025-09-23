let currentEditingDistrict = null;
let currentSelectedDistrict = null;

// Add interactivity when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add click handlers to all districts
    document.querySelectorAll('.district').forEach(district => {
        district.addEventListener('click', function(event) {
            const districtId = this.dataset.id;
            const name = this.dataset.name;
            const info = this.dataset.info;
            const status = this.dataset.status;
            const color = this.dataset.color;
            
            // If it's a TBD district or Ctrl+click, open edit panel directly
            if (status === 'Unknown' || event.ctrlKey) {
                openEditPanel(this, { name, info, status, color});
            } else {
                // Regular click - show info and edit button
                currentSelectedDistrict = this;
                showDistrictDetails(name, info, status, color, districtId);
                
                // Show edit button for defined districts
                document.getElementById('edit-btn').style.display = 'inline-block';
                
                // Highlight selected district
                document.querySelectorAll('.district').forEach(d => {
                    d.style.strokeWidth = '1';
                    d.style.stroke = '#2d3748';
                });
                this.style.strokeWidth = '3';
                this.style.stroke = '#63b3ed';
            }
        });
        
        // Prevent context menu on right click
        district.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            const name = this.dataset.name;
            const info = this.dataset.info;
            const status = this.dataset.status;
            const color = this.dataset.color;
            openEditPanel(this, { name, info, status, color});
        });
    });

    // Close panel when clicking overlay
    document.getElementById('overlay').addEventListener('click', closeEditPanel);
    
    // Hide edit button when clicking elsewhere
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.district') && !e.target.closest('.info-panel')) {
            document.getElementById('edit-btn').style.display = 'none';
            hideDistrictDetails();
            currentSelectedDistrict = null;
        }
    });
});

// Function to show district details with new layout
async function showDistrictDetails(name, info, status, color, districtId) {
    // Update district info
    document.getElementById('district-name').textContent = name;
    const infoElement = document.getElementById('district-info');
    infoElement.innerHTML = info.replace(/\n/g, '<br>');
    document.getElementById('district-status').textContent = status;
    
    // Update border color to match district color
    const infoPanel = document.querySelector('.info-panel');
    if (color === 'sealed') {
        infoPanel.style.borderLeftColor = '#f56565'; // Red for sealed
    } else {
        infoPanel.style.borderLeftColor = color;
    }
    
    // Hide default content and show district details
    document.getElementById('default-content').style.display = 'none';
    document.getElementById('district-details').style.display = 'block';
    
    // Load and display guilds for this district
    await loadDistrictGuilds(districtId);
    
    // Load player notes
    loadPlayerNotes('district', districtId);
}

// Function to hide district details
function hideDistrictDetails() {
    document.getElementById('default-content').style.display = 'block';
    document.getElementById('district-details').style.display = 'none';
    document.getElementById('guilds-section').style.display = 'none';
}

// Function to load player notes for a target
async function loadPlayerNotes(targetType, targetId) {
    try {
        const response = await fetch(`/api/notes/${targetType}/${targetId}`);
        const notes = await response.json();
        
        const notesList = document.getElementById('player-notes-list');
        notesList.innerHTML = '';
        
        let currentUserHasNote = false;
        
        if (notes.length === 0) {
            notesList.innerHTML = '<p style="color: #a0aec0; font-style: italic;">No player notes yet.</p>';
        } else {
            notes.forEach(note => {
                // Check if current user already has a note
                if (note.user_id === currentUserId) {
                    currentUserHasNote = true;
                }
                
                const noteDiv = document.createElement('div');
                noteDiv.className = 'player-note';
                noteDiv.setAttribute('data-note-id', note.id);
                
                let noteActions = '';
                // Only show edit/delete for the note owner or admin
                if (note.user_id === currentUserId || currentUserRole === 'admin') {
                    noteActions = `
                        <div class="note-actions">
                            <button class="btn btn-small" onclick="editPlayerNote(${note.id}, '${note.content.replace(/'/g, "\\'")}')">Edit</button>
                            <button class="btn btn-small btn-danger" onclick="deletePlayerNote(${note.id})">Delete</button>
                        </div>
                    `;
                }
                
                noteDiv.innerHTML = `
                    <strong>${note.username}:</strong>
                    <div class="note-content">${note.content.replace(/\n/g, '<br>')}</div>
                    ${noteActions}
                `;
                
                notesList.appendChild(noteDiv);
            });
        }
        
        // Show/hide the add note section based on user role and existing notes
        const addNoteSection = document.querySelector('.add-note-section');
        
        // Check if we're currently editing a note (textarea has content and buttons show Update/Cancel)
        const isEditingNote = document.querySelector('.add-note-section .note-actions button[onclick*="updatePlayerNote"]') !== null;
        
        // Only players can add notes (DMs/admins edit districts directly)
        if (currentUserRole !== 'player') {
            addNoteSection.style.display = 'none';
        } else if (currentUserHasNote && !isEditingNote) {
            addNoteSection.style.display = 'none';
        } else {
            addNoteSection.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading player notes:', error);
    }
}

// Function to save a new player note
async function savePlayerNote() {
    const content = document.getElementById('new-note-content').value.trim();
    if (!content) return;
    
    const districtId = currentSelectedDistrict.dataset.id;
    
    try {
        const response = await fetch('/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                target_type: 'district',
                target_id: districtId,
                content: content
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            document.getElementById('new-note-content').value = '';
            loadPlayerNotes('district', districtId);
        } else {
            alert('Error saving note: ' + result.error);
        }
    } catch (error) {
        console.error('Error saving note:', error);
        alert('Error saving note. Please try again.');
    }
}

// Function to edit a player note
function editPlayerNote(noteId, currentContent) {
    const textarea = document.getElementById('new-note-content');
    textarea.value = currentContent;
    
    // Force the add note section to be visible during edit
    const addNoteSection = document.querySelector('.add-note-section');
    addNoteSection.style.display = 'block';
    
    // Replace the Add Note button with Update/Cancel buttons
    const actionsDiv = document.querySelector('.add-note-section .note-actions');
    actionsDiv.innerHTML = `
        <button class="btn btn-small" onclick="updatePlayerNote(${noteId})">Update Note</button>
        <button class="btn btn-small btn-secondary" onclick="cancelEditNote()">Cancel</button>
    `;
}

// Function to update a player note
async function updatePlayerNote(noteId) {
    const content = document.getElementById('new-note-content').value.trim();
    if (!content) return;
    
    try {
        const response = await fetch(`/api/notes/${noteId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            cancelEditNote();
            const districtId = currentSelectedDistrict.dataset.id;
            loadPlayerNotes('district', districtId);
        } else {
            alert('Error updating note: ' + result.error);
        }
    } catch (error) {
        console.error('Error updating note:', error);
        alert('Error updating note. Please try again.');
    }
}

// Function to delete a player note
async function deletePlayerNote(noteId) {
    if (!confirm('Are you sure you want to delete this note?')) return;
    
    try {
        const response = await fetch(`/api/notes/${noteId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            const districtId = currentSelectedDistrict.dataset.id;
            loadPlayerNotes('district', districtId);
            // Note: loadPlayerNotes will automatically show/hide add section based on remaining notes
        } else {
            const result = await response.json();
            alert('Error deleting note: ' + result.error);
        }
    } catch (error) {
        console.error('Error deleting note:', error);
        alert('Error deleting note. Please try again.');
    }
}

// Function to cancel editing a note
function cancelEditNote() {
    document.getElementById('new-note-content').value = '';
    const actionsDiv = document.querySelector('.add-note-section .note-actions');
    actionsDiv.innerHTML = '<button class="btn btn-small" onclick="savePlayerNote()">Add Note</button>';
    
    // Hide the add note section if user already has a note
    const districtId = currentSelectedDistrict.dataset.id;
    loadPlayerNotes('district', districtId);
}

// Function to edit the currently selected district
function editCurrentDistrict() {
    if (currentSelectedDistrict) {
        const name = currentSelectedDistrict.dataset.name;
        const info = currentSelectedDistrict.dataset.info;
        const status = currentSelectedDistrict.dataset.status;
        const color = currentSelectedDistrict.dataset.color;
        openEditPanel(currentSelectedDistrict, { name, info, status, color });
    }
}

function openEditPanel(districtElement, data) {
    currentEditingDistrict = districtElement;
    
    document.getElementById('edit-name').value = data.name;
    document.getElementById('edit-info').value = data.info;
    document.getElementById('edit-status').value = data.status;
    document.getElementById('edit-type').value = data.color || '#4a5568';
    
    // Hide color field for The Mere
    const colorGroup = document.getElementById('edit-type').closest('.form-group');
    if (districtElement.classList.contains('mere')) {
        if (colorGroup) colorGroup.style.display = 'none';
    } else {
        if (colorGroup) colorGroup.style.display = 'block';
    }
    
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('edit-panel').style.display = 'block';
}

function closeEditPanel() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('edit-panel').style.display = 'none';
    currentEditingDistrict = null;
}

function saveDistrict() {
    if (!currentEditingDistrict) return;
    
    const newName = document.getElementById('edit-name').value;
    const newInfo = document.getElementById('edit-info').value;
    const newStatus = document.getElementById('edit-status').value;
    const districtId = currentEditingDistrict.dataset.id;
    
    // Prepare data for API call
    const updateData = {
        name: newName,
        info: newInfo,
        status: newStatus
    };
    
    // Only include color for non-Mere districts
    if (!currentEditingDistrict.classList.contains('mere')) {
        const newColor = document.getElementById('edit-type').value;
        updateData.color = newColor;
    }
    
    // Make API call to update district
    fetch(`/api/districts/${districtId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the DOM elements
            currentEditingDistrict.dataset.name = newName;
            currentEditingDistrict.dataset.info = newInfo;
            currentEditingDistrict.dataset.status = newStatus;
            
            // Update visual appearance (skip for The Mere)
            if (!currentEditingDistrict.classList.contains('mere')) {
                const newColor = document.getElementById('edit-type').value;
                currentEditingDistrict.dataset.color = newColor;
                
                if (newColor === 'sealed') {
                    currentEditingDistrict.classList.add('sealed');
                    currentEditingDistrict.style.fill = '';
                } else {
                    currentEditingDistrict.classList.remove('sealed');
                    currentEditingDistrict.style.fill = newColor;
                }
            }
            
            // Update the district label text
            const districtId = currentEditingDistrict.dataset.id;
            const label = document.querySelector(`.district-label[data-district-id="${districtId}"]`);
            if (label) {
                // Extract just the name part (remove parenthetical if present)
                const displayName = newName.includes('(') ? newName.split('(')[0].trim() : newName;
                label.textContent = displayName;
            }
            
            // Update info panel if this district is currently selected
            if (currentSelectedDistrict === currentEditingDistrict) {
                // Refresh the entire district details view
                const districtId = currentEditingDistrict.dataset.id;
                const color = currentEditingDistrict.dataset.color;
                showDistrictDetails(newName, newInfo, newStatus, color, districtId);
            }
            
            closeEditPanel();
        } else {
            alert('Failed to update district: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error updating district:', error);
        alert('Failed to update district. Please try again.');
    });
}

// Function to load and display guilds for a district
async function loadDistrictGuilds(districtId) {
    try {
        const response = await fetch(`/api/districts/${districtId}`, {
            credentials: 'same-origin'
        });
        const districtData = await response.json();
        
        const guildsSection = document.getElementById('guilds-section');
        const guildsList = document.getElementById('guilds-list');
        
        if (districtData.guilds && districtData.guilds.length > 0) {
            // Show guilds section and populate with guild preview cards
            guildsSection.style.display = 'block';
            guildsList.innerHTML = '';
            
            districtData.guilds.forEach(guild => {
                const guildCard = createGuildPreviewCard(guild, districtData.color);
                guildsList.appendChild(guildCard);
            });
        } else {
            // Hide guilds section if no guilds
            guildsSection.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading district guilds:', error);
        document.getElementById('guilds-section').style.display = 'none';
    }
}

// Function to create a guild preview card
function createGuildPreviewCard(guild, districtColor) {
    const card = document.createElement('div');
    card.className = 'guild-preview-card';
    
    // Add visual indicator for relationship to district
    let relationshipIndicator = '';
    
    if (guild.relationship_to_district === 'headquartered') {
        const indicatorColor = districtColor === 'sealed' ? '#f56565' : districtColor;
        relationshipIndicator = `<span class="guild-hq-indicator" title="Headquartered in this district" style="color: ${indicatorColor}">🏛️</span>`;
        // Set border color to match the district color
        card.style.borderLeftColor = indicatorColor;
    } else if (guild.relationship_to_district === 'citywide') {
        relationshipIndicator = '<span class="guild-citywide-indicator" title="Operates city-wide">🌐</span>';
        // Use silver/gray for city-wide guilds (not used in district colors)
        card.style.borderLeftColor = '#a0aec0';
    }
    
    card.innerHTML = `
        <div class="guild-preview-header">
            <h5 class="guild-preview-name">
                ${relationshipIndicator}
                ${guild.name}
            </h5>
        </div>
        
        <div class="guild-preview-description">
            ${guild.description || 'No description available.'}
        </div>
        
        <a href="#" class="guild-preview-link" onclick="viewGuildDetails(${guild.id}); return false;">
            View Full Details →
        </a>
    `;
    
    return card;
}

// Function for viewing guild details - redirects to guild info page
function viewGuildDetails(guildId) {
    window.location.href = `/guild-info#guild-info-${guildId}`;
}