/** @type {import('tailwindcss').Config} */

function withOpacity(variable) {
  return ({ opacityValue }) => {
    if (opacityValue !== undefined) {
      return `rgb(var(${variable}) / ${opacityValue})`;
    }
    return `rgb(var(${variable}))`;
  };
}

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Base surfaces
        "surface": withOpacity("--surface"),
        "surface-dim": withOpacity("--surface-dim"),
        "surface-bright": withOpacity("--surface-bright"),
        "surface-container-lowest": withOpacity("--surface-container-lowest"),
        "surface-container-low": withOpacity("--surface-container-low"),
        "surface-container": withOpacity("--surface-container"),
        "surface-container-high": withOpacity("--surface-container-high"),
        "surface-container-highest": withOpacity("--surface-container-highest"),
        "surface-variant": withOpacity("--surface-variant"),
        
        // Content on surfaces
        "on-surface": withOpacity("--on-surface"),
        "on-surface-variant": withOpacity("--on-surface-variant"),
        "inverse-surface": withOpacity("--inverse-surface"),
        "inverse-on-surface": withOpacity("--inverse-on-surface"),
        "on-background": withOpacity("--on-background"),
        "background": withOpacity("--background"),
        
        // Borders & Outlines
        "outline": withOpacity("--outline"),
        "outline-variant": withOpacity("--outline-variant"),
        "surface-tint": withOpacity("--surface-tint"),
        
        // Brand Primary & Fixed
        "primary": withOpacity("--primary"),
        "on-primary": withOpacity("--on-primary"),
        "primary-container": withOpacity("--primary-container"),
        "on-primary-container": withOpacity("--on-primary-container"),
        "inverse-primary": withOpacity("--inverse-primary"),
        "primary-fixed": withOpacity("--primary-fixed"),
        "primary-fixed-dim": withOpacity("--primary-fixed-dim"),
        "on-primary-fixed": withOpacity("--on-primary-fixed"),
        "on-primary-fixed-variant": withOpacity("--on-primary-fixed-variant"),
        
        // Telemetry Secondary (Cyan/Sky)
        "secondary": withOpacity("--secondary"),
        "on-secondary": withOpacity("--on-secondary"),
        "secondary-container": withOpacity("--secondary-container"),
        "on-secondary-container": withOpacity("--on-secondary-container"),
        "secondary-fixed": withOpacity("--secondary-fixed"),
        "secondary-fixed-dim": withOpacity("--secondary-fixed-dim"),
        "on-secondary-fixed": withOpacity("--on-secondary-fixed"),
        "on-secondary-fixed-variant": withOpacity("--on-secondary-fixed-variant"),
        
        // Telemetry Tertiary (Emerald Valid)
        "tertiary": withOpacity("--tertiary"),
        "on-tertiary": withOpacity("--on-tertiary"),
        "tertiary-container": withOpacity("--tertiary-container"),
        "on-tertiary-container": withOpacity("--on-tertiary-container"),
        "tertiary-fixed": withOpacity("--tertiary-fixed"),
        "tertiary-fixed-dim": withOpacity("--tertiary-fixed-dim"),
        "on-tertiary-fixed": withOpacity("--on-tertiary-fixed"),
        "on-tertiary-fixed-variant": withOpacity("--on-tertiary-fixed-variant"),
        
        // Status & Errors (Crimson Anomaly)
        "error": withOpacity("--error"),
        "on-error": withOpacity("--on-error"),
        "error-container": withOpacity("--error-container"),
        "on-error-container": withOpacity("--on-error-container"),
        "anomaly": withOpacity("--anomaly"),
        "warning": withOpacity("--warning"),
      },
      borderRadius: {
        "none": "0px",
        "DEFAULT": "0px",
        "sm": "0px",
        "md": "0px",
        "lg": "0px",
        "xl": "0px",
        "2xl": "0px",
        "full": "9999px",
      },
      spacing: {
        "space-0": "0px",
        "space-1": "0.25rem",
        "space-2": "0.5rem",
        "space-3": "0.75rem",
        "space-4": "1rem",
        "space-5": "1.25rem",
        "space-6": "1.5rem",
        "space-8": "2rem",
        "space-12": "3rem",
        "gutter": "1px",
        "dock-padding": "0.5rem",
        "panel-padding-compact": "0.75rem",
        "panel-padding-relaxed": "1rem",
      },
      fontFamily: {
        "display-lg": ["Space Grotesk", "sans-serif"],
        "display-lg-mobile": ["Space Grotesk", "sans-serif"],
        "headline-lg": ["Space Grotesk", "sans-serif"],
        "headline-md": ["Space Grotesk", "sans-serif"],
        "headline-sm": ["Space Grotesk", "sans-serif"],
        "label-caps": ["Space Grotesk", "sans-serif"],
        "body-lg": ["Geist", "sans-serif"],
        "body-md": ["Geist", "sans-serif"],
        "body-sm": ["Geist", "sans-serif"],
        "data-mono": ["Geist", "monospace"],
      },
      fontSize: {
        "display-lg": ["2.25rem", { lineHeight: "2.5rem", letterSpacing: "-0.03em", fontWeight: "700" }],
        "display-lg-mobile": ["1.75rem", { lineHeight: "2rem", letterSpacing: "-0.02em", fontWeight: "700" }],
        "headline-lg": ["1.5rem", { lineHeight: "1.75rem", letterSpacing: "-0.02em", fontWeight: "600" }],
        "headline-md": ["1.25rem", { lineHeight: "1.5rem", letterSpacing: "-0.01em", fontWeight: "600" }],
        "headline-sm": ["1rem", { lineHeight: "1.25rem", letterSpacing: "0em", fontWeight: "500" }],
        "label-caps": ["0.6875rem", { lineHeight: "0.875rem", letterSpacing: "0.08em", fontWeight: "700" }],
        "body-lg": ["0.9375rem", { lineHeight: "1.375rem", letterSpacing: "-0.01em", fontWeight: "400" }],
        "body-md": ["0.875rem", { lineHeight: "1.25rem", letterSpacing: "0em", fontWeight: "400" }],
        "body-sm": ["0.75rem", { lineHeight: "1rem", letterSpacing: "0.01em", fontWeight: "400" }],
        "data-mono": ["0.8125rem", { lineHeight: "1rem", letterSpacing: "0.02em", fontWeight: "500" }],
      },
    },
  },
  plugins: [],
}
