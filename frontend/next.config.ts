import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    domains: [
      'i.ebayimg.com',  // Allow eBay image domains
      'thumbs.ebaystatic.com',  // Additional eBay image domain
      'i.ibb.co'  // Allow image hosting sites if needed
    ],
    formats: ['image/avif', 'image/webp'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.ebayimg.com',
        port: '',
        pathname: '/**'
      }
    ]
  }
};

export default nextConfig;
