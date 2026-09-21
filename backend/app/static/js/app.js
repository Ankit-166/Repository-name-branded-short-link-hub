document.addEventListener('DOMContentLoaded', () => {
    
    // UI Helpers
    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast show bg-${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Check Auth State
    const navLinks = document.getElementById('nav-links');
    const isAuth = document.cookie.includes('access_token=');
    
    if (navLinks) {
        if (isAuth) {
            navLinks.innerHTML = `
                <a href="/dashboard">Dashboard</a>
                <a href="#" id="logout-btn">Logout</a>
            `;
            document.getElementById('logout-btn')?.addEventListener('click', async (e) => {
                e.preventDefault();
                await fetch('/api/auth/logout', { method: 'POST' });
                window.location.href = '/login';
            });
        } else {
            navLinks.innerHTML = `
                <a href="/login">Login</a>
                <a href="/signup" class="btn btn-primary">Sign Up</a>
            `;
        }
    }

    // Form Handling - Login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    body: formData
                });
                if (res.ok) {
                    window.location.href = '/dashboard';
                } else {
                    const text = await res.text();
                    try {
                        const data = JSON.parse(text);
                        let errMsg = data.detail || 'Login failed';
                        if (Array.isArray(errMsg)) {
                            errMsg = errMsg.map(e => e.msg).join(", ");
                        } else if (typeof errMsg === 'object') {
                            errMsg = JSON.stringify(errMsg);
                        }
                        showToast(errMsg, 'danger');
                    } catch (e) {
                        showToast(`Server Error: ${text.substring(0, 50)}`, 'danger');
                    }
                }
            } catch (err) {
                showToast(`Error: ${err.message}`, 'danger');
            }
        });
    }

    // Form Handling - Signup
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = Object.fromEntries(new FormData(signupForm));
            try {
                const res = await fetch('/api/auth/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (res.ok) {
                    showToast('Signup successful! Please log in.', 'success');
                    setTimeout(() => window.location.href = '/login', 1500);
                } else {
                    const text = await res.text();
                    try {
                        const errorData = JSON.parse(text);
                        let errMsg = errorData.detail || 'Signup failed';
                        if (Array.isArray(errMsg)) {
                            errMsg = errMsg.map(e => e.msg).join(", ");
                        } else if (typeof errMsg === 'object') {
                            errMsg = JSON.stringify(errMsg);
                        }
                        showToast(errMsg, 'danger');
                    } catch (e) {
                        showToast(`Server Error: ${text.substring(0, 50)}`, 'danger');
                    }
                }
            } catch (err) {
                showToast(`Error: ${err.message}`, 'danger');
            }
        });
    }

    // Dashboard Logic
    if (document.querySelector('.dashboard-container')) {
        
        // Tabs
        const tabs = document.querySelectorAll('.sidebar li');
        const panes = document.querySelectorAll('.tab-pane');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                panes.forEach(p => p.classList.add('hidden'));
                
                tab.classList.add('active');
                document.getElementById(`tab-${tab.dataset.tab}`).classList.remove('hidden');

                if (tab.dataset.tab === 'analytics') loadAnalyticsTab();
                if (tab.dataset.tab === 'bio') loadBioTab();
            });
        });

        // Load Links
        async function loadLinks() {
            try {
                const res = await fetch('/api/links');
                if (res.status === 401) return window.location.href = '/login';
                const links = await res.json();
                
                const tbody = document.getElementById('links-tbody');
                const select = document.getElementById('analytics-link-select');
                
                tbody.innerHTML = '';
                
                // Clear select but keep first option
                select.innerHTML = '<option value="">Choose a link...</option>';

                links.forEach(link => {
                    const shortUrl = link.short_url || `${window.location.origin}/r/${link.short_code}`;
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>
                            <a href="${shortUrl}" target="_blank">${link.short_code}</a>
                            <button class="btn btn-secondary copy-btn" style="padding: 0.2rem 0.5rem; font-size: 0.8rem; margin-left: 0.5rem;" data-url="${shortUrl}">Copy</button>
                        </td>
                        <td style="max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            <a href="${link.destination_url}" target="_blank" title="${link.destination_url}">${link.destination_url}</a>
                        </td>
                        <td>${link.clicks_count}</td>
                        <td>
                            <button class="btn btn-secondary qr-btn" data-id="${link.id}">QR</button>
                            <button class="btn btn-danger delete-btn" data-id="${link.id}">Delete</button>
                        </td>
                    `;
                    tbody.appendChild(tr);

                    const opt = document.createElement('option');
                    opt.value = link.id;
                    opt.textContent = `${link.short_code} - ${link.destination_url.substring(0, 30)}`;
                    select.appendChild(opt);
                });

                // Attach events
                document.querySelectorAll('.copy-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        navigator.clipboard.writeText(e.target.dataset.url);
                        showToast('Copied to clipboard!');
                    });
                });

                document.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        if (confirm('Delete this link?')) {
                            const id = e.target.dataset.id;
                            await fetch(`/api/links/${id}`, { method: 'DELETE' });
                            loadLinks();
                            showToast('Link deleted');
                        }
                    });
                });

                document.querySelectorAll('.qr-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const id = e.target.dataset.id;
                        const modal = document.getElementById('qr-modal');
                        const img = document.getElementById('qr-image');
                        img.src = `/api/links/${id}/qr`;
                        modal.classList.remove('hidden');
                    });
                });

            } catch (err) {
                console.error(err);
            }
        }
        
        loadLinks();

        // Create Link
        const btnNewLink = document.getElementById('btn-new-link');
        const formCreateLink = document.getElementById('form-create-link');
        const btnCancelLink = document.getElementById('btn-cancel-link');
        const newLinkFormContainer = document.getElementById('new-link-form');

        btnNewLink.addEventListener('click', () => {
            newLinkFormContainer.classList.remove('hidden');
        });

        btnCancelLink.addEventListener('click', () => {
            newLinkFormContainer.classList.add('hidden');
            formCreateLink.reset();
        });

        formCreateLink.addEventListener('submit', async (e) => {
            e.preventDefault();
            const dest_url = document.getElementById('dest-url').value;
            const custom_slug = document.getElementById('custom-slug').value;
            
            const payload = { destination_url: dest_url };
            if (custom_slug) payload.custom_slug = custom_slug;

            try {
                const res = await fetch('/api/links', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    showToast('Link created successfully', 'success');
                    newLinkFormContainer.classList.add('hidden');
                    formCreateLink.reset();
                    loadLinks();
                } else {
                    const err = await res.json();
                    showToast(err.detail, 'danger');
                }
            } catch (err) {
                showToast('Error creating link', 'danger');
            }
        });

        // Close Modal
        document.querySelector('.close-modal').addEventListener('click', () => {
            document.getElementById('qr-modal').classList.add('hidden');
        });

        // Analytics Tab
        let clicksChartInstance = null;
        let deviceChartInstance = null;
        
        function loadAnalyticsTab() {
            const select = document.getElementById('analytics-link-select');
            select.addEventListener('change', async (e) => {
                const linkId = e.target.value;
                if (!linkId) {
                    document.getElementById('analytics-results').classList.add('hidden');
                    return;
                }
                
                try {
                    const res = await fetch(`/api/analytics/${linkId}`);
                    const data = await res.json();
                    
                    document.getElementById('analytics-results').classList.remove('hidden');
                    document.getElementById('stat-total').textContent = data.total_clicks;
                    
                    renderCharts(data);
                    
                    const refList = document.getElementById('referrers-list');
                    refList.innerHTML = '';
                    Object.entries(data.top_referrers).forEach(([ref, count]) => {
                        const li = document.createElement('li');
                        li.textContent = `${ref}: ${count} clicks`;
                        li.style.padding = '0.5rem';
                        li.style.borderBottom = '1px solid #e5e7eb';
                        refList.appendChild(li);
                    });
                } catch(err) {
                    showToast('Failed to load analytics', 'danger');
                }
            });
        }
        
        function renderCharts(data) {
            const ctxClicks = document.getElementById('clicksChart').getContext('2d');
            const ctxDevice = document.getElementById('deviceChart').getContext('2d');
            
            if (clicksChartInstance) clicksChartInstance.destroy();
            if (deviceChartInstance) deviceChartInstance.destroy();
            
            clicksChartInstance = new Chart(ctxClicks, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.clicks_by_date),
                    datasets: [{
                        label: 'Clicks per Day',
                        data: Object.values(data.clicks_by_date),
                        backgroundColor: '#4f46e5'
                    }]
                }
            });
            
            deviceChartInstance = new Chart(ctxDevice, {
                type: 'pie',
                data: {
                    labels: Object.keys(data.device_distribution),
                    datasets: [{
                        data: Object.values(data.device_distribution),
                        backgroundColor: ['#4f46e5', '#38bdf8', '#10b981']
                    }]
                }
            });
        }

        // Bio Tab
        let currentAvatarBase64 = null;

        const avatarInput = document.getElementById('bio-avatar-input');
        const btnUploadAvatar = document.getElementById('btn-upload-avatar');
        const avatarPreview = document.getElementById('avatar-preview');

        if (btnUploadAvatar) {
            btnUploadAvatar.addEventListener('click', () => {
                avatarInput.click();
            });
        }

        if (avatarInput) {
            avatarInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (!file) return;

                if (file.size > 2 * 1024 * 1024) {
                    showToast('File size must be less than 2MB', 'danger');
                    avatarInput.value = '';
                    return;
                }
                
                if (!file.type.startsWith('image/')) {
                    showToast('Please upload an image file', 'danger');
                    avatarInput.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = (ev) => {
                    currentAvatarBase64 = ev.target.result;
                    avatarPreview.innerHTML = `<img src="${currentAvatarBase64}" style="width: 100%; height: 100%; object-fit: cover;">`;
                };
                reader.readAsDataURL(file);
            });
        }

        async function loadBioTab() {
            try {
                const res = await fetch('/api/bio/me');
                if (res.ok) {
                    const data = await res.json();
                    document.getElementById('bio-display-name').value = data.display_name || '';
                    document.getElementById('bio-text').value = data.bio || '';
                    document.getElementById('bio-theme').value = data.theme || 'minimal-light';
                    
                    currentAvatarBase64 = data.avatar || null;
                    if (currentAvatarBase64) {
                        avatarPreview.innerHTML = `<img src="${currentAvatarBase64}" style="width: 100%; height: 100%; object-fit: cover;">`;
                    } else {
                        const initial = (data.display_name || data.username || 'U')[0].toUpperCase();
                        avatarPreview.innerHTML = initial;
                    }
                    
                    const viewBtn = document.getElementById('view-public-bio');
                    viewBtn.href = `/bio/${data.username}`;
                    viewBtn.classList.remove('hidden');
                    
                    renderBioLinks(data.links);
                }
            } catch (err) {
                console.log("No bio profile found or error.");
            }
        }
        
        function renderBioLinks(links) {
            const list = document.getElementById('bio-links-list');
            list.innerHTML = '';
            links.forEach(l => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <div>
                        <strong>${l.title}</strong><br>
                        <small>${l.url}</small>
                    </div>
                    <button class="btn btn-danger btn-delete-bio-link" data-id="${l.id}">Delete</button>
                `;
                list.appendChild(li);
            });
            
            document.querySelectorAll('.btn-delete-bio-link').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = e.target.dataset.id;
                    await fetch(`/api/bio/links/${id}`, { method: 'DELETE' });
                    loadBioTab();
                });
            });
        }
        
        document.getElementById('form-bio-profile').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                display_name: document.getElementById('bio-display-name').value,
                bio: document.getElementById('bio-text').value,
                theme: document.getElementById('bio-theme').value,
                avatar: currentAvatarBase64
            };
            try {
                const res = await fetch('/api/bio/me', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    showToast('Profile saved successfully', 'success');
                    loadBioTab();
                }
            } catch (err) {
                showToast('Failed to save profile', 'danger');
            }
        });
        
        document.getElementById('form-bio-link').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                title: document.getElementById('bio-link-title').value,
                url: document.getElementById('bio-link-url').value
            };
            try {
                const res = await fetch('/api/bio/links', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    document.getElementById('form-bio-link').reset();
                    showToast('Link added', 'success');
                    loadBioTab();
                }
            } catch (err) {
                showToast('Failed to add link', 'danger');
            }
        });
    }
});
