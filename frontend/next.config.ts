import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental:{
    disableOptimizedLoading: true,
    serverActions:{
      bodySizeLimit: '10mb'
    }
  }
};

export default nextConfig;
