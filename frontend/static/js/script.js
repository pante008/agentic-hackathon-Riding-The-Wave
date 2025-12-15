// frontend/static/js/script.js
document.addEventListener('DOMContentLoaded', () => {
    const messageForm = document.getElementById('messageForm');
    const loadingIndicator = document.getElementById('loading');
    const errorMessage = document.getElementById('error_message');
    const textContent = document.getElementById('text_content');
    
    // Demo examples data
    const demoExamples = {
        frustrated: {
            text: "I am really frustrated with the constant delays on this feature. We've been waiting for 3 weeks now and the deadline is approaching fast. This is becoming a serious issue for our team and we need to accelerate immediately!",
            description: "Shows how the system detects high frustration and suggests clarification interventions."
        },
        timeline: {
            text: "The project timeline is slipping again. We were supposed to deliver Phase 2 by Friday, but now it looks like it will be delayed by at least another week. This is the third time we've had to push back deadlines. We need to have a serious discussion about resource allocation and priorities.",
            description: "Demonstrates timeline friction detection and action item proposals."
        },
        positive: {
            text: "Great work on the latest sprint! The team really pulled together and we delivered everything on time. The new features are working perfectly and the client is very happy with the progress. Let's keep this momentum going!",
            description: "Shows how the system recognizes positive communication and confirms no friction."
        },
        conflict: {
            text: "I completely disagree with the approach we're taking. The current design doesn't align with our original requirements and I think we're going in the wrong direction. We need to stop and reconsider before we waste more time and resources on this.",
            description: "Highlights conflict detection and mediation intervention suggestions."
        },
        multimodal: {
            text: "This graph shows a significant drop in user engagement over the past month. We went from 85% active users to just 62%. The data suggests there might be an issue with the latest update. Can someone analyze this chart and help us understand what's happening?",
            description: "Tests multimodal analysis capabilities with data visualization context."
        }
    };
    
    // Setup demo buttons
    document.querySelectorAll('.demo-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const exampleKey = btn.getAttribute('data-example');
            const example = demoExamples[exampleKey];
            if (example) {
                textContent.value = example.text;
                // Scroll to form
                messageForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Highlight the textarea briefly
                textContent.focus();
                textContent.style.border = '2px solid #667eea';
                setTimeout(() => {
                    textContent.style.border = '1px solid #ccc';
                }, 2000);
            }
        });
    });

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
            // Update loading message
            const loadingText = loadingIndicator.querySelector('p');
            if (loadingText) {
                loadingText.textContent = '🤖 Processing through AI agents... Analyzing with Gemini AI...';
            }
            
            const response = await fetch('/api/process_message', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            loadingIndicator.classList.add('hidden');
            console.log("API Response:", result);

            if (result.error) {
                errorMessage.textContent = `Error: ${result.error}`;
                errorMessage.classList.remove('hidden');
                return;
            }

            // Warnings removed - don't display API quota/fallback information to users
            // (Warnings are still logged server-side for debugging)

            displayResults(result);
            
            // Smooth scroll to results
            setTimeout(() => {
                document.querySelector('.results-section').scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 100);

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

    // checkForAPIErrors function removed - API quota/fallback warnings are not shown to users

    function displayResults(result) {
        console.log("Full API result:", result);
        
        // Parse string responses if needed
        let commAnalysis = result.communication_analysis;
        let frictionDetection = result.friction_detection;
        let interventionSuggestion = result.intervention_suggestion;

        // Try to parse if they're strings (Python dict format)
        if (typeof commAnalysis === 'string') {
            try {
                // Try to parse as JSON first
                commAnalysis = JSON.parse(commAnalysis);
            } catch (e1) {
                try {
                    // If that fails, try replacing single quotes (Python dict format)
                    commAnalysis = JSON.parse(commAnalysis.replace(/'/g, '"').replace(/None/g, 'null').replace(/True/g, 'true').replace(/False/g, 'false'));
                } catch (e2) {
                    console.warn("Could not parse communication_analysis:", e2, "Raw:", commAnalysis);
                }
            }
        }
        if (typeof frictionDetection === 'string') {
            try {
                frictionDetection = JSON.parse(frictionDetection);
            } catch (e1) {
                try {
                    frictionDetection = JSON.parse(frictionDetection.replace(/'/g, '"').replace(/None/g, 'null').replace(/True/g, 'true').replace(/False/g, 'false'));
                } catch (e2) {
                    console.warn("Could not parse friction_detection:", e2, "Raw:", frictionDetection);
                }
            }
        }
        if (typeof interventionSuggestion === 'string') {
            try {
                interventionSuggestion = JSON.parse(interventionSuggestion);
            } catch (e1) {
                try {
                    interventionSuggestion = JSON.parse(interventionSuggestion.replace(/'/g, '"').replace(/None/g, 'null').replace(/True/g, 'true').replace(/False/g, 'false'));
                } catch (e2) {
                    console.warn("Could not parse intervention_suggestion:", e2, "Raw:", interventionSuggestion);
                }
            }
        }

        console.log("Parsed commAnalysis:", commAnalysis);
        console.log("Parsed frictionDetection:", frictionDetection);
        console.log("Parsed interventionSuggestion:", interventionSuggestion);

        // Display Communication Agent Analysis
        if (commAnalysis) {
            communicationAnalysisCard.classList.remove('hidden');
            // commAnalysis structure: {analysis: {...}, friction: {...}}
            const analysis = commAnalysis.analysis || commAnalysis;
            console.log("Extracted analysis:", analysis);
            
            // Handle nested nlp_analysis structure
            const nlpAnalysis = analysis?.nlp_analysis || analysis;
            console.log("NLP Analysis:", nlpAnalysis);
            
            if (nlpAnalysis && nlpAnalysis.sentiment) {
                const sentiment = nlpAnalysis.sentiment;
                const score = (typeof sentiment === 'object' && sentiment.score !== undefined) ? sentiment.score : 
                             (typeof sentiment === 'number' ? sentiment : 0.0);
                const magnitude = (typeof sentiment === 'object' && sentiment.magnitude !== undefined) ? sentiment.magnitude : 
                                 (typeof sentiment === 'object' ? Math.abs(score) : 'N/A');
                
                document.getElementById('sentiment_score').textContent = typeof score === 'number' ? score.toFixed(2) : (score || 'N/A');
                document.getElementById('sentiment_score').style.color = score < -0.2 ? '#d9534f' : score > 0.2 ? '#5cb85c' : '#f0ad4e';
                document.getElementById('sentiment_magnitude').textContent = typeof magnitude === 'number' ? magnitude.toFixed(2) : (magnitude || 'N/A');
            } else {
                document.getElementById('sentiment_score').textContent = 'N/A';
                document.getElementById('sentiment_magnitude').textContent = 'N/A';
            }

            const entitiesList = document.getElementById('entities_list');
            entitiesList.innerHTML = '';
            const entities = nlpAnalysis?.entities || analysis?.entities || [];
            if (Array.isArray(entities) && entities.length > 0) {
                entities.forEach(entity => {
                    const listItem = document.createElement('li');
                    const entityName = entity.name || 'Unknown';
                    const entityType = entity.type_ || entity.type || 'Unknown';
                    const salience = entity.salience !== undefined ? entity.salience.toFixed(2) : 'N/A';
                    listItem.innerHTML = `<strong>${entityName}</strong> (${entityType}) - Salience: ${salience}`;
                    entitiesList.appendChild(listItem);
                });
            } else {
                entitiesList.innerHTML = '<li>No entities detected</li>';
            }

            const geminiResponse = document.getElementById('gemini_response');
            const geminiText = analysis?.gemini_response_text || analysis?.gemini_response || "No response available";
            geminiResponse.textContent = geminiText;
            
            // Style response box (no API source indicators shown to users)
            geminiResponse.style.backgroundColor = '#eee';
            geminiResponse.style.border = 'none';
        }

        // Display Knowledge Base Update Status
        if (result.knowledge_update_status) {
            knowledgeUpdateCard.classList.remove('hidden');
            document.getElementById('knowledge_status').textContent = result.knowledge_update_status;
        }

        // Display Friction Detection Results
        if (frictionDetection) {
            frictionDetectionCard.classList.remove('hidden');
            // Handle both boolean and string values
            const frictionDetected = frictionDetection.friction_detected === true || 
                                    frictionDetection.friction_detected === 'True' ||
                                    (typeof frictionDetection.friction_detected === 'string' && frictionDetection.friction_detected.toLowerCase() === 'true');
            
            const frictionDetectedEl = document.getElementById('friction_detected');
            frictionDetectedEl.textContent = frictionDetected ? '⚠️ Yes' : '✅ No';
            frictionDetectedEl.style.color = frictionDetected ? '#d9534f' : '#5cb85c';
            frictionDetectedEl.style.fontWeight = 'bold';
            
            let frictionReason = frictionDetection.reason || 'No friction detected';
            // Truncate very long reasons for display
            if (frictionReason.length > 500) {
                frictionReason = frictionReason.substring(0, 500) + '... (truncated)';
            }
            document.getElementById('friction_reason').textContent = frictionReason;
            
            // No API source indicators shown to users
            
            const severity = frictionDetection.severity;
            const severityEl = document.getElementById('friction_severity');
            if (severity !== undefined && severity !== null && severity !== 'N/A') {
                const severityNum = typeof severity === 'number' ? severity : parseFloat(severity);
                if (!isNaN(severityNum)) {
                    severityEl.textContent = severityNum.toFixed(2) + ' / 1.0';
                    severityEl.style.color = severityNum > 0.7 ? '#d9534f' : severityNum > 0.4 ? '#f0ad4e' : '#5cb85c';
                } else {
                    severityEl.textContent = 'N/A';
                }
            } else {
                severityEl.textContent = 'N/A';
            }
        }

        // Display Intervention Suggestion
        if (interventionSuggestion) {
            interventionSuggestionCard.classList.remove('hidden');
            // Handle both boolean and string values
            const interventionSuggested = interventionSuggestion.intervention_suggested === true || 
                                         interventionSuggestion.intervention_suggested === 'True' ||
                                         (typeof interventionSuggestion.intervention_suggested === 'string' && interventionSuggestion.intervention_suggested.toLowerCase() === 'true');
            
            const interventionSuggestedEl = document.getElementById('intervention_suggested');
            interventionSuggestedEl.textContent = interventionSuggested ? '💡 Yes' : '✅ No intervention needed';
            interventionSuggestedEl.style.color = interventionSuggested ? '#667eea' : '#5cb85c';
            interventionSuggestedEl.style.fontWeight = 'bold';
            
            let suggestionText = interventionSuggestion.suggestion || 'No specific intervention needed at this time.';
            // Truncate very long suggestions for display
            if (suggestionText.length > 1000) {
                suggestionText = suggestionText.substring(0, 1000) + '... (truncated)';
            }
            document.getElementById('intervention_text').textContent = suggestionText;
            document.getElementById('intervention_text').style.fontStyle = interventionSuggested ? 'normal' : 'italic';
        }
    }
});

