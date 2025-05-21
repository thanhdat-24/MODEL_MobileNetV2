document.addEventListener("DOMContentLoaded", function () {
    // Fade-in animation for elements
    const fadeElements = document.querySelectorAll('.fade-in');

    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('active');
                }, 100);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    fadeElements.forEach(element => {
        fadeInObserver.observe(element);
    });

    // Drop zone functionality
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fruit360-imageUpload');
    const multiImageContainer = document.getElementById('multiImageContainer');
    const previewImage = document.getElementById('previewImage');
    const recognizeBtn = document.getElementById('recognizeBtn');
    const changeImageBtn = document.getElementById('changeImageBtn');
    const loadingContainer = document.getElementById('loadingContainer');
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsList = document.getElementById('resultsList');
    const shareResultsBtn = document.getElementById('shareResultsBtn');
    const downloadResultsBtn = document.getElementById('downloadResultsBtn');
    const recognitionTips = document.getElementById('recognitionTips');
    const recognitionModeToggle = document.getElementById('recognitionModeToggle');
    const singleModeBtn = document.getElementById('singleModeBtn');
    const multiModeBtn = document.getElementById('multiModeBtn');

    // Check if we're on a page with the fruit recognition UI
    if (!dropZone) {
        return; // Exit the function if we're not on the recognition page
    }

    // Biến theo dõi chế độ nhận diện (đơn hoặc đa ảnh)
    let isMultiMode = false;
    let uploadedFiles = [];

    // Chuyển đổi giữa chế độ đơn và đa ảnh
    if (singleModeBtn && multiModeBtn) {
        singleModeBtn.addEventListener('click', function() {
            switchRecognitionMode(false);
        });

        multiModeBtn.addEventListener('click', function() {
            switchRecognitionMode(true);
        });
    }

    function switchRecognitionMode(multi) {
        isMultiMode = multi;
        if (isMultiMode) {
            if (singleModeBtn) singleModeBtn.classList.remove('active');
            if (multiModeBtn) multiModeBtn.classList.add('active');
            if (multiImageContainer) {
                multiImageContainer.style.display = 'grid';
            }
            if (previewImage) {
                previewImage.style.display = 'none';
            }
            if (fileInput) fileInput.setAttribute('multiple', 'multiple');
            if (dropZone) dropZone.classList.add('multi-mode');
            
            // Reset UI state for multi mode
            if (dropZone && dropZone.classList.contains('has-image')) {
                dropZone.classList.remove('has-image');
                uploadedFiles = [];
                if (multiImageContainer) {
                    multiImageContainer.innerHTML = '';
                }
            }
        } else {
            if (singleModeBtn) singleModeBtn.classList.add('active');
            if (multiModeBtn) multiModeBtn.classList.remove('active');
            if (multiImageContainer) {
                multiImageContainer.style.display = 'none';
            }
            if (previewImage) {
                previewImage.style.display = 'block';
            }
            if (fileInput) fileInput.removeAttribute('multiple');
            if (dropZone) dropZone.classList.remove('multi-mode');
            
            // Reset UI state for single mode
            if (dropZone && dropZone.classList.contains('has-image')) {
                dropZone.classList.remove('has-image');
                if (previewImage) previewImage.src = '#';
            }
        }
        
        // Cập nhật UI
        if (recognizeBtn) recognizeBtn.disabled = true;
        if (changeImageBtn) changeImageBtn.style.display = 'none';
        if (resultsContainer) resultsContainer.style.display = 'none';
        updateTipsVisibility();
        
        // Ẩn search results container nếu có
        const searchResultsContainer = document.getElementById('searchResultsContainer');
        if (searchResultsContainer) {
            searchResultsContainer.style.display = 'none';
        }
    }

    // Cập nhật hiển thị mẹo khi thay đổi ảnh
    function updateTipsVisibility() {
        if (dropZone && dropZone.classList.contains('has-image')) {
            if (recognitionTips) recognitionTips.style.display = 'none';
        } else {
            if (recognitionTips) recognitionTips.style.display = 'block';
        }
    }

    // Initialize change image button state
    if (changeImageBtn) changeImageBtn.style.display = 'none';

    // Handle file selection via input
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            handleFiles(this.files);
            updateTipsVisibility();
        });
    }

    // Set up the drop zone event listeners
    if (dropZone) {
        ['dragover', 'dragenter', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        ['dragover', 'dragenter'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        // Handle file drop
        dropZone.addEventListener('drop', handleDrop, false);

        // Initialize drop zone click to select file
        dropZone.addEventListener('click', function () {
            if (!dropZone.classList.contains('has-image') && fileInput) {
                fileInput.click();
            }
        });
    }

    // Prevent default behaviors
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Add highlight class
    function highlight() {
        if (dropZone) dropZone.classList.add('highlight');
    }

    // Remove highlight class
    function unhighlight() {
        if (dropZone) dropZone.classList.remove('highlight');
    }

    // Handle the dropped files
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle the selected files
    function handleFiles(files) {
        if (files.length) {
            if (isMultiMode) {
                // Xử lý nhiều ảnh
                uploadedFiles = [];
                if (multiImageContainer) {
                    multiImageContainer.innerHTML = '';
                }

                Array.from(files).forEach((file, index) => {
                    if (!file.type.match('image.*')) {
                        return;
                    }

                    uploadedFiles.push(file);
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        // Tạo preview cho mỗi ảnh
                        const imagePreview = document.createElement('div');
                        imagePreview.className = 'multi-image-preview';
                        
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'preview-thumbnail';
                        
                        const removeBtn = document.createElement('button');
                        removeBtn.className = 'remove-image-btn';
                        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
                        removeBtn.dataset.index = index;
                        
                        removeBtn.addEventListener('click', function(e) {
                            e.stopPropagation();
                            const idx = parseInt(this.dataset.index);
                            // Xóa file khỏi mảng
                            uploadedFiles.splice(idx, 1);
                            // Xóa preview
                            this.parentElement.remove();
                            // Cập nhật lại indices cho các nút remove
                            document.querySelectorAll('.remove-image-btn').forEach((btn, i) => {
                                btn.dataset.index = i;
                            });
                            
                            // Nếu không còn ảnh nào
                            if (uploadedFiles.length === 0) {
                                dropZone.classList.remove('has-image');
                                recognizeBtn.disabled = true;
                                changeImageBtn.style.display = 'none';
                                updateTipsVisibility();
                            }
                        });
                        
                        imagePreview.appendChild(img);
                        imagePreview.appendChild(removeBtn);
                        multiImageContainer.appendChild(imagePreview);
                    };
                    
                    reader.readAsDataURL(file);
                });
                
                if (uploadedFiles.length > 0) {
                    dropZone.classList.add('has-image');
                    recognizeBtn.disabled = false;
                    changeImageBtn.style.display = 'block';
                }
            } else {
                // Xử lý một ảnh như hiện tại
                const file = files[0];

                if (!file.type.match('image.*')) {
                    alert('Vui lòng chọn file hình ảnh!');
                    return;
                }

                const reader = new FileReader();

                reader.onload = function (e) {
                    previewImage.src = e.target.result;
                    dropZone.classList.add('has-image');
                    recognizeBtn.disabled = false;
                    changeImageBtn.style.display = 'block';
                    updateTipsVisibility();
                };

                reader.readAsDataURL(file);
            }
        }
    }

    // Change image button click
    changeImageBtn.addEventListener('click', function () {
        dropZone.classList.remove('has-image');
        
        if (isMultiMode) {
            uploadedFiles = [];
            if (multiImageContainer) {
                multiImageContainer.innerHTML = '';
            }
        } else {
            previewImage.src = '#';
        }
        
        fileInput.value = '';
        recognizeBtn.disabled = true;
        changeImageBtn.style.display = 'none';
        resultsContainer.style.display = 'none';
        
        // Ẩn search results container nếu có
        const searchResultsContainer = document.getElementById('searchResultsContainer');
        if (searchResultsContainer) {
            searchResultsContainer.style.display = 'none';
        }
        
        updateTipsVisibility();
    });

    // Recognize button click
    recognizeBtn.addEventListener('click', function () {
        if (isMultiMode) {
            if (uploadedFiles.length === 0) {
                alert('Vui lòng chọn ít nhất một hình ảnh trước khi nhận diện!');
                return;
            }
            
            // Show loading, hide results
            loadingContainer.style.display = 'block';
            resultsContainer.style.display = 'none';
            
            // Ẩn search results container
            const searchResultsContainer = document.getElementById('searchResultsContainer');
            if (searchResultsContainer) {
                searchResultsContainer.style.display = 'none';
            }
            
            recognizeBtn.disabled = true;

            // Create form data for multiple images
            const formData = new FormData();
            uploadedFiles.forEach((file, index) => {
                formData.append('files[]', file);
            });
            formData.append('mode', 'multi');

            // Thêm tuỳ chọn để bỏ qua kiểm tra AI nếu cần thiết (nút skip_check)
            const skipCheckCheckbox = document.getElementById('skipAICheck');
            if (skipCheckCheckbox && skipCheckCheckbox.checked) {
                formData.append('skip_check', 'true');
            }

            // Send request to server
            fetch('/predict-multi', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading
                loadingContainer.style.display = 'none';
                recognizeBtn.disabled = false;

                // Kiểm tra xem có phải lỗi do ảnh không hợp lệ
                if (!data.success) {
                    if (data.invalid_images && data.invalid_images.length > 0) {
                        showInvalidImagesError(data.invalid_images, data.error || 'Ảnh không hợp lệ');
                        return;
                    } else if (data.error) {
                        alert('Lỗi: ' + data.error);
                        console.error('Lỗi:', data.error);
                        return;
                    }
                }

                // Clear previous results
                resultsList.innerHTML = '';
                
                // Show upload summary message
                const summaryMessage = document.createElement('div');
                summaryMessage.className = 'upload-summary';

                // Hiển thị thông báo ảnh không hợp lệ nếu có
                if (data.invalid_images && data.invalid_images.length > 0) {
                    summaryMessage.innerHTML = `
                        <div class="upload-warning-message">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>Đã bỏ qua ${data.invalid_images.length} hình ảnh không phù hợp.</span>
                        </div>
                        <div class="upload-success-message">
                            <i class="fas fa-check-circle"></i>
                            <span>Đã lưu thành công ${data.total_images} hình ảnh vào lịch sử!</span>
                        </div>
                    `;
                } else {
                    summaryMessage.innerHTML = `
                        <div class="upload-success-message">
                            <i class="fas fa-check-circle"></i>
                            <span>Đã lưu thành công ${data.total_images} hình ảnh vào lịch sử!</span>
                        </div>
                    `;
                }
                
                resultsList.appendChild(summaryMessage);

                // Add group results
                data.group_results.forEach((item, index) => {
                    setTimeout(() => {
                        const resultCard = document.createElement('div');
                        resultCard.className = 'result-card group-result';

                        resultCard.innerHTML = `
                            <div class="result-rank">${index + 1}</div>
                            <div class="result-info">
                                <h4 class="result-name">${item.label} <span class="fruit-count">${item.count} ${item.count > 1 ? 'quả' : 'quả'}</span></h4>
                                <div class="result-percent">${(item.confidence * 100).toFixed(1)}% độ chính xác</div>
                                <div class="result-progress">
                                    <div class="result-bar" style="width: ${(item.confidence * 100).toFixed(1)}%"></div>
                                </div>
                            </div>
                        `;

                        resultsList.appendChild(resultCard);
                    }, index * 150); // Stagger animations
                });

                // Show results container
                resultsContainer.style.display = 'block';
                resultsContainer.querySelector('.results-title').innerHTML = '<i class="fas fa-check-circle"></i> Kết Quả Nhận Diện Nhóm';

                // Display image thumbnails if available
                if (data.thumbnails && data.thumbnails.length > 0) {
                    displayImageThumbnails(data.thumbnails);
                }
                
                // Hiển thị ảnh không hợp lệ nếu có
                if (data.invalid_images && data.invalid_images.length > 0) {
                    displayInvalidImages(data.invalid_images);
                }
            })
            .catch(error => {
                loadingContainer.style.display = 'none';
                recognizeBtn.disabled = false;
                alert('Có lỗi xảy ra khi nhận diện nhiều ảnh!');
                console.error('Lỗi:', error);
            });
            
        } else {
            // Xử lý nhận diện một ảnh
            const fileInput = document.getElementById('fruit360-imageUpload');
            if (!fileInput.files.length) {
                alert('Vui lòng chọn hình ảnh trước khi nhận diện!');
                return;
            }

            // Show loading, hide results
            loadingContainer.style.display = 'block';
            resultsContainer.style.display = 'none';
            
            // Ẩn search results container
            const searchResultsContainer = document.getElementById('searchResultsContainer');
            if (searchResultsContainer) {
                searchResultsContainer.style.display = 'none';
            }
            
            recognizeBtn.disabled = true;

            // Create form data for single image
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('mode', 'single');
            
            // Thêm tuỳ chọn để bỏ qua kiểm tra AI nếu cần thiết
            const skipCheckCheckbox = document.getElementById('skipAICheck');
            if (skipCheckCheckbox && skipCheckCheckbox.checked) {
                formData.append('skip_check', 'true');
            }

            // Send request to server
            fetch('/predict', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    // Hide loading
                    loadingContainer.style.display = 'none';
                    recognizeBtn.disabled = false;

                    // Kiểm tra phản hồi có thành công không
                    if (!data.success) {
                        if (data.message) {
                            // Hiển thị modal thông báo lỗi với chi tiết
                            showErrorMessage("Ảnh không hợp lệ", data.message, data.image);
                        } else {
                            alert('Lỗi: ' + (data.error || 'Không thể nhận diện ảnh'));
                        }
                        console.error('Lỗi:', data.error || data.message);
                        return;
                    }

                    // Clear previous results
                    resultsList.innerHTML = '';

                    // Add new results
                    data.predictions.forEach((item, index) => {
                        setTimeout(() => {
                            const confidence = (item.confidence * 100).toFixed(1);
                            const resultCard = document.createElement('div');
                            resultCard.className = 'result-card';

                            resultCard.innerHTML = `
                                <div class="result-rank">${index + 1}</div>
                                <div class="result-info">
                                    <h4 class="result-name">${item.label}</h4>
                                    <div class="result-percent">${confidence}% độ chính xác</div>
                                    <div class="result-progress">
                                        <div class="result-bar" style="width: ${confidence}%"></div>
                                    </div>
                                </div>
                            `;

                            resultsList.appendChild(resultCard);
                        }, index * 150); // Stagger animations
                    });

                    // Show results container
                    resultsContainer.style.display = 'block';
                    resultsContainer.querySelector('.results-title').innerHTML = '<i class="fas fa-check-circle"></i> Kết Quả Nhận Diện';

                    // Handle search results if available
                    if (data.search_results && data.search_results.length > 0) {
                        displaySearchResults(data.search_results, data.search_reason);
                    }
                })
                .catch(error => {
                    loadingContainer.style.display = 'none';
                    recognizeBtn.disabled = false;
                    alert('Có lỗi xảy ra khi nhận diện!');
                    console.error('Lỗi:', error);
                });
        }
    });

    // Function to display image thumbnails
    function displayImageThumbnails(thumbnails) {
        let thumbnailsContainer = document.getElementById('imageThumbnailsContainer');
        
        // Create container if it doesn't exist
        if (!thumbnailsContainer) {
            thumbnailsContainer = document.createElement('div');
            thumbnailsContainer.id = 'imageThumbnailsContainer';
            thumbnailsContainer.className = 'thumbnails-container';
            
            // Insert after resultsContainer
            resultsContainer.parentNode.insertBefore(thumbnailsContainer, resultsContainer.nextSibling);
        } else {
            thumbnailsContainer.innerHTML = ''; // Clear existing thumbnails
        }
        
        const thumbnailsHeader = document.createElement('div');
        thumbnailsHeader.className = 'thumbnails-header';
        thumbnailsHeader.innerHTML = '<h4><i class="fas fa-images"></i> Các hình ảnh đã nhận diện</h4>';
        thumbnailsContainer.appendChild(thumbnailsHeader);
        
        const thumbnailsGrid = document.createElement('div');
        thumbnailsGrid.className = 'thumbnails-grid';
        
        thumbnails.forEach((thumbnail, index) => {
            const thumbnailCard = document.createElement('div');
            thumbnailCard.className = 'thumbnail-card';
            
            thumbnailCard.innerHTML = `
                <img src="${thumbnail.image}" alt="Ảnh ${index + 1}">
                <div class="thumbnail-label">
                    <span>${thumbnail.label}</span>
                    <span class="thumbnail-confidence">${(thumbnail.confidence * 100).toFixed(1)}%</span>
                </div>
            `;
            
            thumbnailsGrid.appendChild(thumbnailCard);
        });
        
        thumbnailsContainer.appendChild(thumbnailsGrid);
        thumbnailsContainer.style.display = 'block';
    }

    // Function to display search results
    function displaySearchResults(searchResults, searchReasons) {
        let searchResultsContainer = document.getElementById('searchResultsContainer');

        // Create container if it doesn't exist
        if (!searchResultsContainer) {
            searchResultsContainer = document.createElement('div');
            searchResultsContainer.id = 'searchResultsContainer';
            searchResultsContainer.className = 'search-results-container';

            // Insert after resultsContainer
            resultsContainer.parentNode.insertBefore(searchResultsContainer, resultsContainer.nextSibling);
        }

        searchResultsContainer.innerHTML = `
            <div class="search-results-header">
                <h4>🔍 Tìm kiếm ảnh tương tự</h4>
                <p class="search-reason">Tìm kiếm vì: ${searchReasons ? searchReasons.join(', ') : 'Độ chính xác thấp'}</p>
            </div>
            <div class="search-results-grid" id="searchResultsList">
                ${searchResults.map((item, index) => `
                    <div class="search-result-card">
                        <img src="${item.thumbnail}" alt="${item.title}" onerror="this.src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=='">
                        <div class="search-info">
                            <a href="${item.link}" target="_blank">${item.title}</a>
                            <p class="search-source">${item.source}</p>
                            <div class="search-confidence">${(item.confidence * 100).toFixed(1)}% similarity</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        searchResultsContainer.style.display = 'block';
    }

    // Share results button
    shareResultsBtn.addEventListener('click', function () {
        // Share implementation (this is a placeholder)
        // In a real implementation, this would use the Web Share API or a custom sharing dialog
        alert('Tính năng chia sẻ kết quả sẽ được phát triển trong tương lai!');
    });

    // Download results button
    downloadResultsBtn.addEventListener('click', function () {
        // Download implementation (this is a placeholder)
        // In a real implementation, this would generate a PDF or image of the results
        alert('Tính năng tải về kết quả sẽ được phát triển trong tương lai!');
    });

    // Product filtering
    const filterButtons = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Get filter value
            const filterValue = this.getAttribute('data-filter');

            // Filter products
            productCards.forEach(card => {
                if (filterValue === 'all') {
                    card.style.display = 'block';
                } else {
                    const categories = card.getAttribute('data-category').split(' ');

                    if (categories.includes(filterValue)) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
        });
    });

    // Khởi tạo chế độ nhận diện mặc định (đơn ảnh)
    if (singleModeBtn && multiModeBtn) {
        switchRecognitionMode(false);
    }

    // Kiểm tra hiển thị mẹo ban đầu
    updateTipsVisibility();

    // Kiểm tra có hash fragment #multiMode để mở chế độ đa ảnh
    if (window.location.hash === '#multiMode' && document.getElementById('multiModeBtn')) {
        const multiModeBtn = document.getElementById('multiModeBtn');
        if (multiModeBtn) {
            setTimeout(() => {
                multiModeBtn.click();
                // Cuộn tới khu vực nhận diện
                document.querySelector('.recognition-section').scrollIntoView({ behavior: 'smooth' });
            }, 500);
        }
    }

    // Hàm hiển thị thông báo lỗi khi ảnh không hợp lệ
    function showErrorMessage(title, message, image) {
        // Tạo modal nếu chưa có
        let errorModal = document.getElementById('errorModal');
        if (!errorModal) {
            errorModal = document.createElement('div');
            errorModal.id = 'errorModal';
            errorModal.className = 'error-modal';
            errorModal.innerHTML = `
                <div class="error-modal-content">
                    <div class="error-modal-header">
                        <h3 id="errorModalTitle"></h3>
                        <button class="error-modal-close">&times;</button>
                    </div>
                    <div class="error-modal-body">
                        <div class="error-image-container">
                            <img id="errorModalImage" src="" alt="Ảnh lỗi">
                        </div>
                        <div class="error-message-container">
                            <p id="errorModalMessage"></p>
                        </div>
                        <div id="technicalErrorContainer" class="technical-error-container">
                            <div class="tech-error-header">
                                <span class="tech-error-title">Chi tiết kỹ thuật</span>
                                <button id="toggleTechError" class="toggle-tech-error">Hiển thị</button>
                            </div>
                            <div id="technicalErrorContent" class="tech-error-content">
                                <code id="technicalErrorMessage"></code>
                            </div>
                        </div>
                    </div>
                    <div class="error-modal-footer">
                        <button class="btn btn-outline-secondary error-modal-close mr-2">Hủy</button>
                        <button id="tryAgainBtn" class="btn btn-primary">Thử lại</button>
                    </div>
                </div>
            `;
            document.body.appendChild(errorModal);
            
            // Thêm CSS cho modal
            if (!document.getElementById('errorModalStyles')) {
                const style = document.createElement('style');
                style.id = 'errorModalStyles';
                style.textContent = `
                    .error-modal {
                        display: none;
                        position: fixed;
                        z-index: 10000;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(0, 0, 0, 0.5);
                        animation: fadeIn 0.3s;
                    }
                    
                    @keyframes fadeIn {
                        from { opacity: 0; }
                        to { opacity: 1; }
                    }
                    
                    .error-modal-content {
                        background-color: #fff;
                        margin: 5% auto;
                        padding: 0;
                        border-radius: 8px;
                        width: 80%;
                        max-width: 550px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                        animation: slideIn 0.3s;
                        overflow: hidden;
                    }
                    
                    @keyframes slideIn {
                        from { transform: translateY(-50px); opacity: 0; }
                        to { transform: translateY(0); opacity: 1; }
                    }
                    
                    .error-modal-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        background-color: #f44336;
                        color: white;
                        padding: 15px 20px;
                    }
                    
                    .error-modal-header h3 {
                        color: white;
                        margin: 0;
                        font-size: 18px;
                        display: flex;
                        align-items: center;
                        font-weight: 500;
                    }
                    
                    .error-modal-header h3:before {
                        content: '\\f071';
                        font-family: 'Font Awesome 5 Free';
                        font-weight: 900;
                        margin-right: 10px;
                    }
                    
                    .error-modal-close {
                        background: none;
                        border: none;
                        font-size: 22px;
                        cursor: pointer;
                        color: rgba(255, 255, 255, 0.8);
                        transition: color 0.2s;
                    }
                    
                    .error-modal-close:hover {
                        color: white;
                    }
                    
                    .error-modal-body {
                        display: flex;
                        flex-direction: column;
                        padding: 20px;
                    }
                    
                    .error-image-container {
                        text-align: center;
                        margin-bottom: 15px;
                        max-height: 250px;
                        overflow: hidden;
                        border-radius: 4px;
                        border: 1px solid #eee;
                    }
                    
                    .error-image-container img {
                        max-width: 100%;
                        max-height: 250px;
                        object-fit: contain;
                    }
                    
                    .error-message-container {
                        background-color: #fff8f8;
                        padding: 15px;
                        border-radius: 4px;
                        border-left: 4px solid #f44336;
                        margin-bottom: 15px;
                    }
                    
                    .error-message-container p {
                        margin: 0;
                        color: #333;
                        line-height: 1.6;
                        font-size: 15px;
                    }
                    
                    .technical-error-container {
                        background-color: #f8f9fa;
                        border-radius: 4px;
                        margin-bottom: 10px;
                        overflow: hidden;
                        border: 1px solid #eee;
                    }
                    
                    .tech-error-header {
                        display: flex;
                        justify-content: space-between;
                        padding: 10px 15px;
                        background-color: #f1f1f1;
                        align-items: center;
                    }
                    
                    .tech-error-title {
                        font-size: 14px;
                        color: #555;
                        font-weight: 500;
                    }
                    
                    .toggle-tech-error {
                        background: none;
                        border: none;
                        color: #007bff;
                        cursor: pointer;
                        font-size: 13px;
                        padding: 0;
                    }
                    
                    .tech-error-content {
                        display: none;
                        padding: 15px;
                        background-color: #2d2d2d;
                        color: #f1f1f1;
                        font-family: monospace;
                        border-radius: 0 0 4px 4px;
                        overflow-x: auto;
                    }
                    
                    .tech-error-content code {
                        white-space: pre-wrap;
                        word-break: break-word;
                        color: #f1f1f1;
                    }
                    
                    .error-modal-footer {
                        display: flex;
                        justify-content: flex-end;
                        padding: 15px 20px;
                        background-color: #f8f9fa;
                        border-top: 1px solid #eee;
                    }
                    
                    .error-modal-footer button {
                        margin-left: 10px;
                    }
                    
                    .mr-2 {
                        margin-right: 10px;
                    }
                    
                    @media (max-width: 768px) {
                        .error-modal-content {
                            width: 95%;
                            margin: 10% auto;
                        }
                    }
                `;
                document.head.appendChild(style);
            }
            
            // Thêm sự kiện đóng modal
            const closeButtons = errorModal.querySelectorAll('.error-modal-close');
            closeButtons.forEach(button => {
                button.addEventListener('click', function() {
                    errorModal.style.display = 'none';
                });
            });
            
            // Đóng modal khi click ra ngoài
            window.addEventListener('click', function(event) {
                if (event.target === errorModal) {
                    errorModal.style.display = 'none';
                }
            });
            
            // Sự kiện cho nút thử lại
            const tryAgainBtn = errorModal.querySelector('#tryAgainBtn');
            if (tryAgainBtn) {
                tryAgainBtn.addEventListener('click', function() {
                    errorModal.style.display = 'none';
                    
                    // Reset bộ chọn file và làm mới giao diện
                    if (document.getElementById('fileInput')) {
                        document.getElementById('fileInput').value = '';
                    }
                    
                    // Ẩn kết quả trước đó nếu có
                    if (document.getElementById('resultsContainer')) {
                        document.getElementById('resultsContainer').style.display = 'none';
                    }
                });
            }
        }
        
        // Tìm kiếm lỗi kỹ thuật trong thông báo
        const technicalErrorContainer = document.getElementById('technicalErrorContainer');
        const technicalErrorContent = document.getElementById('technicalErrorContent');
        const technicalErrorMessage = document.getElementById('technicalErrorMessage');
        const toggleTechErrorBtn = document.getElementById('toggleTechError');
        
        // Kiểm tra nếu có lỗi kỹ thuật trong message
        const technicalErrorMatch = message.match(/127\.0\.0\.1.*|Lỗi:.*|ONNX.*|Error:.*|Exception:.*|Invalid.*/i);
        
        if (technicalErrorMatch && technicalErrorContainer && technicalErrorMessage) {
            // Tách thông báo người dùng và lỗi kỹ thuật
            const userMessage = message.replace(technicalErrorMatch[0], '').trim();
            const techError = technicalErrorMatch[0];
            
            // Cập nhật nội dung
            document.getElementById('errorModalMessage').textContent = userMessage || "Ảnh đầu vào không phải là rau củ quả hoặc chất lượng quá kém để nhận diện vui lòng chọn ảnh phù hợp";
            technicalErrorMessage.textContent = techError;
            technicalErrorContainer.style.display = 'block';
            
            // Thêm sự kiện ẩn/hiện chi tiết kỹ thuật
            if (toggleTechErrorBtn) {
                toggleTechErrorBtn.addEventListener('click', function() {
                    if (technicalErrorContent.style.display === 'block') {
                        technicalErrorContent.style.display = 'none';
                        toggleTechErrorBtn.textContent = 'Hiển thị';
                    } else {
                        technicalErrorContent.style.display = 'block';
                        toggleTechErrorBtn.textContent = 'Ẩn';
                    }
                });
            }
        } else {
            // Không có lỗi kỹ thuật, chỉ hiển thị thông báo người dùng
            document.getElementById('errorModalMessage').textContent = message;
            if (technicalErrorContainer) {
                technicalErrorContainer.style.display = 'none';
            }
        }
        
        // Cập nhật nội dung modal
        document.getElementById('errorModalTitle').textContent = title;
        if (image) {
            document.getElementById('errorModalImage').src = image;
            document.getElementById('errorModalImage').style.display = 'block';
        } else {
            document.getElementById('errorModalImage').style.display = 'none';
        }
        
        // Hiển thị modal
        errorModal.style.display = 'block';
    }
    
    // Hiển thị danh sách các ảnh không hợp lệ với lỗi
    function showInvalidImagesError(invalidImages, errorMessage) {
        // Tạo modal hiển thị danh sách ảnh không hợp lệ
        let errorModal = document.getElementById('invalidImagesModal');
        if (!errorModal) {
            errorModal = document.createElement('div');
            errorModal.id = 'invalidImagesModal';
            errorModal.className = 'error-modal';
            
            const modalContent = document.createElement('div');
            modalContent.className = 'error-modal-content invalid-images-content';
            
            modalContent.innerHTML = `
                <div class="error-modal-header">
                    <h3 id="invalidModalTitle">Ảnh không hợp lệ</h3>
                    <button class="error-modal-close">&times;</button>
                </div>
                <div class="error-modal-body">
                    <div class="error-message-container" id="errorSummary"></div>
                    <div class="invalid-images-grid" id="invalidImagesGrid"></div>
                </div>
                <div class="error-modal-footer">
                    <button class="btn btn-outline-secondary error-modal-close mr-2">Hủy</button>
                    <button id="tryAgainBtn" class="btn btn-primary">Thử lại</button>
                </div>
            `;
            
            errorModal.appendChild(modalContent);
            document.body.appendChild(errorModal);
            
            // Thêm CSS cho danh sách ảnh không hợp lệ
            if (!document.getElementById('invalidImagesStyles')) {
                const style = document.createElement('style');
                style.id = 'invalidImagesStyles';
                style.textContent = `
                    .invalid-images-content {
                        max-width: 800px;
                    }
                    
                    .invalid-images-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                        gap: 15px;
                        max-height: 400px;
                        overflow-y: auto;
                        padding: 5px;
                        margin-bottom: 10px;
                    }
                    
                    .invalid-image-item {
                        background: #fff;
                        border-radius: 8px;
                        overflow: hidden;
                        transition: all 0.2s;
                        border: 1px solid #eee;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                    }
                    
                    .invalid-image-item:hover {
                        transform: translateY(-3px);
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    }
                    
                    .invalid-image-preview {
                        height: 150px;
                        background: #f8f9fa;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        overflow: hidden;
                        position: relative;
                    }
                    
                    .invalid-image-preview img {
                        width: 100%;
                        height: 100%;
                        object-fit: cover;
                    }
                    
                    .invalid-image-preview::after {
                        content: '\\f057';
                        font-family: 'Font Awesome 5 Free';
                        font-weight: 900;
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        color: #f44336;
                        background: rgba(255,255,255,0.9);
                        border-radius: 50%;
                        font-size: 18px;
                        width: 24px;
                        height: 24px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    
                    .invalid-image-message {
                        padding: 10px;
                        font-size: 13px;
                        color: #555;
                        border-top: 1px solid #eee;
                        background: #fff;
                    }
                    
                    @media (max-width: 768px) {
                        .invalid-images-grid {
                            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
                        }
                        
                        .invalid-image-preview {
                            height: 120px;
                        }
                    }
                `;
                document.head.appendChild(style);
            }
            
            // Thêm sự kiện đóng modal
            const closeButtons = errorModal.querySelectorAll('.error-modal-close');
            closeButtons.forEach(button => {
                button.addEventListener('click', function() {
                    errorModal.style.display = 'none';
                });
            });
            
            // Đóng modal khi click ra ngoài
            window.addEventListener('click', function(event) {
                if (event.target === errorModal) {
                    errorModal.style.display = 'none';
                }
            });
            
            // Sự kiện cho nút thử lại
            const tryAgainBtn = errorModal.querySelector('#tryAgainBtn');
            if (tryAgainBtn) {
                tryAgainBtn.addEventListener('click', function() {
                    errorModal.style.display = 'none';
                    
                    // Reset các trường file input
                    if (document.getElementById('multiImagesInput')) {
                        document.getElementById('multiImagesInput').value = '';
                    }
                    
                    // Ẩn kết quả hiện tại nếu có
                    if (document.getElementById('resultsContainer')) {
                        document.getElementById('resultsContainer').style.display = 'none';
                    }
                });
            }
        }
        
        // Cập nhật nội dung modal
        const errorSummary = document.getElementById('errorSummary');
        errorSummary.innerHTML = `
            <strong>${errorMessage}</strong>
            <p>Hệ thống phát hiện ${invalidImages.length} hình ảnh không chứa hoa quả hoặc rau củ.</p>
            <p>Vui lòng kiểm tra các hình ảnh dưới đây và tải lên những hình ảnh chứa hoa quả/rau củ thật.</p>
        `;
        
        // Thêm danh sách ảnh không hợp lệ
        const invalidImagesGrid = document.getElementById('invalidImagesGrid');
        invalidImagesGrid.innerHTML = '';
        
        invalidImages.forEach((image, index) => {
            const imageItem = document.createElement('div');
            imageItem.className = 'invalid-image-item';
            
            imageItem.innerHTML = `
                <div class="invalid-image-preview">
                    <img src="${image.image}" alt="Ảnh không hợp lệ ${index + 1}">
                </div>
                <div class="invalid-image-message">
                    ${image.message || 'Không phải hoa quả/rau củ'}
                </div>
            `;
            
            invalidImagesGrid.appendChild(imageItem);
        });
        
        // Hiển thị modal
        errorModal.style.display = 'block';
    }
    
    // Hiển thị ảnh không hợp lệ trong kết quả
    function displayInvalidImages(invalidImages) {
        let invalidImagesContainer = document.getElementById('invalidImagesContainer');
        
        // Tạo container nếu chưa có
        if (!invalidImagesContainer) {
            invalidImagesContainer = document.createElement('div');
            invalidImagesContainer.id = 'invalidImagesContainer';
            invalidImagesContainer.className = 'invalid-images-container';
            
            // Chèn sau kết quả
            resultsContainer.insertAdjacentElement('afterend', invalidImagesContainer);
        } else {
            invalidImagesContainer.innerHTML = ''; // Xóa nội dung cũ
        }
        
        const header = document.createElement('div');
        header.className = 'invalid-images-header';
        header.innerHTML = `
            <h4><i class="fas fa-exclamation-triangle"></i> Ảnh không đạt yêu cầu (${invalidImages.length})</h4>
            <p>Những ảnh sau không chứa hoa quả và đã bị bỏ qua trong quá trình nhận diện.</p>
        `;
        
        const imagesGrid = document.createElement('div');
        imagesGrid.className = 'invalid-images-thumbnails';
        
        invalidImages.forEach((item, index) => {
            const thumbnail = document.createElement('div');
            thumbnail.className = 'invalid-image-thumbnail';
            
            thumbnail.innerHTML = `
                <div class="thumbnail-preview">
                    <img src="${item.image}" alt="Ảnh không hợp lệ ${index + 1}">
                    <div class="invalid-badge">Không hợp lệ</div>
                </div>
                <div class="thumbnail-reason">${item.message || 'Không phải hoa quả'}</div>
            `;
            
            imagesGrid.appendChild(thumbnail);
        });
        
        invalidImagesContainer.appendChild(header);
        invalidImagesContainer.appendChild(imagesGrid);
        
        // Thêm CSS nếu chưa có
        if (!document.getElementById('invalidImagesCSS')) {
            const style = document.createElement('style');
            style.id = 'invalidImagesCSS';
            style.textContent = `
                .invalid-images-container {
                    margin: 30px 0;
                    background: #fff;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
                
                .invalid-images-header {
                    margin-bottom: 15px;
                }
                
                .invalid-images-header h4 {
                    color: #e74c3c;
                    font-size: 18px;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .invalid-images-header p {
                    color: #666;
                    margin: 0;
                }
                
                .invalid-images-thumbnails {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                    gap: 15px;
                }
                
                .invalid-image-thumbnail {
                    border-radius: 6px;
                    overflow: hidden;
                    background: #f8f9fa;
                    transition: transform 0.2s;
                }
                
                .invalid-image-thumbnail:hover {
                    transform: translateY(-3px);
                }
                
                .thumbnail-preview {
                    height: 150px;
                    position: relative;
                    overflow: hidden;
                }
                
                .thumbnail-preview img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    filter: grayscale(30%);
                }
                
                .invalid-badge {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: #e74c3c;
                    color: white;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                
                .thumbnail-reason {
                    padding: 10px;
                    font-size: 13px;
                    color: #555;
                    border-top: 1px solid #eee;
                }
                
                @media (max-width: 768px) {
                    .invalid-images-thumbnails {
                        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        invalidImagesContainer.style.display = 'block';
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const userDropdown = document.querySelector('.user-dropdown');

    if (userDropdown) {
        userDropdown.addEventListener('click', function (e) {
            const dropdownMenu = this.querySelector('.dropdown-menu');
            dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
            e.stopPropagation();
        });

        // Đóng dropdown khi click ra ngoài
        document.addEventListener('click', function () {
            const dropdownMenu = userDropdown.querySelector('.dropdown-menu');
            if (dropdownMenu.style.display === 'block') {
                dropdownMenu.style.display = 'none';
            }
        });
    }
});