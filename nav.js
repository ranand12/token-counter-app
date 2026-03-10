/* Shared sidebar navigation - Gemini Tools */
(function() {
    'use strict';

    var currentPage = location.pathname.split('/').pop() || 'index.html';

    var sections = [
        { title: 'Analyze', links: [
            ['index.html', 'Token Counter', 'Count tokens in text and images'],
            ['models.html', 'Model Explorer', 'Browse available Gemini models'],
        ]},
        { title: 'Vision', links: [
            ['describe.html', 'Image Describer', 'Describe images with AI'],
            ['detect.html', 'Object Detector', 'Detect objects with bounding boxes'],
            ['video.html', 'Video Analyzer', 'Analyze video content'],
        ]},
        { title: 'Text & Data', links: [
            ['prompt.html', 'Playground', 'Chat with system instructions'],
            ['extract.html', 'Extractor', 'Extract structured data'],
            ['embed.html', 'Embeddings', 'Compute text similarity'],
            ['search.html', 'Search', 'Grounded Google Search'],
            ['pdf.html', 'PDF Analyzer', 'Analyze PDF documents'],
            ['url.html', 'URL Context', 'Summarize and analyze web pages'],
            ['files.html', 'File Search', 'Upload and query documents'],
        ]},
        { title: 'AI Tools', links: [
            ['think.html', 'Thinking', 'See model reasoning step by step'],
            ['code.html', 'Code Runner', 'Generate and execute Python code'],
            ['maps.html', 'Maps', 'Location-aware queries with Google Maps'],
            ['research.html', 'Deep Research', 'Multi-step research agent'],
        ]},
        { title: 'Creative', links: [
            ['tts.html', 'Text to Speech', 'Generate speech from text'],
            ['story.html', 'Story Illustrator', 'Generate illustrated storybooks'],
            ['animate.html', 'Animated Video', 'Create story videos with AI'],
        ]},
    ];

    // Find current page info
    var currentPageName = '';
    sections.forEach(function(s) {
        s.links.forEach(function(l) {
            if (l[0] === currentPage) currentPageName = l[1];
        });
    });

    // --- Build Topbar ---
    var topbar = document.createElement('div');
    topbar.className = 'gt-topbar';

    var hamburger = document.createElement('button');
    hamburger.className = 'gt-hamburger';
    hamburger.setAttribute('aria-label', 'Open navigation');
    for (var i = 0; i < 3; i++) {
        var bar = document.createElement('span');
        bar.className = 'gt-hamburger-bar';
        hamburger.appendChild(bar);
    }
    topbar.appendChild(hamburger);

    var brand = document.createElement('span');
    brand.className = 'gt-topbar-brand';
    brand.textContent = 'Gemini Tools';
    topbar.appendChild(brand);

    if (currentPageName) {
        var pageName = document.createElement('span');
        pageName.className = 'gt-topbar-page';
        pageName.textContent = currentPageName;
        topbar.appendChild(pageName);
    }

    // Theme toggle button
    var themeBtn = document.createElement('button');
    themeBtn.className = 'gt-theme-toggle';
    themeBtn.setAttribute('title', 'Toggle theme');

    var svgNS = 'http://www.w3.org/2000/svg';

    // Moon icon
    var moonSvg = document.createElementNS(svgNS, 'svg');
    moonSvg.setAttribute('class', 'gt-icon-moon');
    moonSvg.setAttribute('viewBox', '0 0 24 24');
    moonSvg.setAttribute('fill', 'none');
    moonSvg.setAttribute('stroke', 'currentColor');
    moonSvg.setAttribute('stroke-width', '2');
    moonSvg.setAttribute('stroke-linecap', 'round');
    moonSvg.setAttribute('stroke-linejoin', 'round');
    var moonPath = document.createElementNS(svgNS, 'path');
    moonPath.setAttribute('d', 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z');
    moonSvg.appendChild(moonPath);
    themeBtn.appendChild(moonSvg);

    // Sun icon
    var sunSvg = document.createElementNS(svgNS, 'svg');
    sunSvg.setAttribute('class', 'gt-icon-sun');
    sunSvg.setAttribute('viewBox', '0 0 24 24');
    sunSvg.setAttribute('fill', 'none');
    sunSvg.setAttribute('stroke', 'currentColor');
    sunSvg.setAttribute('stroke-width', '2');
    sunSvg.setAttribute('stroke-linecap', 'round');
    sunSvg.setAttribute('stroke-linejoin', 'round');
    var sunParts = [
        ['circle', {cx: '12', cy: '12', r: '5'}],
        ['line', {x1: '12', y1: '1', x2: '12', y2: '3'}],
        ['line', {x1: '12', y1: '21', x2: '12', y2: '23'}],
        ['line', {x1: '4.22', y1: '4.22', x2: '5.64', y2: '5.64'}],
        ['line', {x1: '18.36', y1: '18.36', x2: '19.78', y2: '19.78'}],
        ['line', {x1: '1', y1: '12', x2: '3', y2: '12'}],
        ['line', {x1: '21', y1: '12', x2: '23', y2: '12'}],
        ['line', {x1: '4.22', y1: '19.78', x2: '5.64', y2: '18.36'}],
        ['line', {x1: '18.36', y1: '5.64', x2: '19.78', y2: '4.22'}],
    ];
    sunParts.forEach(function(part) {
        var el = document.createElementNS(svgNS, part[0]);
        var attrs = part[1];
        for (var key in attrs) {
            el.setAttribute(key, attrs[key]);
        }
        sunSvg.appendChild(el);
    });
    themeBtn.appendChild(sunSvg);

    themeBtn.addEventListener('click', function() {
        var current = document.documentElement.getAttribute('data-theme');
        var next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    });

    topbar.appendChild(themeBtn);

    // --- Build Overlay ---
    var overlay = document.createElement('div');
    overlay.className = 'gt-overlay';

    // --- Build Sidebar ---
    var sidebar = document.createElement('aside');
    sidebar.className = 'gt-sidebar';

    // Sidebar header
    var sidebarHeader = document.createElement('div');
    sidebarHeader.className = 'gt-sidebar-header';

    var sidebarBrand = document.createElement('span');
    sidebarBrand.className = 'gt-sidebar-brand';
    sidebarBrand.textContent = 'Gemini Tools';
    sidebarHeader.appendChild(sidebarBrand);

    var closeBtn = document.createElement('button');
    closeBtn.className = 'gt-sidebar-close';
    closeBtn.setAttribute('aria-label', 'Close navigation');
    closeBtn.textContent = '\u00D7';
    sidebarHeader.appendChild(closeBtn);

    sidebar.appendChild(sidebarHeader);

    // Sidebar content
    var content = document.createElement('div');
    content.className = 'gt-sidebar-content';

    sections.forEach(function(section) {
        var sectionEl = document.createElement('div');
        sectionEl.className = 'gt-sidebar-section';

        var title = document.createElement('div');
        title.className = 'gt-sidebar-section-title';
        title.textContent = section.title;
        sectionEl.appendChild(title);

        section.links.forEach(function(link) {
            var a = document.createElement('a');
            a.className = 'gt-sidebar-link';
            a.href = link[0];
            if (link[0] === currentPage) a.classList.add('active');

            var name = document.createTextNode(link[1]);
            a.appendChild(name);

            if (link[2]) {
                var desc = document.createElement('span');
                desc.className = 'gt-sidebar-desc';
                desc.textContent = link[2];
                a.appendChild(desc);
            }

            // Close sidebar on link click (same-page navigation)
            a.addEventListener('click', function() {
                closeSidebar();
            });

            sectionEl.appendChild(a);
        });

        content.appendChild(sectionEl);
    });

    sidebar.appendChild(content);

    // --- Open / Close logic ---
    function openSidebar() {
        sidebar.classList.add('open');
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
        document.body.style.overflow = '';
    }

    hamburger.addEventListener('click', openSidebar);
    closeBtn.addEventListener('click', closeSidebar);
    overlay.addEventListener('click', closeSidebar);

    // Close on Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeSidebar();
    });

    // --- Theme initialization ---
    function getPreferredTheme() {
        var stored = localStorage.getItem('theme');
        if (stored) return stored;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    // Apply theme (may have already been applied by inline script, but this ensures consistency)
    document.documentElement.setAttribute('data-theme', getPreferredTheme());

    // --- Insert into DOM ---
    document.body.insertBefore(topbar, document.body.firstChild);
    document.body.insertBefore(overlay, document.body.firstChild);
    document.body.insertBefore(sidebar, document.body.firstChild);

    // Expose toggleTheme globally for any remaining inline onclick handlers
    window.toggleTheme = function() {
        var current = document.documentElement.getAttribute('data-theme');
        var next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    };
})();
