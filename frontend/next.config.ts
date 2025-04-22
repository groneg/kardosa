import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    domains: [
      'i.ebayimg.com',
      'thumbs.ebaystatic.com',
      'i.ibb.co',
      'localhost'
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.ebayimg.com',
        port: '',
        pathname: '/**'
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5000',
        pathname: '/**'
      }
    ],
    unoptimized: true
  }
};

export default nextConfig;
