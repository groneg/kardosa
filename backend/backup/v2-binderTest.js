document.addEventListener('DOMContentLoaded', () => {
    // Add change indicator
    console.log('Card detection method updated: Hough Line Transform');
    document.title += ' (Hough Line Detection)';
    
    const changeIndicator = document.createElement('div');
    changeIndicator.id = 'changeIndicator';
    changeIndicator.style.backgroundColor = 'red';
    changeIndicator.style.color = 'white';
    changeIndicator.style.padding = '10px';
    changeIndicator.style.position = 'fixed';
    changeIndicator.style.top = '0';
    changeIndicator.style.left = '0';
    changeIndicator.style.width = '100%';
    changeIndicator.style.zIndex = '1000';
    changeIndicator.style.textAlign = 'center';
    changeIndicator.textContent = 'New Hough Line Detection Method Implemented';
    
    // Create a container to push content down
    const container = document.querySelector('.container');
    if (container) {
        container.style.marginTop = '50px'; // Adjust based on indicator height
    }
    
    document.body.insertBefore(changeIndicator, document.body.firstChild);

    const fileInput = document.getElementById('binderPageUpload');
    const originalImage = document.getElementById('originalImage');
    const cardRows = document.getElementById('cardRows');
    const statusMessage = document.getElementById('statusMessage');

    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
            // Update status message
            statusMessage.textContent = 'Processing image...';
            statusMessage.style.color = '#007AFF';
            
            // Clear previous content
            originalImage.innerHTML = '';
            cardRows.querySelectorAll('.card-row').forEach(row => {
                row.innerHTML = '';
            });

            // Display original image
            const img = document.createElement('img');
            img.file = file;
            originalImage.appendChild(img);

            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);

            // Send image to backend for processing
            const formData = new FormData();
            formData.append('binderImage', file);

            try {
                statusMessage.textContent = 'Sending image to server for processing...';
                
                const response = await fetch('/process-binder', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Failed to process image');
                }

                const result = await response.json();
                
                // Check if we got a success message but no cards (placeholder implementation)
                if (result.message === 'Binder processing route works!') {
                    statusMessage.textContent = 'Server received the image, but card processing is not yet implemented.';
                    statusMessage.style.color = '#ffc107';
                    
                    // Create placeholder cards for demonstration
                    createPlaceholderCards();
                    return;
                }

                // Display all 9 processed cards
                if (result.status === 'success' && result.cards) {
                    statusMessage.textContent = 'Cards successfully extracted!';
                    statusMessage.style.color = '#28a745';
                    
                    result.cards.forEach((cardBase64, index) => {
                        const cardRow = document.getElementById(`row${index + 1}`);
                        const cardImg = document.createElement('img');
                        cardImg.src = `data:image/png;base64,${cardBase64}`;
                        cardRow.appendChild(cardImg);
                    });
                } else {
                    console.error('Error processing image:', result);
                    statusMessage.textContent = 'Error processing image. Please try again.';
                    statusMessage.style.color = '#dc3545';
                }
            } catch (error) {
                console.error('Error:', error);
                statusMessage.textContent = 'Error: ' + error.message;
                statusMessage.style.color = '#dc3545';
            }
        }
    });
    
    // Function to create placeholder cards for demonstration
    function createPlaceholderCards() {
        for (let i = 1; i <= 9; i++) {
            const cardRow = document.getElementById(`row${i}`);
            cardRow.innerHTML = '';
            
            // Create 3 placeholder cards per row
            for (let j = 0; j < 3; j++) {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `<img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23f0f0f0'/%3E%3Ctext x='50' y='50' font-family='Arial' font-size='14' text-anchor='middle' dominant-baseline='middle' fill='%23999'%3ECard ${i}-${j+1}%3C/text%3E%3C/svg%3E" alt="Card ${i}-${j+1}">`;
                cardRow.appendChild(card);
            }
        }
    }
}); 