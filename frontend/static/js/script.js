// frontend/static/js/script.js
document.addEventListener('DOMContentLoaded', () => {
    const messageForm = document.getElementById('messageForm');
    const loadingIndicator = document.getElementById('loading');
    const errorMessage = document.getElementById('error_message');

    // Result cards
    const originalMessageCard = document.getElementById('original_message_card');
    const communicationAnalysisCard = document.getElementById('communication_analysis_card');
    const knowledgeUpdateCard = document.getElementById('knowledge_update_card');
    const frictionDetectionCard = document.getElementById('friction_detection_card');
    const interventionSuggestionCard = document.getElementById('intervention_suggestion_card');

    messageForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        // Hide previous results and errors
        hideAllCards();
        errorMessage.classList.add('hidden');
        errorMessage.textContent = '';
        loadingIndicator.classList.remove('hidden');

        const formData = new FormData(messageForm);

        // Display submitted message immediately
        document.getElementById('original_text').textContent = formData.get('text_content');
        const originalImage = document.getElementById('original_image');
        const imageFile = formData.get('image_file');

        if (imageFile && imageFile.size > 0) {
            const reader = new FileReader();
            reader.onload = (e) => {
                originalImage.src = e.target.result;
                originalImage.style.display = 'block';
            };
            reader.readAsDataURL(imageFile);
            document.getElementById('original_image_container').classList.remove('hidden');
        } else {
            originalImage.src = '';
            originalImage.style.display = 'none';
            document.getElementById('original_image_container').classList.add('hidden');
        }
        originalMessageCard.classList.remove('hidden'); // Ensure original message card is visible

        try {
            const response = await fetch('/api/process_message', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            loadingIndicator.classList.add('hidden');
            console.log("API Response:", result);

            if (result.error) {
                errorMessage.textContent = `Error: ${result.error}`;
                errorMessage.classList.remove('hidden');
                return;
            }

            displayResults(result);

        } catch (error) {
            loadingIndicator.classList.add('hidden');
            errorMessage.textContent = `An unexpected error occurred: ${error.message}`;
            errorMessage.classList.remove('hidden');
            console.error("Fetch error:", error);
        }
    });

    function hideAllCards() {
        // originalMessageCard.classList.add('hidden'); // Keep original message card visible
        communicationAnalysisCard.classList.add('hidden');
        knowledgeUpdateCard.classList.add('hidden');
        frictionDetectionCard.classList.add('hidden');
        interventionSuggestionCard.classList.add('hidden');
    }

    function displayResults(result) {

        // Display Communication Agent Analysis
        if (result.communication_analysis) {
            communicationAnalysisCard.classList.remove('hidden');
            const analysis = result.communication_analysis.analysis;
            if (analysis && analysis.sentiment) {
                document.getElementById('sentiment_score').textContent = analysis.sentiment.score;
                document.getElementById('sentiment_magnitude').textContent = analysis.sentiment.magnitude;
            }

            const entitiesList = document.getElementById('entities_list');
            entitiesList.innerHTML = '';
            if (analysis && analysis.entities && Array.isArray(analysis.entities)) {
                analysis.entities.forEach(entity => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `Name: ${entity.name}, Type: ${entity.type_}, Salience: ${entity.salience}`;
                    entitiesList.appendChild(listItem);
                });
            }

            const geminiResponse = document.getElementById('gemini_response');
            // analysis.gemini_response may be missing when running on heuristic fallback
            geminiResponse.textContent = analysis.gemini_response_text || "No Gemini response (fallback used)";
        }

        // Display Knowledge Base Update Status
        if (result.knowledge_update_status) {
            knowledgeUpdateCard.classList.remove('hidden');
            document.getElementById('knowledge_status').textContent = result.knowledge_update_status;
        }

        // Display Friction Detection Results
        if (result.friction_detection) {
            frictionDetectionCard.classList.remove('hidden');
            document.getElementById('friction_detected').textContent = result.friction_detection.friction_detected ? 'Yes' : 'No';
            document.getElementById('friction_reason').textContent = result.friction_detection.reason || 'N/A';
            document.getElementById('friction_severity').textContent = result.friction_detection.severity !== undefined ? result.friction_detection.severity.toFixed(2) : 'N/A';
        }

        // Display Intervention Suggestion
        if (result.intervention_suggestion) {
            interventionSuggestionCard.classList.remove('hidden');
            document.getElementById('intervention_suggested').textContent = result.intervention_suggestion.intervention_suggested ? 'Yes' : 'No';
            document.getElementById('intervention_text').textContent = result.intervention_suggestion.suggestion || 'N/A';
        }
    }
});

