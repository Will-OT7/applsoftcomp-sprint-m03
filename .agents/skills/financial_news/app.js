/**
 * Financial News Dashboard - Frontend Application
 * Handles news display, configuration, feedback, and charts.
 */

// State
let config = {
    industries: [],
    events: []
};

let feedback = {};

let allNews = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    loadFeedback();
    loadNewsData();
    
    // Show config on first visit
    if (!config.industries.length && !config.events.length) {
        openConfig();
    }
});

/**
 * Load configuration from localStorage
 */
function loadConfig() {
    const saved = localStorage.getItem('financial_news_config');
    if (saved) {
        config = JSON.parse(saved);
        syncConfigUI();
    }
}

/**
 * Save configuration to localStorage
 */
function saveConfig() {
    const industryCheckboxes = document.querySelectorAll('input[name="industry"]:checked');
    const eventCheckboxes = document.querySelectorAll('input[name="event"]:checked');
    
    const selectedIndustries = Array.from(industryCheckboxes).map(cb => cb.value);
    const selectedEvents = Array.from(eventCheckboxes).map(cb => cb.value);
    
    // Require at least 1 selection
    if (!selectedIndustries.length && !selectedEvents.length) {
        alert('Please select at least one industry or event type.');
        return;
    }
    
    config.industries = selectedIndustries;
    config.events = selectedEvents;
    
    localStorage.setItem('financial_news_config', JSON.stringify(config));
    
    closeConfig();
    filterAndRenderNews();
}

/**
 * Sync config UI with current state
 */
function syncConfigUI() {
    document.querySelectorAll('input[name="industry"]').forEach(cb => {
        cb.checked = config.industries.includes(cb.value);
    });
    
    document.querySelectorAll('input[name="event"]').forEach(cb => {
        cb.checked = config.events.includes(cb.value);
    });
}

/**
 * Load feedback from localStorage
 */
function loadFeedback() {
    const saved = localStorage.getItem('financial_news_feedback');
    if (saved) {
        feedback = JSON.parse(saved);
    }
}

/**
 * Save feedback to localStorage
 */
function saveFeedback() {
    localStorage.setItem('financial_news_feedback', JSON.stringify(feedback));
}

/**
 * Clear feedback history
 */
function clearFeedback() {
    if (confirm('Clear all feedback history?')) {
        feedback = {};
        saveFeedback();
        renderNews();
    }
}

/**
 * Load news data from JSON files
 */
async function loadNewsData() {
    try {
        // Load all 7 days of data
        const dates = getLast7Days();
        const promises = dates.map(date => fetch(`data/${date}.json`).then(r => r.json()).catch(() => []));
        
        const results = await Promise.all(promises);
        allNews = results.flat();
        
        // Sort by date (newest first)
        allNews.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        filterAndRenderNews();
        renderCharts();
    } catch (error) {
        console.error('Error loading news:', error);
        document.getElementById('news-container').innerHTML = 
            '<div class="error-message">Error loading news data. Please ensure the data files exist.</div>';
    }
}

/**
 * Get last 7 days as date strings
 */
function getLast7Days() {
    const dates = [];
    for (let i = 0; i < 7; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dates.push(date.toISOString().split('T')[0]);
    }
    return dates;
}

/**
 * Filter news based on config and render
 */
function filterAndRenderNews() {
    let filtered = allNews;
    
    // Filter by industries
    if (config.industries.length) {
        filtered = filtered.filter(item => config.industries.includes(item.industry));
    }
    
    // Filter by event types
    if (config.events.length) {
        filtered = filtered.filter(item => config.events.includes(item.event_type));
    }
    
    // Apply feedback-based ranking
    filtered = applyFeedbackRanking(filtered);
    
    renderNews(filtered);
}

/**
 * Apply feedback-based ranking
 */
function applyFeedbackRanking(news) {
    // Calculate feedback scores by industry and event type
    const scores = {};
    
    for (const [id, data] of Object.entries(feedback)) {
        const article = allNews.find(n => n.title === id);
        if (!article) continue;
        
        const industry = article.industry;
        const eventType = article.event_type;
        
        if (!scores[industry]) scores[industry] = 0;
        if (!scores[eventType]) scores[eventType] = 0;
        
        if (data.type === 'up') {
            scores[industry] += 1;
            scores[eventType] += 1;
        } else {
            scores[industry] -= 1;
            scores[eventType] -= 1;
        }
    }
    
    // Sort news by score
    return news.sort((a, b) => {
        const scoreA = (scores[a.industry] || 0) + (scores[a.event_type] || 0);
        const scoreB = (scores[b.industry] || 0) + (scores[b.event_type] || 0);
        return scoreB - scoreA;
    });
}

/**
 * Render news items
 */
function renderNews(filteredNews = null) {
    const container = document.getElementById('news-container');
    const news = filteredNews || allNews;
    
    if (!news.length) {
        container.innerHTML = '<div class="no-data">No news articles match your current filters.</div>';
        return;
    }
    
    // Calculate items per industry based on selection count
    const industryCount = config.industries.length || 7;
    const itemsPerIndustry = Math.ceil(news.length / industryCount);
    
    // Group by industry
    const byIndustry = {};
    for (const item of news) {
        if (!byIndustry[item.industry]) byIndustry[item.industry] = [];
        byIndustry[item.industry].push(item);
    }
    
    let html = '';
    for (const [industry, items] of Object.entries(byIndustry)) {
        // Limit items per industry
        const displayItems = items.slice(0, itemsPerIndustry);
        
        html += `<h3 style="margin: 20px 0 10px; color: #4a4a6a;">${industry}</h3>`;
        
        for (const item of displayItems) {
            const feedbackState = feedback[item.title] || { type: null };
            
            html += `
                <div class="news-item" data-id="${item.title}">
                    <div class="news-item-title">
                        <a href="${item.url}" target="_blank" rel="noopener">
                            ${item.title} (${item.industry})
                        </a>
                    </div>
                    <div class="news-item-summary">${item.summary}</div>
                    <div class="news-item-meta">
                        <span class="news-item-source">${item.source} • ${formatDate(item.date)}</span>
                        <span class="news-item-sentiment sentiment-${item.sentiment}">${item.sentiment}</span>
                        <div class="feedback-buttons">
                            <button class="feedback-btn ${feedbackState.type === 'up' ? 'active' : ''}" 
                                    onclick="toggleFeedback('${item.title}', 'up')">👍</button>
                            <button class="feedback-btn ${feedbackState.type === 'down' ? 'active' : ''}" 
                                    onclick="toggleFeedback('${item.title}', 'down')">👎</button>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    container.innerHTML = html;
}

/**
 * Toggle feedback for an article
 */
function toggleFeedback(articleId, type) {
    if (feedback[articleId]?.type === type) {
        // Remove feedback if clicking same button
        delete feedback[articleId];
    } else {
        feedback[articleId] = { type, timestamp: Date.now() };
    }
    
    saveFeedback();
    filterAndRenderNews();
}

/**
 * Format date string
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Render charts using Chart.js
 */
async function renderCharts() {
    try {
        const response = await fetch('data/aggregates.json');
        const aggregates = await response.json().catch(() => ({ by_industry: {}, sentiment_trends: {}, by_date: {} }));
        
        renderSentimentChart(aggregates);
        renderVolumeChart(aggregates);
    } catch (error) {
        console.error('Error loading aggregates:', error);
    }
}

/**
 * Render sentiment trends chart
 */
function renderSentimentChart(aggregates) {
    const ctx = document.getElementById('sentiment-chart').getContext('2d');
    
    const industries = Object.keys(aggregates.sentiment_trends || {});
    const dates = getLast7Days().reverse();
    
    // For now, show current sentiment distribution
    const positiveData = industries.map(ind => aggregates.sentiment_trends[ind]?.positive || 0);
    const negativeData = industries.map(ind => aggregates.sentiment_trends[ind]?.negative || 0);
    const neutralData = industries.map(ind => aggregates.sentiment_trends[ind]?.neutral || 0);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: industries,
            datasets: [
                {
                    label: 'Positive',
                    data: positiveData,
                    backgroundColor: 'rgba(76, 175, 80, 0.7)'
                },
                {
                    label: 'Negative',
                    data: negativeData,
                    backgroundColor: 'rgba(244, 67, 54, 0.7)'
                },
                {
                    label: 'Neutral',
                    data: neutralData,
                    backgroundColor: 'rgba(158, 158, 158, 0.7)'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: { stacked: true },
                y: { stacked: true, beginAtZero: true }
            }
        }
    });
}

/**
 * Render news volume chart
 */
function renderVolumeChart(aggregates) {
    const ctx = document.getElementById('volume-chart').getContext('2d');
    
    const industries = Object.keys(aggregates.by_industry || {});
    const volumeData = industries.map(ind => aggregates.by_industry[ind] || 0);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: industries,
            datasets: [{
                label: 'News Volume',
                data: volumeData,
                backgroundColor: 'rgba(33, 150, 243, 0.7)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

/**
 * Open configuration modal
 */
function openConfig() {
    document.getElementById('config-modal').classList.add('active');
}

/**
 * Close configuration modal
 */
function closeConfig() {
    document.getElementById('config-modal').classList.remove('active');
}
