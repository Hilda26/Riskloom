import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    // wagmi/RainbowKit pull in optional dependencies that don't apply to a
    // browser build (React Native storage, Node-only pretty-printing for
    // WalletConnect's logger) - silence the resulting "module not found"
    // noise rather than installing dead weight.
    config.resolve.fallback = {
      ...config.resolve.fallback,
      "@react-native-async-storage/async-storage": false,
      "pino-pretty": false,
    };
    return config;
  },
};

export default nextConfig;
