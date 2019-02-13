const path = require('path');

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
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    watch: true,
    watchOptions: {
        ignored: ['*.js', 'node_modules']
    },
    resolve: {
        extensions: ['.js', '.jsx', '.json']
    }
}
