// AI Skin Analysis App JavaScript

class SkinAnalysisApp {
    constructor() {
        this.currentStream = null;
        this.currentFacingMode = 'user'; // 'user' for front camera, 'environment' for back camera
        this.analysisResults = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.checkCameraSupport();
    }

    async checkCameraSupport() {
        console.log('🔍 Checking camera support...');
        
        try {
            if (!navigator.mediaDevices) {
                console.warn('⚠️ navigator.mediaDevices not available');
                return;
            }

            if (!navigator.mediaDevices.getUserMedia) {
                console.warn('⚠️ getUserMedia not available');
                return;
            }

            // Check available devices
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');
            
            console.log(`📹 Found ${videoDevices.length} video input devices:`);
            videoDevices.forEach((device, index) => {
                console.log(`  ${index + 1}. ${device.label || 'Camera ' + (index + 1)} (${device.deviceId})`);
            });

            if (videoDevices.length === 0) {
                console.warn('⚠️ No video input devices found');
            }

        } catch (error) {
            console.error('❌ Error checking camera support:', error);
        }
    }

    setupEventListeners() {
        // File upload
        const fileInput = document.getElementById('file-input');
        const uploadZone = document.getElementById('upload-zone');
        
        if (fileInput && uploadZone) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
            uploadZone.addEventListener('click', () => fileInput.click());
        }

        // Camera controls
        const captureBtn = document.getElementById('capture-btn');
        const switchCameraBtn = document.getElementById('switch-camera-btn');
        
        if (captureBtn) {
            captureBtn.addEventListener('click', () => this.capturePhoto());
        }
        
        if (switchCameraBtn) {
            switchCameraBtn.addEventListener('click', () => this.switchCamera());
        }

        // Analysis button
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeImage());
        }

        // Download report button
        const downloadBtn = document.getElementById('download-report-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadReport());
        }
    }

    setupDragAndDrop() {
        const uploadZone = document.getElementById('upload-zone');
        if (!uploadZone) return;

        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });

        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });
    }

    // Navigation functions
    scrollToAnalysis() {
        const analysisSection = document.getElementById('analysis-section');
        if (analysisSection) {
            analysisSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Upload method selection
    activateFileUpload() {
        this.hideAllSections();
        this.showSection('file-upload-section');
        this.setActiveUploadMethod(0);
    }

    activateCamera() {
        console.log('🎥 Activating camera mode...');
        this.hideAllSections();
        this.showSection('camera-section');
        this.setActiveUploadMethod(1);
        
        // Add a small delay to ensure the section is visible before starting camera
        setTimeout(() => {
            this.startCamera();
        }, 100);
    }

    setActiveUploadMethod(index) {
        const methods = document.querySelectorAll('.upload-method');
        methods.forEach((method, i) => {
            method.classList.toggle('active', i === index);
        });
    }

    // Section visibility
    hideAllSections() {
        const sections = [
            'file-upload-section',
            'camera-section', 
            'preview-section',
            'loading-section',
            'results-section'
        ];
        
        sections.forEach(id => this.hideSection(id));
    }

    showSection(id) {
        const section = document.getElementById(id);
        if (section) {
            section.style.display = 'block';
            section.classList.add('fade-in');
        }
    }

    hideSection(id) {
        const section = document.getElementById(id);
        if (section) {
            section.style.display = 'none';
            section.classList.remove('fade-in');
        }
    }

    // File handling
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    }

    handleFile(file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showToast('Please select a valid image file.', 'error');
            return;
        }

        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            this.showToast('File size must be less than 16MB.', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.displayImagePreview(e.target.result);
        };
        reader.readAsDataURL(file);
    }

    // Camera functions
    async startCamera() {
        console.log('🎥 Starting camera...');
        
        try {
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Camera not supported in this browser');
            }

            const video = document.getElementById('camera-video');
            if (!video) {
                console.error('❌ Camera video element not found');
                return;
            }

            console.log('📹 Video element found, requesting camera access...');

            // Stop existing stream
            if (this.currentStream) {
                console.log('🛑 Stopping existing camera stream...');
                this.currentStream.getTracks().forEach(track => track.stop());
            }

            // Request camera permissions with fallback constraints
            let constraints = {
                video: {
                    facingMode: this.currentFacingMode,
                    width: { ideal: 640, max: 1280 },
                    height: { ideal: 480, max: 720 }
                }
            };

            console.log('📱 Requesting camera with constraints:', constraints);

            try {
                this.currentStream = await navigator.mediaDevices.getUserMedia(constraints);
            } catch (constraintError) {
                console.warn('⚠️ Specific constraints failed, trying basic video only...');
                // Fallback to basic video if specific constraints fail
                constraints = { video: true };
                this.currentStream = await navigator.mediaDevices.getUserMedia(constraints);
            }

            console.log('✅ Camera stream obtained successfully');
            
            // Set video source and wait for it to load
            video.srcObject = this.currentStream;
            
            // Update camera status
            this.updateCameraStatus('Connecting to camera...');
            
            // Wait for video to start playing
            video.addEventListener('loadedmetadata', () => {
                console.log('📺 Video metadata loaded, starting playback...');
                this.updateCameraStatus('Starting video stream...');
                
                video.play().then(() => {
                    console.log('▶️ Video playback started successfully');
                    this.updateCameraStatus('Camera ready!', true);
                    this.enableCameraControls(true);
                    this.showToast('Camera started successfully!', 'success');
                }).catch(playError => {
                    console.error('❌ Video play error:', playError);
                    this.updateCameraStatus('Video playback failed', false);
                    this.showToast('Camera loaded but playback failed', 'warning');
                });
            });

            // Handle video errors
            video.addEventListener('error', (e) => {
                console.error('❌ Video element error:', e);
                this.showToast('Video playback error', 'error');
            });

        } catch (error) {
            console.error('❌ Camera error:', error);
            
            let errorMessage = 'Failed to access camera. ';
            
            if (error.name === 'NotAllowedError') {
                errorMessage += 'Please allow camera permissions and try again.';
                this.updateCameraStatus('Camera permission denied', false);
            } else if (error.name === 'NotFoundError') {
                errorMessage += 'No camera device found.';
                this.updateCameraStatus('No camera found', false);
            } else if (error.name === 'NotSupportedError') {
                errorMessage += 'Camera not supported in this browser.';
                this.updateCameraStatus('Camera not supported', false);
            } else {
                errorMessage += error.message || 'Unknown error occurred.';
                this.updateCameraStatus('Camera error occurred', false);
            }
            
            this.enableCameraControls(false);
            this.showToast(errorMessage, 'error');
        }
    }

    updateCameraStatus(message, isSuccess = null) {
        const statusElement = document.getElementById('camera-status-text');
        if (statusElement) {
            statusElement.textContent = message;
            
            // Update status color based on success state
            const statusContainer = statusElement.closest('.camera-status small');
            if (statusContainer) {
                statusContainer.className = 'text-muted';
                if (isSuccess === true) {
                    statusContainer.className = 'text-success';
                } else if (isSuccess === false) {
                    statusContainer.className = 'text-danger';
                }
            }
        }
    }

    enableCameraControls(enable) {
        const captureBtn = document.getElementById('capture-btn');
        const switchBtn = document.getElementById('switch-camera-btn');
        
        if (captureBtn) {
            captureBtn.disabled = !enable;
        }
        
        if (switchBtn) {
            switchBtn.disabled = !enable;
        }
    }

    switchCamera() {
        this.currentFacingMode = this.currentFacingMode === 'user' ? 'environment' : 'user';
        this.startCamera();
    }

    capturePhoto() {
        console.log('📸 Capturing photo...');
        
        const video = document.getElementById('camera-video');
        const canvas = document.getElementById('camera-canvas');
        
        if (!video) {
            console.error('❌ Video element not found');
            this.showToast('Video element not found', 'error');
            return;
        }
        
        if (!canvas) {
            console.error('❌ Canvas element not found');
            this.showToast('Canvas element not found', 'error');
            return;
        }

        // Check if video is playing and has dimensions
        if (video.videoWidth === 0 || video.videoHeight === 0) {
            console.error('❌ Video not ready or has no dimensions');
            this.showToast('Camera not ready. Please wait for camera to load.', 'error');
            return;
        }

        console.log(`📏 Video dimensions: ${video.videoWidth}x${video.videoHeight}`);

        try {
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // Draw the video frame to canvas
            context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
            
            // Convert to image data URL
            const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
            
            console.log('✅ Photo captured successfully');
            console.log(`📊 Image data length: ${imageDataUrl.length} characters`);
            
            // Display the captured image
            this.displayImagePreview(imageDataUrl);
            
            // Stop camera after successful capture
            if (this.currentStream) {
                console.log('🛑 Stopping camera after capture...');
                this.currentStream.getTracks().forEach(track => track.stop());
                this.currentStream = null;
            }
            
            this.showToast('Photo captured successfully!', 'success');
            
        } catch (error) {
            console.error('❌ Capture error:', error);
            this.showToast('Failed to capture photo', 'error');
        }
    }

    // Image preview
    displayImagePreview(imageDataUrl) {
        this.hideAllSections();
        this.showSection('preview-section');
        
        const previewImg = document.getElementById('preview-image');
        if (previewImg) {
            previewImg.src = imageDataUrl;
        }
        
        // Store image data for analysis
        this.currentImageData = imageDataUrl;
    }

    // Analysis functions
    async analyzeImage() {
        if (!this.currentImageData) {
            this.showToast('No image to analyze.', 'error');
            return;
        }

        this.hideAllSections();
        this.showSection('loading-section');

        try {
            const formData = new FormData();
            
            // Convert data URL to blob if it's from camera
            if (this.currentImageData.startsWith('data:')) {
                const response = await fetch(this.currentImageData);
                const blob = await response.blob();
                formData.append('camera_image', this.currentImageData);
            }

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                this.analysisResults = result;
                this.displayResults(result);
            } else {
                throw new Error(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showToast(`Analysis failed: ${error.message}`, 'error');
            this.hideSection('loading-section');
            this.showSection('preview-section');
        }
    }

    displayResults(results) {
        this.hideAllSections();
        this.showSection('results-section');

        // Display skin condition
        const conditionElement = document.getElementById('skin-condition');
        if (conditionElement) {
            conditionElement.textContent = results.skin_condition || 'Unknown';
        }

        // Display confidence
        const confidenceBar = document.getElementById('confidence-bar');
        const confidenceText = document.getElementById('confidence-text');
        const confidence = (results.confidence || 0) * 100;
        
        if (confidenceBar) {
            confidenceBar.style.width = `${confidence}%`;
            confidenceBar.setAttribute('aria-valuenow', confidence);
        }
        
        if (confidenceText) {
            confidenceText.textContent = `${confidence.toFixed(1)}% confident`;
        }

        // Update condition icon
        this.updateConditionIcon(results.skin_condition);

        // Display recommendations
        this.displayRecommendations(results.recommendations || []);

        // Display skincare tips
        this.displaySkincareTips(results.skin_condition);

        this.showToast('Analysis completed successfully!', 'success');
    }

    updateConditionIcon(condition) {
        const iconElement = document.getElementById('condition-icon');
        if (!iconElement) return;

        const iconMap = {
            'Normal': 'fa-face-smile',
            'Dry': 'fa-droplet',
            'Oily': 'fa-oil-can',
            'Acne': 'fa-exclamation-triangle',
            'Sensitive': 'fa-shield-heart',
            'Pigmentation': 'fa-palette',
            'Wrinkles': 'fa-clock'
        };

        const iconClass = iconMap[condition] || 'fa-question-circle';
        iconElement.className = `fas ${iconClass} fa-4x text-primary`;
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendations-container');
        if (!container) return;

        if (recommendations.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No recommendations available.</p>';
            return;
        }

        let html = '';
        recommendations.forEach(product => {
            const skinTypes = this.getSkinTypesBadges(product);
            const priceInfo = this.formatPriceWithINR(product.Price);
            const ingredients = this.formatIngredients(product.Ingredients);
            
            html += `
                <div class="product-card">
                    <div class="row">
                        <div class="col-md-12">
                            <div class="product-header">
                                <div class="product-brand">${product.Brand || 'Unknown Brand'}</div>
                                <h6 class="product-name">${product.Name || 'Product Name'}</h6>
                            </div>
                            <div class="product-info-grid">
                                <div class="product-rating mb-2">
                                    <span class="rating-stars">
                                        ${'★'.repeat(Math.floor(product.Rank || 0))}${'☆'.repeat(5 - Math.floor(product.Rank || 0))}
                                    </span>
                                    <span class="rating-text text-muted">(${product.Rank || 'N/A'})</span>
                                </div>
                                <div class="product-pricing mb-3">
                                    ${priceInfo}
                                </div>
                                <div class="skin-type-badges mb-3">
                                    <strong>Suitable for:</strong>
                                    ${skinTypes}
                                </div>
                                <div class="product-ingredients">
                                    <div class="ingredients-header">
                                        <strong><i class="fas fa-flask text-info me-1"></i> Key Ingredients:</strong>
                                        <button class="btn btn-sm btn-outline-info ms-2" onclick="this.parentElement.nextElementSibling.classList.toggle('d-none')">
                                            <i class="fas fa-eye me-1"></i>View Details
                                        </button>
                                    </div>
                                    <div class="ingredients-content d-none mt-2">
                                        ${ingredients.summary}
                                        <div class="full-ingredients mt-2">
                                            <small class="text-muted">
                                                <strong>Complete Formula:</strong><br>
                                                ${ingredients.full}
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    formatPriceWithINR(usdPrice) {
        if (!usdPrice || usdPrice === 'N/A') {
            return '<div class="price-display"><span class="price-usd">Price: N/A</span></div>';
        }

        // Convert USD to INR (approximate rate: 1 USD = 83 INR)
        const exchangeRate = 83;
        const inrPrice = (parseFloat(usdPrice) * exchangeRate).toFixed(0);
        
        return `
            <div class="price-display">
                <div class="price-usd">
                    <i class="fas fa-dollar-sign text-success me-1"></i>
                    <strong>$${usdPrice} USD</strong>
                </div>
                <div class="price-inr">
                    <i class="fas fa-rupee-sign text-primary me-1"></i>
                    <strong>₹${inrPrice} INR</strong>
                </div>
                <small class="text-muted">*Approximate conversion</small>
            </div>
        `;
    }

    formatIngredients(ingredients) {
        if (!ingredients || ingredients === 'N/A' || ingredients.trim() === '') {
            return {
                summary: '<span class="text-muted">Ingredients information not available</span>',
                full: '<span class="text-muted">Complete ingredients list not provided</span>'
            };
        }

        // Split ingredients by comma and clean them
        const ingredientsList = ingredients.split(',').map(ing => ing.trim());
        
        // Get key ingredients (first 6-8 ingredients are usually the most important)
        const keyIngredients = ingredientsList.slice(0, 6);
        
        // Create key ingredients summary with benefits
        const keyIngredientsWithBenefits = keyIngredients.map(ingredient => {
            const benefits = this.getIngredientBenefits(ingredient);
            return `<span class="ingredient-tag" title="${benefits}">${ingredient}</span>`;
        }).join(' ');

        // Format full ingredients list
        const fullIngredientsList = ingredientsList.join(', ');
        
        return {
            summary: `
                <div class="key-ingredients">
                    ${keyIngredientsWithBenefits}
                    ${ingredientsList.length > 6 ? '<span class="text-muted">+' + (ingredientsList.length - 6) + ' more...</span>' : ''}
                </div>
            `,
            full: fullIngredientsList
        };
    }

    getIngredientBenefits(ingredient) {
        const ingredientBenefits = {
            'Water': 'Base solvent and hydration',
            'Glycerin': 'Humectant that draws moisture to skin',
            'Hyaluronic Acid': 'Intense hydration and plumping',
            'Niacinamide': 'Pore refinement and oil control',
            'Retinol': 'Anti-aging and cell renewal',
            'Salicylic Acid': 'Exfoliation and acne treatment',
            'Vitamin C': 'Antioxidant and brightening',
            'Ceramides': 'Barrier repair and protection',
            'Peptides': 'Collagen boost and firming',
            'Alpha Hydroxy Acids': 'Exfoliation and texture improvement',
            'Beta Hydroxy Acid': 'Deep pore cleansing',
            'Squalane': 'Lightweight moisturizing',
            'Dimethicone': 'Silicone for smooth application',
            'Butylene Glycol': 'Humectant and texture enhancer',
            'Tocopherol': 'Vitamin E antioxidant protection',
            'Allantoin': 'Soothing and healing',
            'Panthenol': 'Pro-vitamin B5 for hydration',
            'Sodium Hyaluronate': 'Smaller molecule hyaluronic acid'
        };

        // Check if ingredient name contains any known beneficial ingredients
        for (const [key, benefit] of Object.entries(ingredientBenefits)) {
            if (ingredient.toLowerCase().includes(key.toLowerCase())) {
                return benefit;
            }
        }

        return 'Cosmetic ingredient for product formulation';
    }

    getSkinTypesBadges(product) {
        const skinTypes = ['Normal', 'Dry', 'Oily', 'Combination', 'Sensitive'];
        let badges = '';
        
        skinTypes.forEach(type => {
            const isActive = product[type] === 1;
            const badgeClass = isActive ? 'skin-type-badge active' : 'skin-type-badge';
            badges += `<span class="${badgeClass}">${type}</span>`;
        });

        return badges;
    }

    displaySkincareTips(skinCondition) {
        const doTipsContainer = document.getElementById('do-tips-container');
        const dontTipsContainer = document.getElementById('dont-tips-container');
        
        if (!doTipsContainer || !dontTipsContainer) return;

        const skincareTips = this.getSkincareTips(skinCondition);
        
        // Display DO tips
        let doHtml = '<ul class="list-unstyled">';
        skincareTips.dos.forEach(tip => {
            doHtml += `
                <li class="mb-2">
                    <i class="fas fa-check text-success me-2"></i>
                    <span>${tip}</span>
                </li>
            `;
        });
        doHtml += '</ul>';
        doTipsContainer.innerHTML = doHtml;

        // Display DON'T tips
        let dontHtml = '<ul class="list-unstyled">';
        skincareTips.donts.forEach(tip => {
            dontHtml += `
                <li class="mb-2">
                    <i class="fas fa-times text-danger me-2"></i>
                    <span>${tip}</span>
                </li>
            `;
        });
        dontHtml += '</ul>';
        dontTipsContainer.innerHTML = dontHtml;
    }

    getSkincareTips(skinCondition) {
        const tipsDatabase = {
            'Normal': {
                dos: [
                    'Use a gentle cleanser twice daily to maintain your skin\'s natural balance',
                    'Apply a lightweight moisturizer to keep your skin hydrated',
                    'Use sunscreen with at least SPF 30 daily for protection',
                    'Exfoliate 1-2 times per week with a mild scrub',
                    'Maintain a consistent skincare routine',
                    'Drink plenty of water and eat a balanced diet',
                    'Get adequate sleep for skin repair and regeneration'
                ],
                donts: [
                    'Don\'t over-cleanse or use harsh scrubs that can disrupt skin balance',
                    'Don\'t skip moisturizer even if your skin feels fine',
                    'Don\'t use too many products at once - keep it simple',
                    'Don\'t neglect sunscreen on cloudy days',
                    'Don\'t pick at your skin or pop pimples',
                    'Don\'t sleep with makeup on',
                    'Don\'t ignore changes in your skin condition'
                ]
            },
            'Dry': {
                dos: [
                    'Use a cream-based or oil-based cleanser to avoid stripping natural oils',
                    'Apply a rich, thick moisturizer immediately after cleansing',
                    'Use a humidifier in dry environments',
                    'Choose products with hyaluronic acid, ceramides, or glycerin',
                    'Take shorter, lukewarm showers instead of hot ones',
                    'Apply face oil or overnight mask for extra hydration',
                    'Drink plenty of water throughout the day'
                ],
                donts: [
                    'Don\'t use alcohol-based toners or astringents',
                    'Don\'t skip moisturizer, especially at night',
                    'Don\'t over-exfoliate - limit to once per week',
                    'Don\'t use foaming cleansers that can dry out your skin',
                    'Don\'t take long, hot showers or baths',
                    'Don\'t use products with harsh fragrances',
                    'Don\'t forget to moisturize your neck and chest area'
                ]
            },
            'Oily': {
                dos: [
                    'Use a gentle foaming cleanser to remove excess oil',
                    'Apply a lightweight, oil-free moisturizer',
                    'Use salicylic acid or niacinamide to control oil production',
                    'Exfoliate 2-3 times per week to unclog pores',
                    'Use clay masks once a week to absorb excess oil',
                    'Choose non-comedogenic makeup and skincare products',
                    'Blot excess oil with blotting papers during the day'
                ],
                donts: [
                    'Don\'t over-cleanse - it can increase oil production',
                    'Don\'t skip moisturizer thinking it will make you more oily',
                    'Don\'t use harsh scrubs that can irritate and inflame skin',
                    'Don\'t touch your face frequently with unwashed hands',
                    'Don\'t use heavy, oil-based products',
                    'Don\'t squeeze or pick at blackheads and pimples',
                    'Don\'t use products with alcohol that can over-dry skin'
                ]
            },
            'Acne': {
                dos: [
                    'Use a gentle, non-comedogenic cleanser twice daily',
                    'Apply acne treatments with salicylic acid or benzoyl peroxide',
                    'Use a lightweight, oil-free moisturizer to prevent dryness',
                    'Spot-treat active breakouts with targeted treatments',
                    'Change pillowcases regularly to avoid bacterial buildup',
                    'Be consistent with your acne treatment routine',
                    'Consult a dermatologist for persistent or severe acne'
                ],
                donts: [
                    'Don\'t pop, squeeze, or pick at pimples and blackheads',
                    'Don\'t use multiple acne treatments at once',
                    'Don\'t scrub aggressively - it can worsen inflammation',
                    'Don\'t use heavy, pore-clogging makeup or skincare',
                    'Don\'t skip sunscreen when using acne treatments',
                    'Don\'t give up on treatments too quickly - allow 6-8 weeks',
                    'Don\'t use dirty makeup brushes or tools'
                ]
            },
            'Sensitive': {
                dos: [
                    'Use fragrance-free and hypoallergenic products',
                    'Patch test new products on a small area first',
                    'Choose gentle, cream-based cleansers',
                    'Apply products with calming ingredients like aloe or chamomile',
                    'Use mineral sunscreen instead of chemical sunscreen',
                    'Keep your skincare routine simple and minimal',
                    'Apply cool compresses to soothe irritated skin'
                ],
                donts: [
                    'Don\'t use products with strong fragrances or essential oils',
                    'Don\'t try multiple new products at the same time',
                    'Don\'t use physical scrubs or harsh exfoliants',
                    'Don\'t use products with alcohol, parabens, or sulfates',
                    'Don\'t expose your skin to extreme temperatures',
                    'Don\'t rub or scrub your skin harshly when cleansing',
                    'Don\'t ignore allergic reactions or persistent irritation'
                ]
            },
            'Pigmentation': {
                dos: [
                    'Use a broad-spectrum sunscreen daily to prevent further darkening',
                    'Apply vitamin C serum in the morning for antioxidant protection',
                    'Use products with niacinamide to help even skin tone',
                    'Consider gentle chemical exfoliants like lactic acid',
                    'Be patient - pigmentation takes months to improve',
                    'Use products consistently for best results',
                    'Consult a dermatologist for professional treatment options'
                ],
                donts: [
                    'Don\'t skip sunscreen - UV exposure worsens pigmentation',
                    'Don\'t use harsh scrubs that can worsen dark spots',
                    'Don\'t expect overnight results from pigmentation treatments',
                    'Don\'t pick at scabs or dark spots',
                    'Don\'t use too many brightening products at once',
                    'Don\'t forget to treat your neck and hands too',
                    'Don\'t use expired or unregulated whitening products'
                ]
            },
            'Wrinkles': {
                dos: [
                    'Use a retinoid or retinol product to boost collagen production',
                    'Apply a rich moisturizer with peptides and hyaluronic acid',
                    'Use sunscreen daily to prevent further sun damage',
                    'Consider eye cream for the delicate under-eye area',
                    'Stay hydrated and maintain a healthy diet',
                    'Get adequate sleep to support skin repair',
                    'Consider professional treatments like chemical peels'
                ],
                donts: [
                    'Don\'t start with strong retinoids - begin with lower concentrations',
                    'Don\'t forget to moisturize when using anti-aging treatments',
                    'Don\'t neglect your neck and décolletage area',
                    'Don\'t smoke - it accelerates skin aging',
                    'Don\'t sleep on your face - it can worsen sleep lines',
                    'Don\'t use harsh exfoliants that can thin the skin',
                    'Don\'t expect immediate results - anti-aging takes time'
                ]
            }
        };

        return tipsDatabase[skinCondition] || tipsDatabase['Normal'];
    }

    // Report download
    async downloadReport() {
        if (!this.analysisResults) {
            this.showToast('No analysis results to download.', 'error');
            return;
        }

        try {
            const response = await fetch('/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.analysisResults)
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `skin_analysis_report_${new Date().toISOString().slice(0, 10)}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showToast('Report downloaded successfully!', 'success');
            } else {
                throw new Error('Failed to generate report');
            }
        } catch (error) {
            console.error('Download error:', error);
            this.showToast('Failed to download report.', 'error');
        }
    }

    // Reset functionality
    resetUpload() {
        this.hideAllSections();
        this.currentImageData = null;
        this.analysisResults = null;
        
        // Stop camera if running
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
            this.currentStream = null;
        }

        // Reset file input
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.value = '';
        }

        // Remove active states
        const methods = document.querySelectorAll('.upload-method');
        methods.forEach(method => method.classList.remove('active'));
    }

    // Toast notifications
    showToast(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const toastMessage = document.getElementById('toast-message');
        
        if (!toast || !toastMessage) return;

        // Set message
        toastMessage.textContent = message;
        
        // Set icon based on type
        const toastHeader = toast.querySelector('.toast-header i');
        const iconMap = {
            success: 'fa-check-circle text-success',
            error: 'fa-exclamation-triangle text-danger',
            warning: 'fa-exclamation-circle text-warning',
            info: 'fa-info-circle text-primary'
        };
        
        if (toastHeader) {
            toastHeader.className = `fas ${iconMap[type] || iconMap.info} me-2`;
        }

        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
}

// Global functions for HTML onclick handlers
function scrollToAnalysis() {
    app.scrollToAnalysis();
}

function activateFileUpload() {
    app.activateFileUpload();
}

function activateCamera() {
    app.activateCamera();
}

function resetUpload() {
    app.resetUpload();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.app = new SkinAnalysisApp();
});

// Handle page visibility changes (pause camera when tab is not visible)
document.addEventListener('visibilitychange', function() {
    if (document.hidden && window.app && window.app.currentStream) {
        // Optionally pause camera when tab is hidden to save resources
        console.log('Tab hidden, camera still running');
    }
});

// Handle beforeunload to cleanup camera
window.addEventListener('beforeunload', function() {
    if (window.app && window.app.currentStream) {
        window.app.currentStream.getTracks().forEach(track => track.stop());
    }
});