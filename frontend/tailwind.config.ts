import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        text: "var(--main)",
        colorForMain: "var(--tw-content)",
      },
      fontSize: {
        'clamp-sm': 'clamp(0.875rem, 1.5vw, 1rem)',
        'clamp-base': 'clamp(1rem, 2vw, 1.25rem)',
        'clamp-lg': 'clamp(1.25rem, 3vw, 1.5rem)',
      }
    },
  },
  plugins: [],
};
export default config;
