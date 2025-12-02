const webpack = require("webpack");

module.exports = function override(config, env) {
  // Ensure resolve object exists
  config.resolve = config.resolve || {};

  // Merge fallback into existing resolve
  config.resolve.fallback = {
    ...(config.resolve.fallback || {}),
    crypto: require.resolve("crypto-browserify"),
    stream: require.resolve("stream-browserify"),
    buffer: require.resolve("buffer/"),
    util: require.resolve("util/"),
  };

  // Provide globals
  config.plugins = (config.plugins || []).concat([
    new webpack.ProvidePlugin({
      Buffer: ["buffer", "Buffer"],
    }),
  ]);

  return config;
};
