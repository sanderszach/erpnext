const HtmlWebpackPlugin = require('html-webpack-plugin');
const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');
const path = require('path');

module.exports = {
  entry: './src/index',
  mode: 'development',
  devServer: {
    static: path.join(__dirname, 'dist'),
    port: 3005,
    historyApiFallback: true,
    client: {
      overlay: false,
    },
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
      "Access-Control-Allow-Headers": "X-Requested-With, content-type, Authorization",
    },
  },
  output: {
    publicPath: 'http://localhost:3005/',
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
    modules: [path.resolve(__dirname, 'node_modules'), 'node_modules'],
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx|js|jsx)$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        options: {
          presets: [
            '@babel/preset-env',
            '@babel/preset-react',
            '@babel/preset-typescript',
          ],
        },
      },
      {
        test: /\.css$/i,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'chat_ui',
      library: { type: 'var', name: 'chat_ui' },
      filename: 'remoteEntry.js',
      exposes: {
        './Chat': './src/components/Chat',
        './render': './src/render',
      },
      shared: {
        react: { 
          singleton: true, 
          requiredVersion: '^18.2.0', 
          eager: true, // Bundle React to avoid conflicts with CDN version
        },
        'react-dom': { 
          singleton: true, 
          requiredVersion: '^18.2.0', 
          eager: true, // Bundle ReactDOM to avoid conflicts with CDN version
        },
        '@chakra-ui/react': { 
          singleton: true, 
          eager: true, // Bundle Chakra UI since host doesn't have it
        },
        '@emotion/react': { 
          singleton: true, 
          eager: true, // Bundle Emotion since host doesn't have it
        },
        '@emotion/styled': { 
          singleton: true, 
          eager: true, // Bundle Emotion styled since host doesn't have it
        },
      },
    }),
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
};

