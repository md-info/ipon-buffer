import { defineConfig } from 'vite';
export default defineConfig({build:{outDir:'dist-nearby',lib:{entry:'src/nearby/sdk.tsx',name:'IponNearby',formats:['es'],fileName:'ipon-nearby'},rollupOptions:{external:['react','react-dom/client','react/jsx-runtime']}}});
