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
                document.getElementById('district-name').textContent = name;
                // Display info with preserved line breaks
                const infoElement = document.getElementById('district-info');
                infoElement.innerHTML = info.replace(/\n/g, '<br>');
                document.getElementById('district-status').textContent = 'Status: ' + status;
                
                // Update border color to match district color
                const infoPanel = document.querySelector('.info-panel');
                if (color === 'sealed') {
                    infoPanel.style.borderLeftColor = '#f56565'; // Red for sealed
                } else {
                    infoPanel.style.borderLeftColor = color;
                }
                
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
            currentSelectedDistrict = null;
        }
    });
});

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
                document.getElementById('district-name').textContent = newName;
                // Update info panel with preserved line breaks
                const infoElement = document.getElementById('district-info');
                infoElement.innerHTML = newInfo.replace(/\n/g, '<br>');
                document.getElementById('district-status').textContent = 'Status: ' + newStatus;
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