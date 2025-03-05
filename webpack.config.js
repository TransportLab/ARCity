const webpack = require("webpack");
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = [
  {
    mode: "development",
    // mode: "production",
    entry: {
      "projector": './src/js/projector.js',
      "GUI": './src/js/GUI.js',
    },
    plugins: [
      new webpack.ProvidePlugin({
        THREE: 'three'
      }),
      new CopyWebpackPlugin({
        patterns: [
          { from: path.resolve(__dirname, 'assets'), to: 'assets' }
        ],
      }),
      new HtmlWebpackPlugin({
        title: 'ARCity Projector',
        favicon: "assets/favicon.ico",
        filename: "projector.html",
        chunks: ['projector']
      }),
      new HtmlWebpackPlugin({
        favicon: "assets/favicon.ico",
        template: "./src/html/GUI.html",
        filename: "GUI.html",
        chunks: ['GUI']
      }),
    ],
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: '[name]-bundle.js',
      clean: true,
    },
    devServer: {
      static: {
        directory: './dist/'
      },
    },
    module: {
      rules: [
        {
          test: /\.css$/i,
          use: ["style-loader", "css-loader"],
        },
        {
          test: /\.(json|json5|png|svg|jpg|jpeg|gif|mp3|stl|glb|gltf)$/i,
          type: 'asset/resource',
          use: ["file-loader?name=[name].[ext]"]
        },
      ],
    },
  },
];
