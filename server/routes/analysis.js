import express from 'express';
import Document from '../models/Document.js';
import jwt from 'jsonwebtoken';

const router = express.Router();

// Middleware to verify token
const auth = (req, res, next) => {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    if (!token) return res.status(401).json({ message: 'No token, authorization denied' });

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded.user;
        next();
    } catch (err) {
        res.status(401).json({ message: 'Token is not valid' });
    }
};

router.post('/analyze', auth, async (req, res) => {
    try {
        const { filenames } = req.body;

        // Mock Analysis Logic (similar to previous mock)
        // In a real app, this would process the files from GridFS

        const individual_analysis = {};
        const sentiment_analysis = {};
        let totalPolarity = 0;

        for (const filename of filenames) {
            individual_analysis[filename] = `
### Executive Summary
Analysis of **${filename}** indicates a strong financial position with a **15% increase** in YoY revenue. Operating margins have improved due to cost-cutting measures implemented in Q3.

### Key Metrics
* **Revenue**: $4.5M (+15%)
* **Net Income**: $1.2M (+8%)
* **EBITDA**: $1.8M

### Risk Factors
While growth is strong, the report highlights potential supply chain disruptions affecting Q4 projections. Cash flow from operations remains positive but capital expenditures have increased significantly.
            `;

            const polarity = (Math.random() * 2) - 1; // -1 to 1
            totalPolarity += polarity;

            sentiment_analysis[filename] = {
                polarity: polarity,
                subjectivity: Math.random(),
                sentiment: polarity > 0.1 ? 'Positive' : polarity < -0.1 ? 'Negative' : 'Neutral',
                positive_signals: ['Revenue growth', 'Margin expansion', 'Strong cash flow'],
                negative_signals: ['Supply chain risks', 'Rising CAPEX'],
                interpretation: polarity > 0 ? "The document conveys optimism regarding future growth." : "The document expresses caution regarding market conditions."
            };

            // Update Document status in DB
            await Document.findOneAndUpdate(
                { filename: filename, user: req.user.id },
                {
                    status: 'analyzed',
                    analysisResult: {
                        individual: individual_analysis[filename],
                        sentiment: sentiment_analysis[filename]
                    }
                }
            );
        }

        res.json({
            analysis: {
                individual_analysis,
                sentiment_analysis,
                overall_sentiment: {
                    average_polarity: totalPolarity / filenames.length,
                    average_subjectivity: 0.5,
                    total_positive: filenames.length * 3,
                    total_negative: filenames.length * 2,
                    summary: `Overall, the ${filenames.length} analyzed documents show a ${totalPolarity > 0 ? 'positive' : 'mixed'} trend. Revenue growth is consistent across entities, though risk factors regarding supply chains are a common theme.`
                }
            },
            status: 200
        });

    } catch (err) {
        console.error(err);
        res.status(500).json({ message: 'Server Error' });
    }
});

export default router;
