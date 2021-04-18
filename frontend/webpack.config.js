const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    mode: 'development',
    output: {
        filename: 'bundle.js',
        library: 'cwg'
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'style.css'
        }),
    ],
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader'
                ]
            }
        ]
    }
}