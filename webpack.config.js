const webpack = require("webpack");
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

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
      new HtmlWebpackPlugin({
        title: 'ARCity Projector',
        favicon: "./resources/favicon.ico",
        filename: "projector.html",
        chunks: ['projector']
      }),
      new HtmlWebpackPlugin({
        favicon: "./resources/favicon.ico",
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
          test: /\.(json|json5|png|svg|jpg|jpeg|gif|mp3|stl|glb)$/i,
          type: 'asset/resource',
          use: ["file-loader?name=[name].[ext]"]
        },
      ],
    },
  },
];
