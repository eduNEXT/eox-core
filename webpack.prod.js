const merge = require('webpack-merge');
var webpack = require('webpack');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  devtool: false,
  watch: false,
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production'),
    }),
  ],
});
