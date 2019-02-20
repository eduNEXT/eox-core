const path = require('path');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
    entry: path.join(__dirname, '/eox_core/cms/static/js/index.jsx'),
    output: {
        filename: 'build.js',
        path: path.join(__dirname, '/eox_core/static/js'),
        libraryTarget: 'window'
    },
    module: {
        rules:[
            {
                test: /\.jsx$/,
                exclude: /node_modules/,
                loader: 'babel-loader'
            },
            {
                test: /\.scss$/,
                loader: ExtractTextPlugin.extract({
                    fallback: 'style-loader',
                    use: [
                        {
                            loader: 'css-loader'
                        },
                        {
                            loader: 'sass-loader',
                            options: {
                                includePaths: [
                                    path.join(__dirname, './node_modules')
                                ]
                            }
                        }
                    ]
                })
            }
        ]
    },
    watch: true,
    watchOptions: {
        ignored: ['*.js', 'node_modules']
    },
    resolve: {
        extensions: ['.js', '.jsx', '.json', '.scss']
    },
    plugins: [
        new ExtractTextPlugin({
            filename: '../css/course-management.bundle.css'
        })
    ]
}
