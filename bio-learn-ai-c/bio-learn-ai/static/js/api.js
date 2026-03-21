async function generateContent() {
    const topic = document.getElementById('topicInput').value;
    const level = document.getElementById('levelSelect').value;
    const btn = document.getElementById('generateBtn');
    const loader = document.getElementById('loading');

    if (!topic) {
        alert("Please enter a biotechnology topic first!");
        return;
    }

    // Show Loading, Hide Button
    loader.classList.remove('hidden');
    btn.disabled = true;
    btn.classList.add('opacity-50');

    try {
        const response = await fetch('/api/generate-topic', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: topic, level: level })
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert("Error: " + (errorData.error || `Server error (${response.status})`));
            return;
        }

        const data = await response.json();

        if (data.content) {
            console.log("AI Response:", data.content);
            localStorage.setItem('currentModule', data.content);
            localStorage.setItem('currentTopic', topic);
            window.location.href = '/module';
        } else {
            alert("Error: " + (data.error || "Unknown error - content not received"));
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        alert("Network error: " + error.message + ". Please try again.");
    } finally {
        loader.classList.add('hidden');
        btn.disabled = false;
        btn.classList.remove('opacity-50');
    }
}