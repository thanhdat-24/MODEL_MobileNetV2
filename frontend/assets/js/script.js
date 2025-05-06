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
    const previewImage = document.getElementById('previewImage');
    const recognizeBtn = document.getElementById('recognizeBtn');
    const changeImageBtn = document.getElementById('changeImageBtn');
    const loadingContainer = document.getElementById('loadingContainer');
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsList = document.getElementById('resultsList');
    const shareResultsBtn = document.getElementById('shareResultsBtn');
    const downloadResultsBtn = document.getElementById('downloadResultsBtn');
    const recognitionTips = document.getElementById('recognitionTips');

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

    // Change image button click
    changeImageBtn.addEventListener('click', function () {
        dropZone.classList.remove('has-image');
        previewImage.src = '#';
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

        // Create form data
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

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
    });

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

    // Kiểm tra hiển thị mẹo ban đầu
    updateTipsVisibility();
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