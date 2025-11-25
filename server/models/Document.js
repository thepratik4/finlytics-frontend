import mongoose from 'mongoose';

const documentSchema = new mongoose.Schema({
    filename: {
        type: String,
        required: true,
    },
    fileSize: {
        type: Number,
        required: true,
    },
    uploadDate: {
        type: Date,
        default: Date.now,
    },
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
    },
    gridfsId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
    },
    status: {
        type: String,
        enum: ['uploaded', 'analyzed', 'pending'],
        default: 'uploaded',
    },
    analysisResult: {
        type: Object, // Store the JSON analysis result here
        default: null
    }
});

export default mongoose.model('Document', documentSchema);
