const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  devtool: 'inline-source-map',
  watch: true,
  watchOptions: {
    ignored: ['*.js', 'node_modules'],
  },
});
