const webpack = require("webpack");
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = [
  {
    mode: "development",
    // mode: "production",
    entry: {
      "index": './src/js/index.js',
    },
    plugins: [
      new webpack.ProvidePlugin({
        THREE: 'three'
      }),
      new HtmlWebpackPlugin({
        title: 'ARCity',
        // favicon: "./resources/favicon512.png",
        // template: "index.html",
        filename: "index.html",
        chunks: ['index']
      }),
    ],
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: '[name]-bundle.js',
      clean: true,
    },
    devServer: {
      static: {
        directory: '.'
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
