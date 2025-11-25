import mongoose from 'mongoose';
import dotenv from 'dotenv';

dotenv.config();

const uri = process.env.MONGO_URI || 'mongodb://localhost:27017/finlytics';

console.log('Testing connection to:', uri);

mongoose.connect(uri)
    .then(() => {
        console.log('MongoDB Connection Successful!');
        process.exit(0);
    })
    .catch(err => {
        console.error('MongoDB Connection Failed:', err.message);
        process.exit(1);
    });
