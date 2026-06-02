/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  safelist: [
  {
      pattern:
        /^bg-(red|green|yellow|emerald|amber|rose|orange|slate|violet|indigo|cyan|blue)-(50|100|200|300|400|500|600|700|800|900|950)$/,
    },
    {
      pattern:
        /^text-(red|green|yellow|emerald|amber|rose|orange|slate|violet|indigo|cyan|blue)-(50|100|200|300|400|500|600|700|800|900|950)$/,
    },
    {
      pattern:
        /^border-(red|green|yellow|emerald|amber|rose|orange|slate|violet|indigo|cyan|blue)-(50|100|200|300|400|500|600|700|800|900|950)$/,
    },
    {
      pattern:
        /^ring-(red|green|yellow|emerald|amber|rose|orange|slate|violet|indigo|cyan|blue)-(50|100|200|300|400|500|600|700|800|900|950)$/,
    },
    'animate-pulse',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'ui-sans-serif',
          'system-ui',
          'sans-serif',
          'Apple Color Emoji',
          'Segoe UI Emoji',
        ],
        mono: [
          'ui-monospace',
          'SFMono-Regular',
          'Menlo',
          'Monaco',
          'Consolas',
          'Liberation Mono',
          'Courier New',
          'monospace',
        ],
      },
    },
  },
  plugins: [],
}
