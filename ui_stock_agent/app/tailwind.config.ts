import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#e8ecf4",
        abyss: "#09111f",
        mist: "#90a0ba",
        tide: "#10233f",
        edge: "#20385f",
        flare: "#5ef2c7",
        ember: "#ff9157",
        sun: "#f6d66b",
      },
      boxShadow: {
        panel: "0 18px 60px rgba(3, 10, 24, 0.28)",
      },
      backgroundImage: {
        hero:
          "radial-gradient(circle at top left, rgba(94,242,199,0.16), transparent 28%), radial-gradient(circle at top right, rgba(246,214,107,0.12), transparent 22%), linear-gradient(180deg, rgba(9,17,31,0.98), rgba(6,12,24,1))",
      },
    },
  },
  plugins: [],
};

export default config;
