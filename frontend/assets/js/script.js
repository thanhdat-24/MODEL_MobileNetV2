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
            singleModeBtn.classList.remove('active');
            multiModeBtn.classList.add('active');
            if (multiImageContainer) {
                multiImageContainer.style.display = 'grid';
            }
            if (previewImage) {
                previewImage.style.display = 'none';
            }
            fileInput.setAttribute('multiple', 'multiple');
            dropZone.classList.add('multi-mode');
            
            // Reset UI state for multi mode
            if (dropZone.classList.contains('has-image')) {
                dropZone.classList.remove('has-image');
                uploadedFiles = [];
                if (multiImageContainer) {
                    multiImageContainer.innerHTML = '';
                }
            }
        } else {
            singleModeBtn.classList.add('active');
            multiModeBtn.classList.remove('active');
            if (multiImageContainer) {
                multiImageContainer.style.display = 'none';
            }
            if (previewImage) {
                previewImage.style.display = 'block';
            }
            fileInput.removeAttribute('multiple');
            dropZone.classList.remove('multi-mode');
            
            // Reset UI state for single mode
            if (dropZone.classList.contains('has-image')) {
                dropZone.classList.remove('has-image');
                previewImage.src = '#';
            }
        }
        
        // Cập nhật UI
        recognizeBtn.disabled = true;
        changeImageBtn.style.display = 'none';
        resultsContainer.style.display = 'none';
        updateTipsVisibility();
        
        // Ẩn search results container nếu có
        const searchResultsContainer = document.getElementById('searchResultsContainer');
        if (searchResultsContainer) {
            searchResultsContainer.style.display = 'none';
        }
    }

    // Cập nhật hiển thị mẹo khi thay đổi ảnh
    function updateTipsVisibility() {
        if (dropZone.classList.contains('has-image')) {
            if (recognitionTips) recognitionTips.style.display = 'none';
        } else {
            if (recognitionTips) recognitionTips.style.display = 'block';
        }
    }

    // Initialize change image button state
    changeImageBtn.style.display = 'none';

    // Handle file selection via input
    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
        updateTipsVisibility();
    });

    // Set up the drop zone event listeners
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
        if (!dropZone.classList.contains('has-image')) {
            fileInput.click();
        }
    });

    // Prevent default behaviors
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Add highlight class
    function highlight() {
        dropZone.classList.add('highlight');
    }

    // Remove highlight class
    function unhighlight() {
        dropZone.classList.remove('highlight');
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

                if (data.error) {
                    alert('Lỗi: ' + data.error);
                    console.error('Lỗi:', data.error);
                    return;
                }

                // Clear previous results
                resultsList.innerHTML = '';
                
                // Show upload summary message
                const summaryMessage = document.createElement('div');
                summaryMessage.className = 'upload-summary';
                summaryMessage.innerHTML = `
                    <div class="upload-success-message">
                        <i class="fas fa-check-circle"></i>
                        <span>Đã lưu thành công ${data.total_images} hình ảnh vào lịch sử!</span>
                    </div>
                `;
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

                    if (data.error) {
                        alert('Lỗi: ' + data.error);
                        console.error('Lỗi:', data.error);
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