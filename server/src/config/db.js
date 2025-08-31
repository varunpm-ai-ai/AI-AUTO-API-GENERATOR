const mongoose = require('mongoose')

let isConnected = false;

const connectdb = async (MONGODB_URI) => {
    if (isConnected) return;
    mongoose.set('strictQuery', true);

    uri = process.env.MONGODB_URI

    const Options = {
        autoIndex: true,
        serverSelectionTimeoutMS: 10000,
    }

    await mongoose.connect(uri, Options)
        .catch(err => console.log(err));

    isConnected = true;
    console.log("MongoDB Connected");
}

module.exports = connectdb;