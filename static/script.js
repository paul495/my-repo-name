const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('fileElem');
const myForm = document.querySelector('.my-form');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const processBtn = document.getElementById('process-btn');
const loader = document.getElementById('loader');
const results = document.getElementById('results');
const errorMsg = document.getElementById('error-message');
const languageSelect = document.getElementById('language');
const taskSelect = document.getElementById('task');
const resetBtn = document.getElementById('reset-btn');
const dlTxtBtn = document.getElementById('dl-txt');
const dlSrtBtn = document.getElementById('dl-srt');
const dlJsonBtn = document.getElementById('dl-json');

let currentFile = null;
let lastData = null;

// Prevent default drag behaviors
;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Highlight drop area when item is dragged over it
;['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
});

;['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    dropArea.classList.add('highlight');
}

function unhighlight(e) {
    dropArea.classList.remove('highlight');
}

// Handle dropped files
dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length === 0) return;
    
    const file = files[0];
    
    // Check if it's an MP4
    if (file.type !== 'video/mp4' && !file.name.toLowerCase().endsWith('.mp4')) {
        showError("Only MP4 files are supported.");
        return;
    }
    
    currentFile = file;
    myForm.classList.add('hidden');
    fileInfo.classList.remove('hidden');
    fileName.textContent = file.name;
    
    processBtn.disabled = false;
    hideError();
}

function clearSelection() {
    currentFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    myForm.classList.remove('hidden');
    processBtn.disabled = true;
    hideError();
}

function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.classList.remove('hidden');
}

function hideError() {
    errorMsg.classList.add('hidden');
}

// Handle process upload
processBtn.addEventListener('click', async () => {
    if (!currentFile) return;

    // Reset UI
    hideError();
    results.classList.add('hidden');
    processBtn.disabled = true;
    
    // Show Loader
    loader.classList.remove('hidden');
    dropArea.style.opacity = '0.5';
    dropArea.style.pointerEvents = 'none';

    const formData = new FormData();
    formData.append('video', currentFile);
    formData.append('language', languageSelect.value);
    formData.append('task', taskSelect.value);

    try {
        const response = await fetch('/transcribe', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Server responded with an error');
        }
        
        lastData = data;

        // Display results
        document.getElementById('res-language').textContent = data.language || 'Unknown';
        document.getElementById('res-text').textContent = data.text || 'No text extracted.';
        document.getElementById('res-json').textContent = JSON.stringify(data, null, 2);
        
        results.classList.remove('hidden');

    } catch (err) {
        showError(err.message);
    } finally {
        // Hide Loader & Reset Drop Area
        loader.classList.add('hidden');
        dropArea.style.opacity = '1';
        dropArea.style.pointerEvents = 'auto';
        processBtn.disabled = false;
    }
});

// Reset Form
resetBtn.addEventListener('click', () => {
    clearSelection();
    results.classList.add('hidden');
});

// Download logic
function downloadFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

dlTxtBtn.addEventListener('click', () => {
    if (!lastData) return;
    downloadFile('transcription.txt', lastData.text || '', 'text/plain');
});

dlSrtBtn.addEventListener('click', () => {
    if (!lastData) return;
    downloadFile('transcription.srt', lastData.srt_content || '', 'text/plain');
});

dlJsonBtn.addEventListener('click', () => {
    if (!lastData) return;
    const jsonStr = JSON.stringify(lastData, null, 2);
    downloadFile('transcription.json', jsonStr, 'application/json');
});
