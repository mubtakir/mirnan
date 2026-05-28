document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const promptInput = document.getElementById('prompt-input');
    const chatContainer = document.getElementById('chat-container');
    const modeSelect = document.getElementById('mode-select');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    const betaSlider = document.getElementById('beta-slider');
    const betaValue = document.getElementById('beta-value');
    const kBSlider = document.getElementById('kB-slider');
    const kBValue = document.getElementById('kB-value');
    const meterSelect = document.getElementById('meter-select');
    const rhymeInput = document.getElementById('rhyme-input');
    const poeticOptions = document.getElementById('poetic-options');
    const cascadeToggle = document.getElementById('cascade-toggle');
    const cascadeStrengthSlider = document.getElementById('cascade-strength-slider');
    const cascadeStrengthValue = document.getElementById('cascade-strength-value');
    const dialogueToggle = document.getElementById('dialogue-toggle');

    // New split workspace element handles
    const fieldResultsContainer = document.getElementById('field-results-container');
    const calibrationSidebar = document.getElementById('calibration-sidebar');
    const letterGrid = document.getElementById('letter-grid');
    const selectedLetterHeader = document.getElementById('selected-letter-header');
    const slidersContainer = document.getElementById('sliders-container');
    const saveCalibrationBtn = document.getElementById('save-calibration-btn');
    const newBenchmarkWordInput = document.getElementById('new-benchmark-word');
    const addBenchmarkWordBtn = document.getElementById('add-benchmark-word-btn');
    const benchmarkWordsList = document.getElementById('benchmark-words-list');
    const vocabTypeSelect = document.getElementById('vocab-type-select');
    const hebbianBoostToggle = document.getElementById('hebbian-boost-toggle');
    const attractedWordsList = document.getElementById('attracted-words-list');
    const repelledWordsList = document.getElementById('repelled-words-list');

    // Sidebar & calibration state
    let currentLetter = null;
    let letterVectors = {};
    let dimNames = [];
    let isDirty = false;
    let benchmarkWords = [];

    const ARABIC_DIM_LABELS = {
        "concentration": "تركيز",
        "internal_external": "داخلي/خارجي",
        "stability_motion": "ثبات/حركة",
        "density": "كثافة",
        "temperature": "حرارة",
        "time_accumulation": "تراكم زمني",
        "time_peak": "ذروة زمنية",
        "time_discharge": "تفريغ زمني",
        "motion_linear": "حركة خطية",
        "motion_rotary": "حركة دورانية",
        "motion_pulse": "حركة نبضية",
        "motion_stretch": "حركة تمددية",
        "motion_slip": "حركة انزلاقية",
        "motion_air": "حركة هوائية",
        "axis_v": "محور عمودي",
        "mass": "كتلة",
        "hardness_solid": "صلابة",
        "penetration": "تغلغل/اختراق",
        "charge": "شحنة",
        "reference_self": "مرجعية ذاتية",
        "space_extensionality": "امتداد مكاني",
        "time_causality": "سببية زمنية"
    };

    betaSlider.addEventListener('input', () => {
        betaValue.textContent = parseFloat(betaSlider.value).toFixed(1);
    });
    kBSlider.addEventListener('input', () => {
        kBValue.textContent = parseFloat(kBSlider.value).toFixed(1);
    });

    cascadeToggle.addEventListener('change', () => {
        cascadeStrengthSlider.disabled = !cascadeToggle.checked;
    });
    cascadeStrengthSlider.addEventListener('input', () => {
        cascadeStrengthValue.textContent = parseFloat(cascadeStrengthSlider.value).toFixed(1);
    });

    // Handle Generation mode dynamic layout updates
    modeSelect.addEventListener('change', () => {
        poeticOptions.style.display = modeSelect.value === 'poetic' ? 'flex' : 'none';
        
        if (modeSelect.value === 'attract') {
            promptInput.placeholder = "أدخل كلمة أو حرفاً لفحص حقل الجذب والتنافر الفيزيائي...";
            chatContainer.style.display = 'none';
            fieldResultsContainer.style.display = 'flex';
            calibrationSidebar.style.display = 'flex';
            
            // Load initialization data
            loadLetters();
            loadBenchmarkVocab();
        } else {
            promptInput.placeholder = "اكتب رسالتك هنا...";
            chatContainer.style.display = 'flex';
            fieldResultsContainer.style.display = 'none';
            calibrationSidebar.style.display = 'none';
        }
    });

    // Letter Calibration APIs
    async function loadLetters() {
        try {
            const response = await fetch('/api/letters');
            const data = await response.json();
            dimNames = data.dim_names;
            letterVectors = {};
            for (const [ch, info] of Object.entries(data.letters)) {
                letterVectors[ch] = info.v;
            }
            renderLetterGrid();
        } catch (error) {
            console.error("Failed to load letters:", error);
        }
    }

    const ARABIC_LETTERS_ORDER = "أبتثجحخدذرزسشصضطظعغفقكلمنهوي".split("");
    function renderLetterGrid() {
        letterGrid.innerHTML = '';
        ARABIC_LETTERS_ORDER.forEach(ch => {
            if (letterVectors[ch]) {
                const btn = document.createElement('button');
                btn.className = 'letter-btn';
                btn.textContent = ch;
                btn.type = 'button';
                if (currentLetter === ch) {
                    btn.classList.add('active');
                }
                btn.addEventListener('click', () => selectLetter(ch));
                letterGrid.appendChild(btn);
            }
        });
    }

    function selectLetter(letter) {
        currentLetter = letter;
        document.querySelectorAll('.letter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.textContent === letter);
        });
        selectedLetterHeader.textContent = `معايرة الحرف: ${letter}`;
        renderSliders(letter);
        saveCalibrationBtn.disabled = true;
        isDirty = false;
    }

    function renderSliders(letter) {
        slidersContainer.innerHTML = '';
        const vector = letterVectors[letter];
        dimNames.forEach((name, idx) => {
            const val = vector[idx];
            const group = document.createElement('div');
            group.className = 'dim-slider-group';
            
            const labelText = ARABIC_DIM_LABELS[name] || name;
            
            group.innerHTML = `
                <div class="dim-slider-label">
                    <span>${labelText}</span>
                    <span class="dim-val" id="val-${name}">${val.toFixed(2)}</span>
                </div>
                <input type="range" class="dim-slider" id="slider-${name}" min="-1" max="1" step="0.05" value="${val}">
            `;
            
            const slider = group.querySelector('input');
            slider.addEventListener('input', (e) => {
                const newVal = parseFloat(e.target.value);
                document.getElementById(`val-${name}`).textContent = newVal.toFixed(2);
                
                // Update internal values
                letterVectors[letter][idx] = newVal;
                isDirty = true;
                saveCalibrationBtn.disabled = false;
                
                updateSliderTrack(slider, newVal);
                triggerFieldUpdate();
            });
            
            slidersContainer.appendChild(group);
            updateSliderTrack(slider, val);
        });
    }

    function updateSliderTrack(slider, value) {
        const pct = (value + 1) / 2 * 100;
        slider.style.background = `linear-gradient(to right, #ef4444 0%, #ef4444 ${pct}%, #10b981 ${pct}%, #10b981 100%)`;
    }

    let updateTimeout = null;
    function triggerFieldUpdate() {
        if (updateTimeout) return;
        updateTimeout = setTimeout(() => {
            updateTimeout = null;
            sendLetterUpdate(currentLetter, letterVectors[currentLetter]);
        }, 45);
    }

    async function sendLetterUpdate(letter, vector) {
        try {
            await fetch('/api/letters/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({letter, vector})
            });
            recalculateField();
        } catch (error) {
            console.error("Failed to update letter:", error);
        }
    }

    saveCalibrationBtn.addEventListener('click', () => {
        if (!currentLetter || !isDirty) return;
        saveCalibrationBtn.disabled = true;
        isDirty = false;
        saveCalibrationBtn.innerHTML = '<i class="fa-solid fa-check"></i> تم الحفظ!';
        setTimeout(() => {
            saveCalibrationBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> حفظ المعايرة';
        }, 1500);
    });

    // Benchmark Vocabulary Manager APIs
    async function loadBenchmarkVocab() {
        try {
            const response = await fetch('/api/benchmark');
            const data = await response.json();
            benchmarkWords = data.words;
            renderBenchmarkVocab();
        } catch (error) {
            console.error("Failed to load benchmark vocabulary:", error);
        }
    }

    function renderBenchmarkVocab() {
        benchmarkWordsList.innerHTML = '';
        benchmarkWords.forEach(w => {
            const tag = document.createElement('div');
            tag.className = 'benchmark-tag';
            tag.innerHTML = `
                <span>${w}</span>
                <span class="delete-tag"><i class="fa-solid fa-xmark"></i></span>
            `;
            tag.querySelector('.delete-tag').addEventListener('click', () => deleteBenchmarkWord(w));
            benchmarkWordsList.appendChild(tag);
        });
    }

    async function deleteBenchmarkWord(word) {
        benchmarkWords = benchmarkWords.filter(w => w !== word);
        renderBenchmarkVocab();
        await saveBenchmarkVocab();
        recalculateField();
    }

    async function addBenchmarkWord() {
        const word = newBenchmarkWordInput.value.trim();
        if (!word) return;
        if (!benchmarkWords.includes(word)) {
            benchmarkWords.push(word);
            renderBenchmarkVocab();
            await saveBenchmarkVocab();
            recalculateField();
        }
        newBenchmarkWordInput.value = '';
    }

    async function saveBenchmarkVocab() {
        try {
            await fetch('/api/benchmark/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({words: benchmarkWords})
            });
        } catch (error) {
            console.error("Failed to save benchmark vocabulary:", error);
        }
    }

    addBenchmarkWordBtn.addEventListener('click', addBenchmarkWord);
    newBenchmarkWordInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addBenchmarkWord();
        }
    });

    // Field Calculation Updates
    async function recalculateField() {
        const target = promptInput.dataset.lastTarget || "";
        if (!target) return;
        
        const vocabType = vocabTypeSelect.value;
        const useHebbian = hebbianBoostToggle.checked;
        
        try {
            const response = await fetch(`/api/field?target=${encodeURIComponent(target)}&vocab_type=${vocabType}&use_hebbian=${useHebbian}`);
            const data = await response.json();
            renderFieldResults(data);
        } catch (error) {
            console.error("Failed to calculate attraction field:", error);
        }
    }

    vocabTypeSelect.addEventListener('change', recalculateField);
    hebbianBoostToggle.addEventListener('change', recalculateField);

    function renderFieldResults(data) {
        attractedWordsList.innerHTML = '';
        repelledWordsList.innerHTML = '';
        
        if (data.attracted && data.attracted.length > 0) {
            data.attracted.forEach(([word, score]) => {
                attractedWordsList.appendChild(createWordCard(word, score));
            });
        } else {
            attractedWordsList.innerHTML = '<div class="word-card"><div class="word-card-header"><span class="word-name">لا توجد نتائج</span></div></div>';
        }
        
        if (data.repelled && data.repelled.length > 0) {
            data.repelled.forEach(([word, score]) => {
                repelledWordsList.appendChild(createWordCard(word, score));
            });
        } else {
            repelledWordsList.innerHTML = '<div class="word-card"><div class="word-card-header"><span class="word-name">لا توجد نتائج</span></div></div>';
        }
    }

    function createWordCard(word, score) {
        const card = document.createElement('div');
        card.className = 'word-card';
        const pct = Math.min(Math.max(Math.abs(score) * 100, 0), 100);
        
        card.innerHTML = `
            <div class="word-card-header">
                <span class="word-name">${word}</span>
                <span class="word-score">${score >= 0 ? '+' : ''}${score.toFixed(3)}</span>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width: ${pct}%"></div>
            </div>
        `;
        return card;
    }

    // Markdown Parser
    function parseMarkdown(text) {
        if (!text) return "";
        let html = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/`(.*?)`/g, '<code>$1</code>');

        let lines = html.split('\n');
        let inList = false;
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i].trim();
            if (line.startsWith('- ')) {
                if (!inList) {
                    lines[i] = '<ul><li>' + line.substring(2) + '</li>';
                    inList = true;
                } else {
                    lines[i] = '<li>' + line.substring(2) + '</li>';
                }
            } else {
                if (inList) {
                    lines[i] = '</ul>' + (line ? '<p>' + line + '</p>' : '');
                    inList = false;
                } else if (line) {
                    if (!line.startsWith('<h') && !line.startsWith('<ul') && !line.startsWith('<li')) {
                        lines[i] = '<p>' + line + '</p>';
                    }
                }
            }
        }
        if (inList) {
            lines.push('</ul>');
        }
        return lines.join('\n');
    }

    function addMessage(content, type) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}-message`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (type === 'bot' || type === 'system') {
            contentDiv.innerHTML = parseMarkdown(content);
        } else {
            contentDiv.textContent = content;
        }

        msgDiv.appendChild(contentDiv);
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return msgDiv;
    }

    function addPhysicsReport(msgDiv, report, timeTaken) {
        if (!report) return;

        const reportDiv = document.createElement('div');
        reportDiv.className = 'physics-report';

        const addStat = (icon, label) => {
            const s = document.createElement('div');
            s.className = 'physics-stat';
            s.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${label}</span>`;
            reportDiv.appendChild(s);
        };

        addStat('fa-stopwatch', `${timeTaken.toFixed(3)}s`);
        addStat('fa-wave-square', `S=${report.entropy}`);
        addStat('fa-fire', `β=${report.beta}`);
        addStat('fa-temperature-high', `k_B=${report.k_B}`);

        if (report.dccf_coupling !== undefined) {
            addStat('fa-link', `DCCF=${report.dccf_coupling}`);
        }
        if (report.ppm_field !== undefined) {
            addStat('fa-magnet', `PPM=${report.ppm_field}`);
        }
        if (report.amfs_centrality !== undefined) {
            addStat('fa-weight-scale', `AMFS=${report.amfs_centrality}`);
        }
        if (report.cascade_enabled !== undefined) {
            addStat('fa-circle-down', `CASCADE=${report.cascade_enabled ? 'ON' : 'OFF'}(${report.cascade_strength})`);
        }
        if (report.dialogue_mode) {
            addStat('fa-comments', `DIALOGUE=${report.dialogue_intent}(${report.dialogue_confidence})`);
        }
        if (report.mass_mean) {
            addStat('fa-weight-hanging', `M=${report.mass_mean.toFixed(2)}`);
        }
        if (report.mode) {
            addStat('fa-microchip', report.mode);
        }

        msgDiv.insertAdjacentElement('afterend', reportDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Chat submit handler
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const prompt = promptInput.value.trim();
        if (!prompt) return;

        // Custom handling for attraction field mode
        if (modeSelect.value === 'attract') {
            promptInput.dataset.lastTarget = prompt;
            promptInput.value = '';
            
            recalculateField();
            
            if (prompt.length === 1 && letterVectors[prompt]) {
                selectLetter(prompt);
            }
            return;
        }

        const mode = modeSelect.value;
        const beta = parseFloat(betaSlider.value);
        const k_B = parseFloat(kBSlider.value);

        promptInput.value = '';
        promptInput.disabled = true;
        sendBtn.disabled = true;

        addMessage(prompt, 'user');
        typingIndicator.style.display = 'flex';
        chatContainer.scrollTop = chatContainer.scrollHeight;

        const body = {
            prompt: prompt,
            mode: mode,
            max_words: 30,
            beta: beta,
            k_B: k_B,
            cascade: cascadeToggle.checked,
            cascade_strength: cascadeToggle.checked ? parseFloat(cascadeStrengthSlider.value) : null,
            dialogue: dialogueToggle.checked,
        };

        if (mode === 'poetic') {
            body.poetic_meter = meterSelect.value;
            if (rhymeInput.value.trim()) {
                body.poetic_rhyme = rhymeInput.value.trim();
            }
        }

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate response');
            }

            const data = await response.json();
            typingIndicator.style.display = 'none';

            const botMsg = addMessage(data.result || '(No output generated)', 'bot');
            addPhysicsReport(botMsg, data.physics_report, data.time_taken);

        } catch (error) {
            typingIndicator.style.display = 'none';
            addMessage(`خطأ النظام: ${error.message}`, 'system');
        } finally {
            promptInput.disabled = false;
            sendBtn.disabled = false;
            promptInput.focus();
        }
    });
});
