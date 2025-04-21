/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'i.ebayimg.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'ebayimg.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '**.ebayimg.com',
        pathname: '/**',
      }
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://kardosa-api.onrender.com'
  }
};

module.exports = nextConfig;
