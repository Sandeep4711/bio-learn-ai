# 🎨 Design System Component Reference

## Quick Copy-Paste Components

### Buttons

```html
<!-- Primary Button -->
<button class="btn btn-primary">Get Started</button>

<!-- Primary Button with Icon -->
<button class="btn btn-primary">
    Continue
    <span>→</span>
</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">Learn More</button>

<!-- Outline Button -->
<button class="btn btn-outline">View Details</button>

<!-- Ghost Button -->
<button class="btn btn-ghost">Cancel</button>

<!-- Large Button -->
<a href="#" class="btn btn-primary btn-lg">Start Learning Now</a>

<!-- Small Button -->
<button class="btn btn-primary btn-sm">Apply</button>

<!-- Loading Button -->
<button class="btn btn-primary btn-loading" disabled>
    <span style="visibility: hidden;">Loading...</span>
</button>
```

---

### Cards

```html
<!-- Basic Card -->
<div class="card">
    <h3 style="margin-bottom: 12px;">Card Title</h3>
    <p style="color: var(--text-secondary);">Card content goes here</p>
</div>

<!-- Elevated Card -->
<div class="card card-elevated" style="padding: 32px;">
    <h3>Elevated Card</h3>
    <p>More prominent with shadow</p>
</div>

<!-- Clickable Card -->
<a href="/page" class="card card-clickable" style="text-decoration: none;">
    <div style="font-size: 32px; margin-bottom: 12px;">📊</div>
    <h4 style="margin-bottom: 8px;">Dashboard</h4>
    <p class="text-small" style="color: var(--text-secondary);">
        View your analytics
    </p>
</a>

<!-- Stat Card -->
<div class="stat-card">
    <div class="stat-label">Total Users</div>
    <div class="stat-value">10,542</div>
    <div class="stat-change positive">+12% this week</div>
</div>
```

---

### Form Inputs

```html
<!-- Text Input -->
<div class="form-group">
    <label class="form-label">Email Address</label>
    <input
        type="email"
        class="input"
        placeholder="your@email.com"
        required
    >
</div>

<!-- Password Input -->
<div class="form-group">
    <label class="form-label">Password</label>
    <input
        type="password"
        class="input"
        placeholder="Enter password"
        required
    >
</div>

<!-- Input with Error State -->
<div class="form-group">
    <label class="form-label">Username</label>
    <input
        type="text"
        class="input input-error"
        placeholder="Username"
    >
    <div class="field-error">Username is already taken</div>
</div>

<!-- Select Dropdown -->
<select class="input">
    <option>Option 1</option>
    <option>Option 2</option>
    <option>Option 3</option>
</select>
```

---

### Navigation

```html
<!-- Navbar -->
<nav class="navbar">
    <div class="navbar-container">
        <a href="/" class="navbar-brand">
            <span style="font-size: 24px;">🧬</span>
            <span>BioLearn AI</span>
        </a>
        <div class="navbar-nav">
            <a href="#features" class="navbar-link">Features</a>
            <a href="#pricing" class="navbar-link">Pricing</a>
            <a href="/login" class="btn btn-ghost btn-sm">Login</a>
            <a href="/signup" class="btn btn-primary btn-sm">Sign Up</a>
        </div>
    </div>
</nav>

<!-- Sidebar -->
<div class="sidebar">
    <a href="/" class="sidebar-brand">
        <span style="font-size: 28px;">🧬</span>
        <span>BioLearn AI</span>
    </a>

    <nav class="sidebar-nav">
        <a href="/dashboard" class="sidebar-link active">
            <span class="sidebar-icon">📊</span>
            <span>Dashboard</span>
        </a>
        <a href="/lessons" class="sidebar-link">
            <span class="sidebar-icon">📚</span>
            <span>Lessons</span>
        </a>
        <a href="/quizzes" class="sidebar-link">
            <span class="sidebar-icon">✅</span>
            <span>Quizzes</span>
        </a>
    </nav>
</div>
```

---

### Loading States

```html
<!-- Skeleton Loader -->
<div class="card skeleton" style="height: 100px;"></div>

<!-- Spinner -->
<div class="spinner"></div>

<!-- Loading Grid -->
<div class="stats-grid">
    <div class="stat-card skeleton" style="height: 140px;"></div>
    <div class="stat-card skeleton" style="height: 140px;"></div>
    <div class="stat-card skeleton" style="height: 140px;"></div>
</div>
```

---

### Layouts

```html
<!-- Container -->
<div class="container">
    <!-- Content with max-width: 1280px -->
</div>

<!-- Dashboard Layout -->
<div class="sidebar">
    <!-- Sidebar content -->
</div>
<div class="dashboard-container">
    <!-- Main content -->
</div>

<!-- Stats Grid (Auto-fit 3 columns) -->
<div class="stats-grid">
    <div class="stat-card">Card 1</div>
    <div class="stat-card">Card 2</div>
    <div class="stat-card">Card 3</div>
</div>

<!-- Two Column Layout -->
<div style="display: grid; grid-template-columns: 2fr 1fr; gap: 32px;">
    <div>Main content (2/3 width)</div>
    <div>Sidebar content (1/3 width)</div>
</div>
```

---

### Badges & Tags

```html
<!-- Status Badge -->
<span style="display: inline-block; padding: 4px 12px; background: rgba(99, 102, 241, 0.1); color: var(--primary); border-radius: 100px; font-size: 12px; font-weight: 600;">
    Active
</span>

<!-- Success Badge -->
<span style="display: inline-block; padding: 4px 12px; background: rgba(16, 185, 129, 0.1); color: var(--success); border-radius: 100px; font-size: 12px; font-weight: 600;">
    Completed
</span>

<!-- Warning Badge -->
<span style="display: inline-block; padding: 4px 12px; background: rgba(245, 158, 11, 0.1); color: var(--warning); border-radius: 100px; font-size: 12px; font-weight: 600;">
    Pending
</span>

<!-- Error Badge -->
<span style="display: inline-block; padding: 4px 12px; background: rgba(239, 68, 68, 0.1); color: var(--error); border-radius: 100px; font-size: 12px; font-weight: 600;">
    Failed
</span>
```

---

### Alerts & Messages

```html
<!-- Success Message -->
<div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: var(--success); padding: 16px; border-radius: 10px; font-size: 14px;">
    ✓ Your changes have been saved successfully
</div>

<!-- Error Message -->
<div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); color: var(--error); padding: 16px; border-radius: 10px; font-size: 14px;">
    ✕ Something went wrong. Please try again.
</div>

<!-- Info Message -->
<div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); color: var(--primary); padding: 16px; border-radius: 10px; font-size: 14px;">
    ℹ️ Your trial expires in 7 days
</div>
```

---

### Feature Cards (Home Page)

```html
<div class="card feature-card">
    <div style="font-size: 48px; margin-bottom: 24px;">⚡</div>
    <h3 style="margin-bottom: 12px; font-size: 20px;">Feature Title</h3>
    <p style="color: var(--text-secondary); line-height: 1.6;">
        Feature description explaining the benefit
    </p>
</div>
```

---

### Hero Section

```html
<section style="min-height: 90vh; display: flex; align-items: center; position: relative;">
    <div class="hero-gradient" style="position: absolute; inset: 0; pointer-events: none;"></div>

    <div class="container" style="position: relative; z-index: 1;">
        <div style="max-width: 800px; margin: 0 auto; text-align: center;">
            <h1 style="font-size: 56px; font-weight: 800; line-height: 1.1; margin-bottom: 24px;">
                Your Headline Here
            </h1>

            <p style="font-size: 20px; color: var(--text-secondary); margin-bottom: 48px;">
                Your compelling subheadline that explains the value
            </p>

            <div style="display: flex; gap: 16px; justify-content: center;">
                <a href="/signup" class="btn btn-primary btn-lg">
                    Get Started Free
                    <span>→</span>
                </a>
                <a href="#learn-more" class="btn btn-secondary btn-lg">
                    Learn More
                </a>
            </div>
        </div>
    </div>
</section>
```

---

### Empty States

```html
<div class="card" style="text-align: center; padding: 64px 32px;">
    <div style="font-size: 64px; margin-bottom: 24px; opacity: 0.5;">📭</div>
    <h3 style="margin-bottom: 12px;">No items yet</h3>
    <p style="color: var(--text-secondary); margin-bottom: 32px;">
        Get started by creating your first item
    </p>
    <a href="/create" class="btn btn-primary">Create Item</a>
</div>
```

---

## JavaScript Utilities

```javascript
// Show toast notification
Toast.show('Profile updated successfully!', 'success');
Toast.show('An error occurred', 'error');
Toast.show('Please wait...', 'info');

// Button loading state
const loading = new LoadingState(button, { loadingText: 'Saving...' });
loading.start();
// ... do async work
loading.stop();

// API call with error handling
const data = await API.get('/api/dashboard-stats');
const result = await API.post('/api/save', { name: 'value' });

// Form validation
if (!FormValidator.validateEmail(email)) {
    FormValidator.showError(emailInput, 'Please enter a valid email');
} else {
    FormValidator.clearError(emailInput);
}

// Format numbers
formatNumber(1234567); // "1,234,567"
formatDuration(125); // "2h 5m"
relativeTime('2024-03-20T10:00:00'); // "2 hours ago"
```

---

## CSS Variables Reference

```css
/* Colors */
--primary: #6366F1
--accent: #22D3EE
--bg-primary: #0B1220
--bg-surface: #111827
--bg-elevated: #1F2937
--border-primary: #1F2937
--text-primary: #E5E7EB
--text-secondary: #9CA3AF
--success: #10B981
--warning: #F59E0B
--error: #EF4444

/* Spacing */
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-6: 24px
--space-8: 32px
--space-12: 48px
--space-16: 64px

/* Typography */
--text-xs: 12px
--text-sm: 14px
--text-base: 16px
--text-xl: 20px
--text-2xl: 24px
--text-3xl: 28px
--text-4xl: 32px
--text-5xl: 40px

/* Border Radius */
--radius-sm: 6px
--radius-md: 10px
--radius-lg: 12px
--radius-xl: 16px
```

---

## Animation Classes

```html
<!-- Fade In -->
<div class="fade-in">Content fades in on load</div>

<!-- Slide In -->
<div class="slide-in">Content slides in from left</div>

<!-- Skeleton Loading -->
<div class="skeleton" style="width: 200px; height: 40px;"></div>
```

---

## Responsive Patterns

```css
/* Mobile-first approach */
.container {
    padding: 0 16px;
}

@media (min-width: 768px) {
    .container {
        padding: 0 24px;
    }
}

/* Hide sidebar on mobile */
@media (max-width: 768px) {
    .sidebar {
        display: none;
    }
    .dashboard-container {
        margin-left: 0;
    }
}
```

---

**Pro Tip:** Keep components consistent by reusing these patterns throughout your application. Avoid creating one-off designs that break the system.
