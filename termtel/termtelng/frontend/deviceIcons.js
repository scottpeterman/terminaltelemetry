// deviceIcons.js
// Make DeviceIcons available globally for browser usage
window.DeviceIcons = class DeviceIcons {
    static getRouterSVG() {
        return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 60 41">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="0.3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <g fill="none" stroke="#22D3EE" stroke-width="0.8" filter="url(#glow)">
    <!-- Base cylinder outlines -->
    <path d="M29.137 22.837c16.144 0 29.137-5.119 29.137-11.419S45.281 0 29.137 0 0 5.119 0 11.419s12.994 11.419 29.137 11.419z" opacity="0.4"/>
    <path d="M58.274 11.419c0 6.3-12.994 11.419-29.137 11.419S0 17.719 0 11.419v16.537c0 6.3 12.994 11.419 29.137 11.419s29.137-5.119 29.137-11.419z" opacity="0.4"/>

    <!-- Grid lines -->
    <path d="M14.5 11.419 h43.774" opacity="0.2"/>
    <path d="M29.137 5.419 v16.418" opacity="0.2"/>
    <path d="M43.774 11.419 h-43.774" opacity="0.2"/>

    <!-- Network connections -->
    <path d="M22.448 7.081l2.363 3.544-9.056 1.969 1.969-1.575L3.942 8.656 7.486 5.9l13.388 2.362 1.575-1.181z" stroke-width="1"/>
    <path d="M35.442 15.743L33.473 12.2l8.269-1.969-1.181 1.575 13.388 2.362-3.15 2.363-13.781-2.363-1.575 1.575z" stroke-width="1"/>
    <path d="M30.717 5.113l9.056-2.362.394 3.544-2.363-.394-4.331 3.938-4.331-.787 4.331-3.544-2.756-.394z" stroke-width="1"/>
    <path d="M26.78 19.288l-8.662 1.575-.394-4.331 2.756.787 4.725-4.331 4.331.787-5.119 4.725 2.362.788z" stroke-width="1"/>

    <!-- Corner brackets -->
    <path d="M2 2 h6 M2 2 v6" stroke-width="1"/>
    <path d="M58 2 h-6 M58 2 v6" stroke-width="1"/>
    <path d="M2 39 h6 M2 39 v-6" stroke-width="1"/>
    <path d="M58 39 h-6 M58 39 v-6" stroke-width="1"/>
  </g>
</svg>`;
    }

    static getSwitchSVG() {
        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 41">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="0.3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <g fill="none" stroke="#22D3EE" stroke-width="0.8" filter="url(#glow)">
    <!-- Main switch body -->
    <path d="M15,10 h40 l-10,18 h-40 l10,-18z" opacity="0.4"/>
    <path d="M5,28 h40 v8 h-40z" opacity="0.4"/>
    <path d="M45,28 l10,-18 v8 l-10,18z" opacity="0.4"/>

    <!-- Network arrows -->
    <g stroke-width="1">
      <line x1="22" y1="15" x2="30" y2="15"/>
      <polygon points="23,18 17,15 23,12"/>

      <line x1="15" y1="23" x2="23" y2="23"/>
      <polygon points="16,26 10,23 16,20"/>

      <line x1="38" y1="22" x2="30" y2="22"/>
      <polygon points="37,19 43,22 37,25"/>

      <line x1="47" y1="14" x2="39" y2="14"/>
      <polygon points="46,11 52,14 46,17"/>
    </g>

    <!-- Corner brackets -->
    <path d="M2 2 h6 M2 2 v6" stroke-width="1"/>
    <path d="M58 2 h-6 M58 2 v6" stroke-width="1"/>
    <path d="M2 39 h6 M2 39 v-6" stroke-width="1"/>
    <path d="M58 39 h-6 M58 39 v-6" stroke-width="1"/>
  </g>
</svg>`;
    }

    static getLinuxSVG() {
        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 100">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="0.3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <g fill="none" stroke="#22D3EE" stroke-width="0.8" filter="url(#glow)" transform="translate(155, 5) rotate(90)">
    <!-- Main server chassis -->
    <rect x="20" y="10" width="60" height="140" opacity="0.4"/>

    <!-- Server sections/units -->
    <rect x="22" y="15" width="56" height="25" opacity="0.4"/>
    <rect x="22" y="45" width="56" height="25" opacity="0.4"/>
    <rect x="22" y="75" width="56" height="25" opacity="0.4"/>
    <rect x="22" y="105" width="56" height="25" opacity="0.4"/>

    <!-- Front panel details -->
    <circle cx="35" cy="27.5" r="5" opacity="0.6"/>
    <circle cx="35" cy="57.5" r="5" opacity="0.6"/>
    <circle cx="35" cy="87.5" r="5" opacity="0.6"/>
    <circle cx="35" cy="117.5" r="5" opacity="0.6"/>

    <!-- Drive bays -->
    <rect x="45" y="20" width="28" height="4" opacity="0.4"/>
    <rect x="45" y="26" width="28" height="4" opacity="0.4"/>
    <rect x="45" y="50" width="28" height="4" opacity="0.4"/>
    <rect x="45" y="56" width="28" height="4" opacity="0.4"/>
    <rect x="45" y="80" width="28" height="4" opacity="0.4"/>
    <rect x="45" y="86" width="28" height="4" opacity="0.4"/>
    <rect x="45" y="110" width="28" height="4" opacity="0.4"/>
    <rect x="45" y="116" width="28" height="4" opacity="0.4"/>

    <!-- Network activity indicators -->
    <path d="M75 25 h8" opacity="0.8" stroke-width="1"/>
    <path d="M75 55 h8" opacity="0.8" stroke-width="1"/>
    <path d="M75 85 h8" opacity="0.8" stroke-width="1"/>
    <path d="M75 115 h8" opacity="0.8" stroke-width="1"/>

    <!-- Corner brackets -->
    <path d="M15 5 h10 M15 5 v10" stroke-width="1"/>
    <path d="M85 5 h-10 M85 5 v10" stroke-width="1"/>
    <path d="M15 155 h10 M15 155 v-10" stroke-width="1"/>
    <path d="M85 155 h-10 M85 155 v-10" stroke-width="1"/>
  </g>
</svg>`;
    }

    static getDiscoveringSVG() {
        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500">
    <defs>
        <filter id="subtleGlow">
            <feGaussianBlur stdDeviation="0.3" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>

        <linearGradient id="sweepGradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" style="stop-color:#22D3EE;stop-opacity:0.4"/>
            <stop offset="100%" style="stop-color:#22D3EE;stop-opacity:0"/>
        </linearGradient>
    </defs>

    <g fill="none" stroke="#22D3EE" stroke-width="0.8" filter="url(#subtleGlow)">
        <!-- Main circle -->
        <circle cx="250" cy="250" r="200" opacity="0.4"/>

        <!-- Grid lines -->
        <line x1="250" y1="50" x2="250" y2="450" opacity="0.4"/>
        <line x1="50" y1="250" x2="450" y2="250" opacity="0.4"/>
        <line x1="100" y1="100" x2="400" y2="400" opacity="0.4"/>
        <line x1="100" y1="400" x2="400" y2="100" opacity="0.4"/>

        <!-- Concentric circles -->
        <circle cx="250" cy="250" r="50" opacity="0.4"/>
        <circle cx="250" cy="250" r="100" opacity="0.4"/>
        <circle cx="250" cy="250" r="150" opacity="0.4"/>

        <!-- Radar sweep -->
        <g>
            <path d="M250,250 L250,50 A30,30 0 0 1 290,65 Z" fill="url(#sweepGradient)" opacity="0.6">
                <animateTransform
                    attributeName="transform"
                    type="rotate"
                    from="0 250 250"
                    to="360 250 250"
                    dur="4s"
                    repeatCount="indefinite"/>
            </path>
            <line x1="250" y1="250" x2="250" y2="50" opacity="0.6">
                <animateTransform
                    attributeName="transform"
                    type="rotate"
                    from="0 250 250"
                    to="360 250 250"
                    dur="4s"
                    repeatCount="indefinite"/>
            </line>
        </g>

        <!-- Corner brackets -->
        <path d="M50 50 h30 M50 50 v30" stroke-width="1"/>
        <path d="M450 50 h-30 M450 50 v30" stroke-width="1"/>
        <path d="M50 450 h30 M50 450 v-30" stroke-width="1"/>
        <path d="M450 450 h-30 M450 450 v-30" stroke-width="1"/>
    </g>
</svg>`;
    }
    static getRadarSVG() {
        return `<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <!-- Basic glow effect -->
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>

        <!-- Radial gradient for the sweep sector -->
        <linearGradient id="sweepGradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" style="stop-color:#00FF00;stop-opacity:0.4"/>
            <stop offset="100%" style="stop-color:#00FF00;stop-opacity:0"/>
        </linearGradient>
    </defs>

    <!-- Background -->
    <rect width="100%" height="100%" fill="black"/>

    <!-- Main circle with glow -->
    <circle cx="250" cy="250" r="200" stroke="#00FF00" stroke-width="4" fill="none" filter="url(#glow)"/>

    <!-- Wedges with glow -->
    <line x1="250" y1="50" x2="250" y2="450" stroke="#00FF00" stroke-width="2" filter="url(#glow)"/>
    <line x1="50" y1="250" x2="450" y2="250" stroke="#00FF00" stroke-width="2" filter="url(#glow)"/>
    <line x1="100" y1="100" x2="400" y2="400" stroke="#00FF00" stroke-width="2" filter="url(#glow)"/>
    <line x1="100" y1="400" x2="400" y2="100" stroke="#00FF00" stroke-width="2" filter="url(#glow)"/>

    <!-- Circles for grid with subtle glow -->
    <circle cx="250" cy="250" r="50" stroke="#00FF00" stroke-width="1" fill="none" opacity="0.5" filter="url(#glow)"/>
    <circle cx="250" cy="250" r="100" stroke="#00FF00" stroke-width="1" fill="none" opacity="0.5" filter="url(#glow)"/>
    <circle cx="250" cy="250" r="150" stroke="#00FF00" stroke-width="1" fill="none" opacity="0.5" filter="url(#glow)"/>

    <!-- Radar sweep with trailing sector -->
    <g>
        <!-- Sweep sector (60 degree triangle) -->
        <path d="M250,250 L250,50 A30,30 0 0 1 290,65 Z" fill="url(#sweepGradient)">
            <animateTransform attributeName="transform"
                          type="rotate"
                          from="0 250 250"
                          to="360 250 250"
                          dur="4s"
                          repeatCount="indefinite"/>
        </path>
        <!-- Main sweep line -->
        <line x1="250" y1="250" x2="250" y2="50" stroke="#00FF00" stroke-width="3" filter="url(#glow)">
            <animateTransform attributeName="transform"
                          type="rotate"
                          from="0 250 250"
                          to="360 250 250"
                          dur="4s"
                          repeatCount="indefinite"/>
        </line>
    </g>
</svg>`;
    }

    static getUnknownSVG() {
        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 41">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="0.3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <g fill="none" stroke="#22D3EE" stroke-width="0.8" filter="url(#glow)">
    <!-- Base outline -->
    <rect x="10" y="8" width="40" height="25" rx="2" opacity="0.4"/>

    <!-- Question mark -->
    <path d="M25 28h2v2h-2zM31 16c0-3-2.5-5-5.5-5S20 13 20 16h2c0-2 1.5-3 3.5-3s3.5 1 3.5 3c0 1-1 2-2.5 3-2 1.5-2.5 2.5-2.5 4h2c0-1 .5-2 2-3 2-1.5 3-2.5 3-4z"
          opacity="0.8"/>

    <!-- Corner brackets -->
    <path d="M2 2 h6 M2 2 v6" stroke-width="1"/>
    <path d="M58 2 h-6 M58 2 v6" stroke-width="1"/>
    <path d="M2 39 h6 M2 39 v-6" stroke-width="1"/>
    <path d="M58 39 h-6 M58 39 v-6" stroke-width="1"/>
  </g>
</svg>`;
    }

static updateDeviceIcon(deviceInfo) {
    const iconContainer = document.querySelector('.device-icon-container');
    if (!iconContainer) return;

    let svgContent;

    if (!deviceInfo) {
        svgContent = this.getUnknownSVG();
    } else if (deviceInfo === 'discovering') {
        svgContent = this.getDiscoveringSVG();
    } else {
        const model = (deviceInfo.model || '').toLowerCase();
        const osVersion = (deviceInfo.os_version || '').toLowerCase();

        // Check for Linux systems first
        if (
            model.includes('linux') ||
            osVersion.includes('ubuntu') ||
            osVersion.includes('debian') ||
            osVersion.includes('centos') ||
            osVersion.includes('fedora') ||
            osVersion.includes('redhat') ||
            model.includes('generic')
        ) {
            svgContent = this.getLinuxSVG();
        } else {
            // Check for specific router keywords
            const routerKeywords = [
                'isr',        // Cisco ISR
                'asr',        // Cisco ASR
                'mx',         // Juniper MX
                'acx',        // Juniper ACX
                'router',     // Generic router
                '2951',       // Cisco 2951
                '7200',       // Cisco 7200
                '7204',
                '7206',
                '7206VXR',
                '7300',       // Cisco 7300
                '4321',       // ISR 4321
                '4331',       // ISR 4331
                '4351',       // ISR 4351
                '4431',       // ISR 4431
                '4451',       // ISR 4451
                '1100',       // ISR 1100
                'c8000',      // Cisco 8000
                'asr1000',    // ASR 1000
                'asr9000',    // ASR 9000
                'ncs',        // Cisco NCS
                'csr1000v'    // Cloud Services Router
            ];
            // Use Array.some() to check if any router keyword is present
            const isRouter = routerKeywords.some(keyword => model.includes(keyword));
            if (isRouter) {
                svgContent = this.getRouterSVG();
            } else {
                // Default to switch SVG for all other devices
                svgContent = this.getSwitchSVG();
            }
        }
    }

    iconContainer.innerHTML = svgContent;
    this.applyThemeColor();
}
    static applyThemeColor() {
        const style = getComputedStyle(document.documentElement);
        const themeColor = style.getPropertyValue('--border-color').trim() || '#22D3EE';

        document.querySelectorAll('.device-icon-container svg g').forEach(g => {
            g.setAttribute('stroke', themeColor);
        });
    }
}