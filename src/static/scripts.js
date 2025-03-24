// scripts.js
document.getElementById('combinedForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const subject = document.getElementById('subject').value.trim();
    const topic = document.getElementById('topic').value.trim();
    const subtopic = document.getElementById('subtopic').value.trim();
    const prompt = document.getElementById('prompt').value.trim();
    const errorElement = document.getElementById('error');
    errorElement.textContent = '';

    if ((!subject && !topic && !subtopic) && !prompt) {
        errorElement.textContent = 'Please provide either Subject/Topic/Subtopic or General Prompt';
        return;
    }

    try {
        let response;
        if (subject && topic && subtopic) {
            response = await fetch('/generate_response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ subject, topic, subtopic })
            });
        } else if (prompt) {
            response = await fetch('/generate_response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt })
            });
        }

        const data = await response.json();
        console.log('Response:', data);
        if (response.ok) {
            openResponsePopup(data.response);
            clearInputs();
        } else {
            throw new Error(data.detail || 'Unknown error');
        }
    } catch (error) {
        console.error('Error:', error);
        errorElement.textContent = 'Error: ' + error.message;
    }
});

function openResponsePopup(response) {
    const responsePageUrl = `/response?response=${encodeURIComponent(response)}`;
    const popupWidth = 600;
    const popupHeight = 400;
    const left = (window.innerWidth - popupWidth) / 2;
    const top = (window.innerHeight - popupHeight) / 2;
    const popupOptions = `width=${popupWidth},height=${popupHeight},left=${left},top=${top},scrollbars=yes,resizable=yes`;

    window.open(responsePageUrl, '_blank', popupOptions);
}

function clearInputs() {
    document.getElementById('subject').value = '';
    document.getElementById('topic').value = '';
    document.getElementById('subtopic').value = '';
    document.getElementById('prompt').value = '';
}
